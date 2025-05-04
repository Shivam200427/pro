# Enhanced User Authentication System with Security Analytics

This application provides a secure user authentication system with advanced security analytics and visualization features.

## Features

- User registration and authentication
- JWT-based session management
- Security analytics dashboard
- Login attempt visualization
- Geolocation tracking
- Real-time activity monitoring
- Responsive modern UI

## Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- MySQL Server

## Setup Instructions

### Database Setup

1. Install MySQL and create a new database:
```sql
CREATE DATABASE auth_analytics_db;
```

2. Import the database schema:
```bash
mysql -u root -p auth_analytics_db < database/init.sql
```

### API Keys Setup

1. **MaxMind GeoLite2**:
   - Sign up for a MaxMind account at https://www.maxmind.com/en/geolite2/signup
   - Create a license key in your account
   - Download GeoLite2 City database

2. **Google Maps**:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Maps JavaScript API
   - Create API credentials (API key)
   - Add restrictions to your API key for security

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install flask flask-cors flask-sqlalchemy mysql-connector-python python-dotenv jwt requests geoip2
```

4. Configure the environment variables in `.env` file:
```
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=auth_analytics_db
SECRET_KEY=your_secret_key_here
MAXMIND_LICENSE_KEY=your_maxmind_license_key
GEOIP_DB_PATH=GeoLite2-City.mmdb
```

5. Run the Flask application:
```bash
flask run
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure the environment variables in `.env` file:
```
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

4. Start the development server:
```bash
npm start
```

5. Access the application at http://localhost:3000

### GeoIP Setup

1. Sign up for a MaxMind account and obtain a license key
2. Add your MaxMind license key to the backend `.env` file
3. The GeoIP database will be downloaded automatically during setup

Optional: Set up automatic GeoIP database updates
1. Open PowerShell as Administrator
2. Run the following command:
```powershell
New-Service -Name "GeoIPUpdater" -BinaryPathName "powershell.exe -ExecutionPolicy Bypass -File <path_to_repo>\scripts\geoip_service.ps1"
```
3. Start the service:
```powershell
Start-Service -Name "GeoIPUpdater"
```

The service will automatically download updates for the GeoIP database every Wednesday at midnight.

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Register a new account or login with existing credentials
3. View the security analytics dashboard at `/analytics`

## Security Features

- Password hashing using PBKDF2-SHA256
- JWT token-based authentication
- Geolocation tracking for login attempts
- Detailed user agent and device information logging
- Real-time monitoring of login attempts
- Visual analytics for security patterns

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register a new user
- POST `/api/auth/login` - Login user
- GET `/api/auth/analytics` - Get security analytics data

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
