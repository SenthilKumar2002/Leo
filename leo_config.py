"""
Leo Configuration Module
All settings in one place for easy management
"""

from dataclasses import dataclass
import os

@dataclass
class Config:
    """Leo configuration"""
    
    # Network
    INTERFACE: str = "eth0"
    
    # Detection
    DETECTION_WINDOW: int = 30  # seconds
    MIN_CONFIDENCE: float = 0.70
    MIN_EVIDENCE_POINTS: int = 3
    CORRELATION_WINDOW: int = 60
    
    # Features (enable/disable modules)
    ENABLE_RESPONSE: bool = True
    ENABLE_ML: bool = True
    ENABLE_DPI: bool = True
    ENABLE_THREAT_INTEL: bool = True
    ENABLE_GEO_BLOCKING: bool = False
    
    # Geo blocking
    GEO_BLOCKED_COUNTRIES: list = None  # ["KP", "CN", "RU"]
    
    # Paths
    LOG_FILE: str = "/var/log/leo-detection.log"
    INCIDENT_FILE: str = "/var/log/leo-incidents.jsonl"
    GEOIP_DB: str = "/opt/leo/geoip/GeoLite2-City.mmdb"
    IP_REPUTATION_DB: str = "/opt/leo/data/ip-reputation.json"
    ML_MODEL_FILE: str = "/opt/leo/data/ml-model.pkl"
    
    # ML Settings
    ML_CONTAMINATION: float = 0.10
    ML_N_ESTIMATORS: int = 100
    ML_TRAINING_SAMPLES: int = 1000
    
    # DPI Settings
    DPI_ENTROPY_THRESHOLD: float = 7.5
    DPI_SQL_KEYWORDS_MIN: int = 2
    DPI_SHELL_CHARS_MIN: int = 3
    
    # Response
    RESPONSE_MODE: str = "graduated"  # graduated, immediate, alert_only
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.GEO_BLOCKED_COUNTRIES is None:
            self.GEO_BLOCKED_COUNTRIES = []
        
        # Create directories if needed
        os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(self.IP_REPUTATION_DB), exist_ok=True)

# Global config instance
config = Config()
