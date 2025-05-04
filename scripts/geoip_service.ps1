# Install as a Windows Service:
# 1. Open PowerShell as Administrator
# 2. Run: New-Service -Name "GeoIPUpdater" -BinaryPathName "powershell.exe -ExecutionPolicy Bypass -File <path_to_this_script>"

$ErrorActionPreference = "Stop"

# Get the script directory
$scriptPath = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Activate virtual environment and start the updater
try {
    Set-Location $scriptPath
    Set-Location "..\backend"
    .\venv\Scripts\Activate.ps1
    python update_geoip.py --schedule
} catch {
    Write-Error "Error running GeoIP updater: $_"
    exit 1
}
