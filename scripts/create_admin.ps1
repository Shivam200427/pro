Write-Host "Creating first admin user..." -ForegroundColor Green

# Navigate to backend directory
Set-Location -Path "backend"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the create_admin script
python create_admin.py

# Deactivate virtual environment
deactivate

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "You can now login to the admin dashboard at http://localhost:3000/admin"
