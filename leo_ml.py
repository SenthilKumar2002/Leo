"""
Leo ML (Machine Learning) Module
Isolation Forest based anomaly detection
"""

import numpy as np
from collections import deque
from typing import Tuple, List
from leo_config import config
import logging

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("scikit-learn not available - ML detection disabled")

class MLDetector:
    """Machine Learning based anomaly detection"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.training_data = deque(maxlen=config.ML_TRAINING_SAMPLES)
        self.is_trained = False
        
        if ML_AVAILABLE:
            self.initialize_model()
    
    def initialize_model(self):
        """Initialize Isolation Forest model"""
        try:
            self.model = IsolationForest(
                contamination=config.ML_CONTAMINATION,
                n_estimators=config.ML_N_ESTIMATORS,
                random_state=42
            )
            self.scaler = StandardScaler()
            logger.info("ML model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ML model: {e}")
            ML_AVAILABLE = False
    
    def extract_features(self, metrics: dict) -> List[float]:
        """Extract feature vector from metrics"""
        return [
            metrics.get('pps', 0),
            metrics.get('mbps', 0),
            metrics.get('syn_ratio', 0),
            metrics.get('ack_ratio', 0),
            metrics.get('udp_ratio', 0),
            metrics.get('icmp_ratio', 0),
            metrics.get('unique_src_ips', 0),
            metrics.get('unique_flows', 0),
            metrics.get('avg_flow_entropy', 0),
        ]
    
    def add_training_sample(self, metrics: dict):
        """Add metrics for training"""
        if ML_AVAILABLE:
            features = self.extract_features(metrics)
            self.training_data.append(features)
    
    def train(self):
        """Train model on collected data"""
        if not ML_AVAILABLE or len(self.training_data) < 10:
            return False
        
        try:
            features = list(self.training_data)
            
            # Scale features
            scaled = self.scaler.fit_transform(features)
            
            # Train model
            self.model.fit(scaled)
            self.is_trained = True
            
            logger.info(f"ML model trained on {len(features)} samples")
            return True
        except Exception as e:
            logger.error(f"ML training failed: {e}")
            return False
    
    def detect_anomaly(self, metrics: dict) -> Tuple[bool, float]:
        """Detect anomalies using isolation forest"""
        if not ML_AVAILABLE or not self.is_trained:
            return False, 0
        
        try:
            features = np.array(self.extract_features(metrics)).reshape(1, -1)
            scaled = self.scaler.transform(features)
            
            # Get anomaly score (-1 to 1, higher = more anomalous)
            anomaly_score = -self.model.score_samples(scaled)[0]
            
            # Convert to confidence (0 to 1)
            confidence = min(max(anomaly_score / 2, 0), 1.0)
            
            # Threshold for detection
            if confidence > 0.5:
                return True, confidence
        except Exception as e:
            logger.warning(f"Anomaly detection failed: {e}")
        
        return False, 0
    
    def get_status(self) -> dict:
        """Get ML module status"""
        return {
            "available": ML_AVAILABLE,
            "trained": self.is_trained,
            "training_samples": len(self.training_data),
            "model": "Isolation Forest" if self.model else None
        }

# Global ML detector instance
ml_detector = MLDetector()
