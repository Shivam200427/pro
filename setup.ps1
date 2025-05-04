$ErrorActionPreference = "Stop"

Write-Host "Setting up Enhanced User Authentication System..." -ForegroundColor Green

# Create and activate Python virtual environment
Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "backend\venv")) {
    Set-Location backend
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    
    # Install Python dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install flask flask-cors flask-sqlalchemy mysql-connector-python python-dotenv jwt requests geoip2 schedule
    
    # Download GeoIP database
    Write-Host "Downloading GeoIP database..." -ForegroundColor Yellow
    python update_geoip.py
    
    Set-Location ..
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
    
    # Update GeoIP database if needed
    Set-Location backend
    .\venv\Scripts\Activate.ps1
    python update_geoip.py
    Set-Location ..
}

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install

# Start both applications
Write-Host "Starting the application..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'backend'; .\venv\Scripts\Activate.ps1; flask run"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'frontend'; npm start"

Write-Host "Application is running!" -ForegroundColor Green
Write-Host "Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
