import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Database configuration with URL-encoded password
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:BU%40%402024@localhost/auth_analytics_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

def create_admin():
    print("Creating first admin user...")
    try:
        # Create tables if they don't exist
        db.create_all()
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email="shivamjain@gmail.com").first()
        if existing_admin:
            print("Admin user already exists!")
            return

        # Create new admin user with pbkdf2:sha256 hashing
        admin = User(
            username="shivamjain",
            email="shivamjain@gmail.com",
            password=generate_password_hash("Shivam@2004", method='pbkdf2:sha256'),
            is_admin=True
        )
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print("Admin credentials:")
        print("Username: shivamjain")
        print("Email: shivamjain@gmail.com")
        print("Password: Shivam@2004")
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    with app.app_context():
        create_admin()
