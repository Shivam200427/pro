import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

def create_admin():
    print("Creating first admin user...")
    try:
        # Check if admin already exists
        existing_admin = User.query.filter_by(email="shivamjain@gmail.com").first()
        if existing_admin:
            print("Admin user already exists!")
            return

        # Create new admin user
        admin = User(
            username="shivamjain",
            email="shivamjain@gmail.com",
            password=generate_password_hash("Shivam@2004"),
            is_admin=True
        )
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.session.rollback()
    
    # Check if admin already exists
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        print("An admin user already exists!")
        return

    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password (min 8 characters): ")

    if len(password) < 8:
        print("Password must be at least 8 characters long!")
        return

    try:
        # Create admin user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        admin_user = User(
            username=username,
            email=email,
            password=hashed_password,
            is_admin=True
        )
        
        # Add to database
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"\nAdmin user created successfully!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print("\nYou can now login using these credentials.")
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        # Create admin user
        create_admin()
