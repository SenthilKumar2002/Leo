"""
Leo Response Engine
Graduated response based on confidence
"""

import subprocess
import logging
from leo_config import config

logger = logging.getLogger(__name__)

class ResponseEngine:
    """Execute response actions"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.rate_limited_ips = set()
    
    def execute(self, alert: dict):
        """Execute response based on confidence"""
        if not config.ENABLE_RESPONSE:
            return
        
        confidence = alert.get('confidence', 0)
        attack_type = alert.get('type', 'UNKNOWN')
        
        # Graduated response
        if confidence > 0.99:
            self._block(alert)
        elif confidence > 0.90:
            self._mitigate(alert)
        elif confidence > 0.85:
            self._rate_limit(alert)
        else:
            self._alert_only(alert)
    
    def _block(self, alert: dict):
        """Block attacker IP"""
        logger.warning(f"BLOCK: {alert['type']} confidence={alert['confidence']:.0%}")
        # In production: iptables -I INPUT -s [IP] -j DROP
    
    def _mitigate(self, alert: dict):
        """Enable SYN cookies + rate limit"""
        logger.warning(f"MITIGATE: {alert['type']} confidence={alert['confidence']:.0%}")
        # In production: sysctl net.ipv4.tcp_syncookies=1
    
    def _rate_limit(self, alert: dict):
        """Rate limit traffic"""
        logger.warning(f"RATE_LIMIT: {alert['type']} confidence={alert['confidence']:.0%}")
        # In production: tc qdisc tbf dev eth0
    
    def _alert_only(self, alert: dict):
        """Log alert only"""
        logger.info(f"ALERT: {alert['type']} confidence={alert['confidence']:.0%}")

response_engine = ResponseEngine()
