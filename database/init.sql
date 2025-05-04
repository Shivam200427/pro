-- Create the database
CREATE DATABASE IF NOT EXISTS auth_analytics_db;
USE auth_analytics_db;

-- Create users table
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Create login_attempt table
CREATE TABLE IF NOT EXISTS login_attempt (
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
    isp VARCHAR(200),
    connection_type VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES user(id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_ip_address (ip_address),
    INDEX idx_location (latitude, longitude)
);
