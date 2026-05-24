"""
Leo Detector
Core detection engine with all modules integrated
"""

import json
import time
import logging
import threading
from collections import defaultdict, deque
from datetime import datetime
from typing import Optional, Dict

from scapy.all import sniff, IP, TCP, UDP, ICMP, Raw

from leo_config import config
from leo_signatures import ATTACK_SIGNATURES
from leo_threat_intel import threat_intel
from leo_dpi import dpi
from leo_ml import ml_detector
from leo_geo import geo_blocker

logger = logging.getLogger(__name__)

class Flow:
    """Flow tracking (5-tuple)"""
    def __init__(self, src_ip, dst_ip, protocol, src_port=0, dst_port=0):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.protocol = protocol
        self.src_port = src_port
        self.dst_port = dst_port
        self.packets = 0
        self.bytes = 0
        self.first_seen = time.time()
        self.last_seen = time.time()
        self.flags = set()

class LeoDetector:
    """Main detection engine"""
    
    def __init__(self):
        self.packets = deque(maxlen=config.DETECTION_WINDOW)
        self.bytes_sent = deque(maxlen=config.DETECTION_WINDOW)
        self.flows = {}
        self.window_history = deque(maxlen=100)
        
        # Counters
        self.tcp_syns = 0
        self.tcp_acks = 0
        self.tcp_rsts = 0
        self.tcp_fins = 0
        self.udp_count = 0
        self.icmp_count = 0
        
        # IPs
        self.src_ips = defaultdict(lambda: {"packets": 0, "bytes": 0})
        self.dst_ips = defaultdict(lambda: {"packets": 0, "bytes": 0})
        
        # Stats
        self.total_packets = 0
        self.total_bytes = 0
        self.total_alerts = 0
        self.recent_alerts = deque(maxlen=100)
        
        logger.info("Leo Detector initialized")
    
    def process_packet(self, packet):
        """Process single packet"""
        self.total_packets += 1
        
        if not IP in packet:
            return
        
        ip = packet[IP]
        pkt_size = len(packet)
        
        self.packets.append(1)
        self.bytes_sent.append(pkt_size)
        self.total_bytes += pkt_size
        
        self.src_ips[ip.src]["packets"] += 1
        self.src_ips[ip.src]["bytes"] += pkt_size
        self.dst_ips[ip.dst]["packets"] += 1
        self.dst_ips[ip.dst]["bytes"] += pkt_size
        
        # Protocol classification
        if TCP in packet:
            tcp = packet[TCP]
            if tcp.flags & 0x02:
                self.tcp_syns += 1
            if tcp.flags & 0x10:
                self.tcp_acks += 1
            if tcp.flags & 0x04:
                self.tcp_rsts += 1
            if tcp.flags & 0x01:
                self.tcp_fins += 1
        elif UDP in packet:
            self.udp_count += 1
        elif ICMP in packet:
            self.icmp_count += 1
    
    def calculate_metrics(self) -> Optional[Dict]:
        """Calculate detection metrics - refactored to eliminate duplication"""
        if len(self.packets) < 10:
            return None
        
        total = max(self.total_packets, 1)
        pps = len(self.packets) / config.DETECTION_WINDOW
        mbps = (sum(self.bytes_sent) * 8) / (1_000_000 * config.DETECTION_WINDOW)
        
        # Helper: safe division
        def safe_ratio(num, denom):
            return num / max(denom, 1)
        
        # Build metrics
        metrics = {
            'pps': pps,
            'mbps': mbps,
            'syn_ratio': safe_ratio(self.tcp_syns, self.tcp_syns + self.tcp_acks),
            'ack_ratio': safe_ratio(self.tcp_acks, self.tcp_syns + self.tcp_acks),
            'rst_ratio': safe_ratio(self.tcp_rsts, self.tcp_syns + 1),
            'fin_ratio': safe_ratio(self.tcp_fins, self.tcp_syns + 1),
            'udp_ratio': safe_ratio(self.udp_count, total),
            'icmp_ratio': safe_ratio(self.icmp_count, total),
            'unique_src_ips': len(self.src_ips),
            'unique_dst_ips': len(self.dst_ips),
            'unique_flows': len(self.flows),
        }
        
        self.window_history.append(metrics)
        return metrics
    
    def detect(self) -> Optional[Dict]:
        """Detect attacks"""
        metrics = self.calculate_metrics()
        if not metrics:
            return None
        
        # Check signatures
        for attack_type, sig in ATTACK_SIGNATURES.items():
            confidence = self._score_signature(metrics, sig)
            
            if confidence >= config.MIN_CONFIDENCE:
                # ML boost
                if config.ENABLE_ML:
                    is_anomaly, anomaly_conf = ml_detector.detect_anomaly(metrics)
                    if is_anomaly:
                        confidence *= (1 + anomaly_conf * 0.3)
                
                # Final confidence
                confidence = min(confidence, 1.0)
                
                # Create alert
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'type': attack_type,
                    'confidence': confidence,
                    'severity': sig.get('severity', 'UNKNOWN'),
                    'pps': metrics['pps'],
                    'mbps': metrics['mbps'],
                }
                
                self.recent_alerts.append(alert)
                self.total_alerts += 1
                return alert
        
        return None
    
    def _score_signature(self, metrics: Dict, sig: Dict) -> float:
        """Score signature match"""
        base_conf = sig.get('confidence', 0.5)
        matches = 0
        
        for metric_name, op, threshold in sig.get('indicators', []):
            value = metrics.get(metric_name, 0)
            
            if op == '>' and value > threshold:
                matches += 1
            elif op == '<' and value < threshold:
                matches += 1
            elif op == '==' and value == threshold:
                matches += 1
        
        match_ratio = matches / max(len(sig.get('indicators', [])), 1)
        return base_conf * match_ratio if match_ratio > 0.5 else 0
    
    def reset_counters(self):
        """Reset window counters"""
        self.tcp_syns = 0
        self.tcp_acks = 0
        self.tcp_rsts = 0
        self.tcp_fins = 0
        self.udp_count = 0
        self.icmp_count = 0
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        critical = sum(1 for a in self.recent_alerts if a.get('severity') == 'CRITICAL')
        high = sum(1 for a in self.recent_alerts if a.get('severity') == 'HIGH')
        
        return {
            'total_packets': self.total_packets,
            'total_bytes': self.total_bytes,
            'total_alerts': self.total_alerts,
            'critical': critical,
            'high': high,
            'uptime_seconds': int(time.time()),
            'recent_alerts': list(self.recent_alerts)
        }

detector = LeoDetector()
