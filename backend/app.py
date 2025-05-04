from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import jwt
import requests
import geoip2.database
import geoip2.errors
import os.path
from functools import wraps
from geolocation_service import GeolocationService
import logging

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize geolocation service
geo_service = GeolocationService()

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    location = db.Column(db.String(200))
    device_info = db.Column(db.String(200))
    browser_info = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float(precision=10))
    longitude = db.Column(db.Float(precision=10))
    accuracy_radius = db.Column(db.Integer)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    timezone = db.Column(db.String(50))
    isp = db.Column(db.String(200))
    connection_type = db.Column(db.String(50))

# Routes
def download_geoip_database():
    """Download the GeoLite2 City database if it doesn't exist."""
    db_path = os.getenv('GEOIP_DB_PATH')
    if not os.path.exists(db_path):
        license_key = os.getenv('MAXMIND_LICENSE_KEY')
        if not license_key:
            raise ValueError("MAXMIND_LICENSE_KEY not set in environment")
            
        url = f"https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key={license_key}&suffix=tar.gz"
        response = requests.get(url)
        
        if response.status_code == 200:
            with open(f"{db_path}.tar.gz", 'wb') as f:
                f.write(response.content)
            
            import tarfile
            with tarfile.open(f"{db_path}.tar.gz", 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.name.endswith('.mmdb'):
                        member.name = os.path.basename(member.name)
                        tar.extract(member, '.')
            
            os.remove(f"{db_path}.tar.gz")
        else:
            raise Exception(f"Failed to download GeoIP database: {response.status_code}")

def get_location_from_ip(ip_address):
    """Get location information using MaxMind GeoLite2 database."""
    if ip_address in ('127.0.0.1', 'localhost', '::1'):
        return {
            'city': 'Local',
            'country': 'Local',
            'latitude': 0.0,  # Default to a valid coordinate for local access
            'longitude': 0.0,
            'accuracy_radius': 0,
            'timezone': 'UTC'
        }

    try:
        db_path = os.getenv('GEOIP_DB_PATH')
        if not os.path.exists(db_path):
            download_geoip_database()
            
        with geoip2.database.Reader(db_path) as reader:
            response = reader.city(ip_address)
            return {
                'city': response.city.name or 'Unknown City',
                'country': response.country.name or 'Unknown Country',
                'latitude': float(response.location.latitude) if response.location.latitude else 0.0,
                'longitude': float(response.location.longitude) if response.location.longitude else 0.0,
                'accuracy_radius': response.location.accuracy_radius,
                'timezone': str(response.location.time_zone)
            }
    except (geoip2.errors.AddressNotFoundError, FileNotFoundError, ValueError) as e:
        print(f"Error getting location for IP {ip_address}: {str(e)}")
        return {
            'city': 'Unknown',
            'country': 'Unknown',
            'latitude': 0.0,  # Default to valid coordinates
            'longitude': 0.0,
            'accuracy_radius': 0,
            'timezone': 'UTC'
        }
    except Exception as e:
        print(f"Unexpected error getting location for IP {ip_address}: {str(e)}")
        return {
            'city': 'Error',
            'country': 'Error',
            'latitude': 0.0,
            'longitude': 0.0,
            'accuracy_radius': 0,
            'timezone': 'UTC'
        }

# Secret key management
def get_current_secret_key():
    """Get the current secret key from environment."""
    load_dotenv()  # Reload environment variables
    return os.getenv('SECRET_KEY')

def create_token(user_id):
    """Create a new JWT token with current secret key."""
    secret_key = get_current_secret_key()
    return jwt.encode(
        {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=24)},
        secret_key,
        algorithm='HS256'
    )

def verify_token(token):
    """Verify JWT token with current secret key."""
    try:
        secret_key = get_current_secret_key()
        return jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        # If invalid, try once more with reloaded secret key
        try:
            load_dotenv()
            secret_key = get_current_secret_key()
            return jwt.decode(token, secret_key, algorithms=['HS256'])
        except:
            return None

# Update token verification decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is missing!'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = verify_token(token)
            if not data:
                return jsonify({'message': 'Token is invalid!'}), 401
            
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
                
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is missing!'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = verify_token(token)
            if not data:
                return jsonify({'message': 'Token is invalid!'}), 401
            
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
            
            if not current_user.is_admin:
                return jsonify({'message': 'Admin privileges required!'}), 403

        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# Admin routes
@app.route('/api/admin/create', methods=['POST'])
@admin_required
def create_admin():
    data = request.json
    
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'message': 'Missing required fields'}), 400
        
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
        
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_admin = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        is_admin=True
    )
    
    db.session.add(new_admin)
    db.session.commit()
    
    return jsonify({'message': 'Admin user created successfully'}), 201

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        } for user in users]
    })

# Update analytics endpoint to require admin access
@app.route('/api/auth/analytics', methods=['GET'])
@admin_required
def get_analytics():
    try:
        # Verify JWT token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'message': 'Missing token'}), 401
        
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        # Get all login attempts
        total_attempts = LoginAttempt.query.count()
        successful_attempts = LoginAttempt.query.filter_by(success=True).count()
        failed_attempts = total_attempts - successful_attempts

        # Get recent attempts with coordinates
        recent_attempts = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).limit(10).all()
        
        # Get hourly statistics for the last 24 hours
        now = datetime.utcnow()
        hourly_attempts = []
        
        for hour in range(24):
            start_time = now - timedelta(hours=hour+1)
            end_time = now - timedelta(hours=hour)
            
            hourly_data = {
                'hour': start_time.strftime('%H:00'),
                'successful': LoginAttempt.query.filter(
                    LoginAttempt.timestamp.between(start_time, end_time),
                    LoginAttempt.success == True
                ).count(),
                'failed': LoginAttempt.query.filter(
                    LoginAttempt.timestamp.between(start_time, end_time),
                    LoginAttempt.success == False
                ).count()
            }
            hourly_attempts.append(hourly_data)

        return jsonify({
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'failed_attempts': failed_attempts,
            'recent_attempts': [{
                'ip_address': attempt.ip_address,
                'timestamp': attempt.timestamp.isoformat(),
                'success': attempt.success,
                'location': attempt.location,
                'device_info': attempt.device_info,
                'latitude': float(attempt.latitude) if attempt.latitude else None,
                'longitude': float(attempt.longitude) if attempt.longitude else None
            } for attempt in recent_attempts],
            'hourly_attempts': hourly_attempts
        })
    except Exception as e:
        return jsonify({'message': 'Error fetching analytics data'}), 500

# Vercel serverless function handler
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    # Only run the app directly when in development
    app.run(host='0.0.0.0', port=5000)
