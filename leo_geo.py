"""
Leo GeoIP Module
Geographic blocking and location analysis
"""

import os
from typing import Dict
from leo_config import config
import logging

logger = logging.getLogger(__name__)

try:
    import geoip2.database
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False
    logger.warning("geoip2 not available - geographic blocking disabled")

class GeoBlocking:
    """Geographic blocking and analysis"""
    
    def __init__(self):
        self.reader = None
        self.blocked_countries = set(config.GEO_BLOCKED_COUNTRIES)
        self.cache = {}
        
        if GEOIP_AVAILABLE:
            self.load_geoip_db()
    
    def load_geoip_db(self):
        """Load MaxMind GeoLite2 database"""
        if not os.path.exists(config.GEOIP_DB):
            logger.warning(f"GeoIP database not found: {config.GEOIP_DB}")
            logger.info("Download from: https://www.maxmind.com/en/geolite2")
            return
        
        try:
            self.reader = geoip2.database.Reader(config.GEOIP_DB)
            logger.info("GeoIP database loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load GeoIP database: {e}")
    
    def get_location(self, ip: str) -> Dict:
        """Get IP geolocation"""
        # Check cache first
        if ip in self.cache:
            return self.cache[ip]
        
        if not self.reader:
            return {}
        
        try:
            response = self.reader.city(ip)
            location = {
                "country": response.country.iso_code,
                "country_name": response.country.name,
                "city": response.city.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "timezone": response.location.time_zone
            }
            
            # Cache result
            self.cache[ip] = location
            
            # Limit cache size
            if len(self.cache) > 10000:
                # Remove oldest 1000 entries
                for _ in range(1000):
                    self.cache.pop(next(iter(self.cache)))
            
            return location
        except Exception as e:
            logger.debug(f"Failed to get location for {ip}: {e}")
            return {}
    
    def should_block(self, ip: str) -> bool:
        """Check if IP should be geo-blocked"""
        if not self.blocked_countries or not config.ENABLE_GEO_BLOCKING:
            return False
        
        location = self.get_location(ip)
        if not location:
            return False
        
        country = location.get("country")
        return country in self.blocked_countries
    
    def get_country(self, ip: str) -> str:
        """Get country code for IP"""
        location = self.get_location(ip)
        return location.get("country", "UNKNOWN")
    
    def get_status(self) -> dict:
        """Get GeoIP module status"""
        return {
            "available": GEOIP_AVAILABLE,
            "database_loaded": self.reader is not None,
            "blocked_countries": list(self.blocked_countries),
            "cache_size": len(self.cache)
        }
    
    def clear_cache(self):
        """Clear geolocation cache"""
        self.cache.clear()
        logger.info("GeoIP cache cleared")

# Global geo blocker instance
geo_blocker = GeoBlocking()
