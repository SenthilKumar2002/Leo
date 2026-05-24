"""
Leo Threat Intelligence Module
IP reputation scoring and threat tracking
"""

import json
import time
import os
from collections import defaultdict
from leo_config import config
import logging

logger = logging.getLogger(__name__)

class ThreatIntelligence:
    """Threat intelligence and reputation scoring"""
    
    def __init__(self):
        self.ip_reputation = defaultdict(lambda: {
            "reputation": 0.0,
            "attack_count": 0,
            "last_seen": 0,
            "first_seen": 0,
            "attacks": []
        })
        self.malicious_ips = set()
        self.load_reputation_db()
    
    def load_reputation_db(self):
        """Load local IP reputation database"""
        if not os.path.exists(config.IP_REPUTATION_DB):
            logger.info("IP reputation database not found, starting fresh")
            return
        
        try:
            with open(config.IP_REPUTATION_DB, 'r') as f:
                data = json.load(f)
                for ip, reputation_data in data.items():
                    self.ip_reputation[ip].update(reputation_data)
            logger.info(f"Loaded reputation for {len(self.ip_reputation)} IPs")
        except Exception as e:
            logger.error(f"Failed to load reputation DB: {e}")
    
    def save_reputation_db(self):
        """Save IP reputation database"""
        try:
            os.makedirs(os.path.dirname(config.IP_REPUTATION_DB), exist_ok=True)
            with open(config.IP_REPUTATION_DB, 'w') as f:
                json.dump(dict(self.ip_reputation), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save reputation DB: {e}")
    
    def get_ip_reputation(self, ip: str) -> float:
        """Get IP reputation score (0-1.0)"""
        return self.ip_reputation[ip].get("reputation", 0.0)
    
    def get_ip_stats(self, ip: str) -> dict:
        """Get complete IP statistics"""
        return {
            "ip": ip,
            "reputation": self.ip_reputation[ip]["reputation"],
            "attack_count": self.ip_reputation[ip]["attack_count"],
            "first_seen": self.ip_reputation[ip]["first_seen"],
            "last_seen": self.ip_reputation[ip]["last_seen"],
            "attacks": self.ip_reputation[ip]["attacks"][-10:]  # Last 10 attacks
        }
    
    def mark_as_attacker(self, ip: str, attack_type: str, confidence: float):
        """Mark IP as attacker and update reputation"""
        current_time = time.time()
        
        if self.ip_reputation[ip]["attack_count"] == 0:
            self.ip_reputation[ip]["first_seen"] = current_time
        
        self.ip_reputation[ip]["attack_count"] += 1
        self.ip_reputation[ip]["last_seen"] = current_time
        
        # Reputation increases with attack count
        # Max 1.0 at 10+ attacks
        self.ip_reputation[ip]["reputation"] = min(
            self.ip_reputation[ip]["attack_count"] / 10,
            1.0
        )
        
        # Track last 100 attacks per IP
        self.ip_reputation[ip]["attacks"].append({
            "type": attack_type,
            "confidence": confidence,
            "timestamp": current_time
        })
        
        if len(self.ip_reputation[ip]["attacks"]) > 100:
            self.ip_reputation[ip]["attacks"].pop(0)
        
        # Mark as malicious after 3 attacks
        if self.ip_reputation[ip]["attack_count"] >= 3:
            self.malicious_ips.add(ip)
    
    def is_known_attacker(self, ip: str) -> bool:
        """Check if IP is known attacker"""
        return ip in self.malicious_ips
    
    def get_top_attackers(self, limit: int = 10) -> list:
        """Get top attacking IPs"""
        sorted_ips = sorted(
            self.ip_reputation.items(),
            key=lambda x: x[1]["attack_count"],
            reverse=True
        )
        return [
            {
                "ip": ip,
                "attacks": data["attack_count"],
                "reputation": data["reputation"],
                "last_seen": data["last_seen"]
            }
            for ip, data in sorted_ips[:limit]
        ]
    
    def cleanup_old_entries(self, days: int = 30):
        """Remove old IP entries (older than N days)"""
        cutoff = time.time() - (days * 24 * 3600)
        to_remove = [
            ip for ip, data in self.ip_reputation.items()
            if data["last_seen"] < cutoff and data["attack_count"] < 3
        ]
        
        for ip in to_remove:
            del self.ip_reputation[ip]
        
        logger.info(f"Cleaned up {len(to_remove)} old IP entries")

# Global threat intel instance
threat_intel = ThreatIntelligence()
