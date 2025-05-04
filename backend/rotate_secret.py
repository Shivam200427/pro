import os
import schedule
import time
import secrets
import string
from dotenv import load_dotenv
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_secret_key(length=64):
    """Generate a cryptographically secure secret key."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def update_secret_key():
    try:
        # Generate new secret key
        new_secret = generate_secret_key()
        
        # Get the absolute path to .env file
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))
        logger.info(f'Updating secret key in: {env_path}')
        
        # Read all lines from the file
        with open(env_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Flag to check if we found and updated the SECRET_KEY
        updated = False
        
        # Update the SECRET_KEY line
        for i, line in enumerate(lines):
            if line.strip().startswith('SECRET_KEY='):
                lines[i] = f'SECRET_KEY={new_secret}\n'
                updated = True
                break
        
        # If SECRET_KEY wasn't found, append it
        if not updated:
            lines.append(f'SECRET_KEY={new_secret}\n')
        
        # Write back to env file
        with open(env_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
            
        logger.info(f'Successfully updated secret key to: {new_secret}')
        
        logger.info(f'Secret key rotated successfully at {datetime.now()}')
    except Exception as e:
        logger.error(f'Error rotating secret key: {str(e)}')

def main():
    logger.info('Starting secret key rotation service...')
    
    # Schedule the job to run every 3 minutes
    schedule.every(3).minutes.do(update_secret_key)
    
    # Run immediately on start
    update_secret_key()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
