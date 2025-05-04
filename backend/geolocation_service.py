import os
import geoip2.database
import geoip2.errors
import requests
import socket
import logging
from typing import Dict, Optional, Tuple
from user_agents import parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeolocationService:
    def __init__(self):
        self.db_path = os.getenv('GEOIP_DB_PATH', 'GeoLite2-City.mmdb')
        self.backup_ip_service = "http://ip-api.com/json/{}"
        self.cache = {}  # Simple in-memory cache

    def _is_valid_ip(self, ip_address: str) -> bool:
        """Validate IP address format."""
        try:
            socket.inet_aton(ip_address)
            return True
        except socket.error:
            return False

    def _get_from_maxmind(self, ip_address: str) -> Optional[Dict]:
        """Get location data from MaxMind database."""
        try:
            with geoip2.database.Reader(self.db_path) as reader:
                response = reader.city(ip_address)
                return {
                    'city': response.city.name or 'Unknown City',
                    'country': response.country.name or 'Unknown Country',
                    'latitude': float(response.location.latitude or 0.0),
                    'longitude': float(response.location.longitude or 0.0),
                    'accuracy_radius': response.location.accuracy_radius or 0,
                    'timezone': str(response.location.time_zone or 'UTC'),
                    'isp': '',  # MaxMind City database doesn't include ISP info
                    'connection_type': ''
                }
        except (geoip2.errors.AddressNotFoundError, FileNotFoundError) as e:
            logger.warning(f"MaxMind lookup failed for IP {ip_address}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in MaxMind lookup for IP {ip_address}: {str(e)}")
            return None

    def _get_from_ip_api(self, ip_address: str) -> Optional[Dict]:
        """Get location data from IP-API as backup."""
        try:
            response = requests.get(self.backup_ip_service.format(ip_address), timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'city': data.get('city', 'Unknown City'),
                        'country': data.get('country', 'Unknown Country'),
                        'latitude': float(data.get('lat', 0.0)),
                        'longitude': float(data.get('lon', 0.0)),
                        'accuracy_radius': 100,  # IP-API doesn't provide this
                        'timezone': data.get('timezone', 'UTC'),
                        'isp': data.get('isp', ''),
                        'connection_type': ''
                    }
            return None
        except Exception as e:
            logger.error(f"IP-API lookup failed for IP {ip_address}: {str(e)}")
            return None

    def _get_local_info(self) -> Dict:
        """Return default info for local/private IPs."""
        return {
            'city': 'Local',
            'country': 'Local',
            'latitude': 0.0,
            'longitude': 0.0,
            'accuracy_radius': 0,
            'timezone': 'UTC',
            'isp': 'Local Network',
            'connection_type': 'Local'
        }

    def parse_user_agent(self, user_agent_string: str) -> Tuple[str, str]:
        """Parse user agent string to get device and browser info."""
        try:
            user_agent = parse(user_agent_string)
            device_info = f"{user_agent.device.brand} {user_agent.device.model}"
            browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}"
            return device_info.strip(), browser_info.strip()
        except Exception as e:
            logger.error(f"Error parsing user agent: {str(e)}")
            return "Unknown Device", "Unknown Browser"

    def get_location_info(self, ip_address: str, user_agent: str = "") -> Dict:
        """
        Get comprehensive location information for an IP address.
        Includes fallback mechanisms and caching.
        """
        if not ip_address or ip_address in ('127.0.0.1', 'localhost', '::1'):
            return self._get_local_info()

        # Check cache first
        if ip_address in self.cache:
            return self.cache[ip_address]

        if not self._is_valid_ip(ip_address):
            logger.error(f"Invalid IP address format: {ip_address}")
            return self._get_local_info()

        # Try MaxMind first
        location_info = self._get_from_maxmind(ip_address)

        # Fallback to IP-API if MaxMind fails
        if not location_info:
            location_info = self._get_from_ip_api(ip_address)

        # If both services fail, return default values
        if not location_info:
            location_info = {
                'city': 'Unknown',
                'country': 'Unknown',
                'latitude': 0.0,
                'longitude': 0.0,
                'accuracy_radius': 0,
                'timezone': 'UTC',
                'isp': 'Unknown',
                'connection_type': 'Unknown'
            }

        # Parse user agent if provided
        if user_agent:
            device_info, browser_info = self.parse_user_agent(user_agent)
            location_info['device_info'] = device_info
            location_info['browser_info'] = browser_info

        # Cache the result
        self.cache[ip_address] = location_info
        return location_info
