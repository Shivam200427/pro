# Start the secret rotation service
Write-Host "Starting secret key rotation service..." -ForegroundColor Green

# Navigate to backend directory and activate virtual environment
Set-Location -Path "$PSScriptRoot\..\backend"
.\venv\Scripts\Activate.ps1

# Run the secret rotation script
Write-Host "Running secret rotation script in background..."
Start-Process -NoNewWindow -FilePath ".\venv\Scripts\python.exe" -ArgumentList "rotate_secret.py"

Write-Host "Secret key rotation service is running in the background."
Write-Host "The secret key will be updated every 3 minutes."
