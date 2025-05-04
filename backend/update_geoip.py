import os
import sys
import requests
import tarfile
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def download_geoip_database():
    """Download the GeoLite2 City database."""
    license_key = os.getenv('MAXMIND_LICENSE_KEY')
    db_path = os.getenv('GEOIP_DB_PATH', 'GeoLite2-City.mmdb')
    
    if not license_key:
        print("Error: MAXMIND_LICENSE_KEY not set in environment")
        sys.exit(1)

    url = f"https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key={license_key}&suffix=tar.gz"
    
    try:
        print(f"{datetime.now()}: Downloading GeoLite2 City database...")
        response = requests.get(url)
        
        if response.status_code == 200:
            # Save the tar.gz file
            with open('GeoLite2-City.tar.gz', 'wb') as f:
                f.write(response.content)
            
            # Extract the database file
            with tarfile.open('GeoLite2-City.tar.gz', 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.name.endswith('.mmdb'):
                        # Rename the file while extracting
                        member.name = db_path
                        tar.extract(member)
            
            # Clean up
            os.remove('GeoLite2-City.tar.gz')
            print(f"{datetime.now()}: Successfully updated GeoLite2 City database")
            return True
        else:
            print(f"Error downloading database: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def schedule_updates():
    """Schedule weekly database updates."""
    if download_geoip_database():
        print("Initial database download successful")
    else:
        print("Initial database download failed")
    
    # Schedule weekly updates
    schedule.every().wednesday.at("00:00").do(download_geoip_database)
    
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        schedule_updates()
    else:
        download_geoip_database()
