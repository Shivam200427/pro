import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='BU@@2024',
        database='auth_analytics_db'
    )

    cursor = connection.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS login_attempt")
    cursor.execute("DROP TABLE IF EXISTS user")
    
    # Create user table with larger password field
    cursor.execute("""
    CREATE TABLE user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,        email VARCHAR(120) UNIQUE NOT NULL,
        password LONGTEXT NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME
    )
    """)
    
    # Create login_attempt table
    cursor.execute("""
    CREATE TABLE login_attempt (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        ip_address VARCHAR(45) NOT NULL,
        location VARCHAR(200),
        device_info VARCHAR(200),
        browser_info VARCHAR(200),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        success BOOLEAN DEFAULT FALSE,
        latitude DECIMAL(10, 8),
        longitude DECIMAL(11, 8),
        accuracy_radius INT,
        city VARCHAR(100),
        country VARCHAR(100),
        timezone VARCHAR(50),
        isp VARCHAR(100),
        connection_type VARCHAR(50),
        FOREIGN KEY (user_id) REFERENCES user(id)
    )
    """)
    
    connection.commit()
    print("Tables recreated successfully!")

except Error as e:
    print(f"Error: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection closed.")
