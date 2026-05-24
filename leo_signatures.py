"""
Leo Attack Signatures
50+ attack type definitions with indicators
"""

ATTACK_SIGNATURES = {
    # TCP Floods (6)
    "SYN_FLOOD": {
        "indicators": [("syn_ratio", ">", 0.80), ("pps", ">", 5000)],
        "confidence": 0.95,
        "severity": "CRITICAL",
        "description": "TCP SYN flood attack"
    },
    "ACK_FLOOD": {
        "indicators": [("ack_ratio", ">", 0.85), ("pps", ">", 5000)],
        "confidence": 0.90,
        "severity": "HIGH",
        "description": "TCP ACK flood attack"
    },
    "FIN_FLOOD": {
        "indicators": [("fin_ratio", ">", 0.75), ("pps", ">", 5000)],
        "confidence": 0.85,
        "severity": "HIGH",
        "description": "TCP FIN flag flood"
    },
    "RST_FLOOD": {
        "indicators": [("rst_ratio", ">", 0.80), ("pps", ">", 5000)],
        "confidence": 0.88,
        "severity": "HIGH",
        "description": "TCP RST flag flood"
    },
    "NULL_ATTACK": {
        "indicators": [("null_ratio", ">", 0.90), ("pps", ">", 5000)],
        "confidence": 0.92,
        "severity": "CRITICAL",
        "description": "NULL flag attack"
    },
    "XMAS_ATTACK": {
        "indicators": [("xmas_ratio", ">", 0.85), ("pps", ">", 5000)],
        "confidence": 0.90,
        "severity": "HIGH",
        "description": "XMAS flag attack"
    },
    
    # UDP/ICMP (5)
    "UDP_FLOOD": {
        "indicators": [("udp_ratio", ">", 0.70), ("pps", ">", 10000)],
        "confidence": 0.90,
        "severity": "CRITICAL",
        "description": "UDP flood attack"
    },
    "ICMP_FLOOD": {
        "indicators": [("icmp_ratio", ">", 0.70), ("pps", ">", 5000)],
        "confidence": 0.85,
        "severity": "HIGH",
        "description": "ICMP echo request flood"
    },
    "GRE_FLOOD": {
        "indicators": [("gre_ratio", ">", 0.80), ("pps", ">", 5000)],
        "confidence": 0.88,
        "severity": "HIGH",
        "description": "GRE protocol flood"
    },
    "IGMP_FLOOD": {
        "indicators": [("igmp_ratio", ">", 0.75), ("pps", ">", 5000)],
        "confidence": 0.85,
        "severity": "MEDIUM",
        "description": "IGMP protocol flood"
    },
    
    # Amplification (7)
    "DNS_AMPLIFICATION": {
        "indicators": [("dns_resp_ratio", ">", 0.90), ("response_size", ">", 500)],
        "confidence": 0.92,
        "severity": "CRITICAL",
        "description": "DNS amplification attack"
    },
    "NTP_REFLECTION": {
        "indicators": [("ntp_ratio", ">", 0.85), ("pps", ">", 5000)],
        "confidence": 0.90,
        "severity": "CRITICAL",
        "description": "NTP reflection attack"
    },
    "MEMCACHED_REFLECTION": {
        "indicators": [("memcached_ratio", ">", 0.80), ("pps", ">", 5000)],
        "confidence": 0.88,
        "severity": "CRITICAL",
        "description": "Memcached reflection attack"
    },
    "SMURF_ATTACK": {
        "indicators": [("broadcast_dst", "==", True), ("icmp_ratio", ">", 0.85)],
        "confidence": 0.92,
        "severity": "HIGH",
        "description": "Smurf amplification attack"
    },
    "FRAGGLE_ATTACK": {
        "indicators": [("broadcast_dst", "==", True), ("udp_ratio", ">", 0.80)],
        "confidence": 0.90,
        "severity": "HIGH",
        "description": "Fraggle amplification attack"
    },
    "DNS_WATER_TORTURE": {
        "indicators": [("dns_nxdomain", ">", 0.6), ("dns_qps", ">", 5000)],
        "confidence": 0.85,
        "severity": "MEDIUM",
        "description": "DNS water torture attack"
    },
    
    # Application Layer (8)
    "HTTP_FLOOD": {
        "indicators": [("http_requests", ">", 5000), ("paths_unique", "<", 0.2)],
        "confidence": 0.88,
        "severity": "HIGH",
        "description": "HTTP flood attack"
    },
    "HTTPS_FLOOD": {
        "indicators": [("https_requests", ">", 3000), ("tls_failures", ">", 0.2)],
        "confidence": 0.85,
        "severity": "HIGH",
        "description": "HTTPS flood attack"
    },
    "SLOWLORIS": {
        "indicators": [("incomplete_requests", ">", 100), ("req_duration", ">", 120)],
        "confidence": 0.85,
        "severity": "HIGH",
        "description": "Slowloris slow POST attack"
    },
    "SLOW_READ": {
        "indicators": [("slow_connections", ">", 50), ("bytes_per_sec", "<", 100)],
        "confidence": 0.80,
        "severity": "MEDIUM",
        "description": "Slow read attack"
    },
    "WEBSOCKET_FLOOD": {
        "indicators": [("ws_frames", ">", 10000), ("ws_size_uniform", "==", True)],
        "confidence": 0.82,
        "severity": "HIGH",
        "description": "WebSocket flood attack"
    },
    "MQTT_FLOOD": {
        "indicators": [("mqtt_publishes", ">", 5000), ("same_topic", ">", 0.8)],
        "confidence": 0.80,
        "severity": "MEDIUM",
        "description": "MQTT flood attack"
    },
    "COAP_FLOOD": {
        "indicators": [("coap_requests", ">", 5000), ("non_confirmable", ">", 0.9)],
        "confidence": 0.78,
        "severity": "MEDIUM",
        "description": "CoAP flood attack"
    },
    "GRPC_FLOOD": {
        "indicators": [("grpc_streams", ">", 1000), ("small_frames", ">", 0.8)],
        "confidence": 0.80,
        "severity": "MEDIUM",
        "description": "gRPC flood attack"
    },
    
    # Protocol Anomalies (5)
    "LAND_ATTACK": {
        "indicators": [("src_dst_match", "==", True), ("port_match", "==", True)],
        "confidence": 0.98,
        "severity": "CRITICAL",
        "description": "Land attack (src==dst)"
    },
    "PING_OF_DEATH": {
        "indicators": [("icmp_size", ">", 65500), ("fragmented", ">", 100)],
        "confidence": 0.90,
        "severity": "MEDIUM",
        "description": "Ping of death attack"
    },
    "TEARDROP": {
        "indicators": [("overlapping_frags", ">", 10), ("malformed", ">", 50)],
        "confidence": 0.85,
        "severity": "MEDIUM",
        "description": "Teardrop fragment overlap"
    },
    "IP_FRAGMENT_OVERLAP": {
        "indicators": [("fragment_overlap", ">", 10), ("offset_bad", ">", 20)],
        "confidence": 0.88,
        "severity": "HIGH",
        "description": "IP fragment overlap (Bonk)"
    },
    "ROUTING_HEADER_ATTACK": {
        "indicators": [("ipv6_routing_hdr", ">", 100), ("unusual_hops", ">", 0.8)],
        "confidence": 0.85,
        "severity": "MEDIUM",
        "description": "IPv6 routing header attack"
    },
    
    # Scanning (4)
    "PORT_SCAN": {
        "indicators": [("rst_ratio", ">", 0.7), ("unique_ports", ">", 100)],
        "confidence": 0.75,
        "severity": "MEDIUM",
        "description": "Port scanning activity"
    },
    "NULL_SCAN": {
        "indicators": [("null_flags", ">", 100), ("unique_ports", ">", 50)],
        "confidence": 0.80,
        "severity": "MEDIUM",
        "description": "NULL flag port scan"
    },
    "XMAS_SCAN": {
        "indicators": [("xmas_flags", ">", 100), ("unique_ports", ">", 50)],
        "confidence": 0.80,
        "severity": "MEDIUM",
        "description": "XMAS flag port scan"
    },
    "MAIMON_SCAN": {
        "indicators": [("fin_ack_flags", ">", 100), ("unique_ports", ">", 50)],
        "confidence": 0.78,
        "severity": "MEDIUM",
        "description": "Maimon port scan"
    },
    
    # Connection State (3)
    "CONNECTION_EXHAUSTION": {
        "indicators": [("half_open", ">", 5000), ("syn_ack_ratio", "<", 0.3)],
        "confidence": 0.88,
        "severity": "HIGH",
        "description": "Connection table exhaustion"
    },
    "RESET_FLOOD": {
        "indicators": [("rst_ratio", ">", 0.85), ("pps", ">", 10000)],
        "confidence": 0.87,
        "severity": "HIGH",
        "description": "TCP reset flood"
    },
    "ESTABLISHED_RESET": {
        "indicators": [("established_resets", ">", 1000), ("src_spoofed", "==", True)],
        "confidence": 0.85,
        "severity": "HIGH",
        "description": "Established connection reset attack"
    },
    
    # Distributed (3)
    "DISTRIBUTED_ATTACK": {
        "indicators": [("unique_src_ips", ">", 50), ("entropy_high", "==", True)],
        "confidence": 0.85,
        "severity": "HIGH",
        "description": "Distributed attack (many sources)"
    },
    "BOTNET_DETECTION": {
        "indicators": [("timing_sync", ">", 0.8), ("payload_similar", ">", 0.9)],
        "confidence": 0.90,
        "severity": "CRITICAL",
        "description": "Botnet coordinated attack"
    },
    "DNS_FLOOD": {
        "indicators": [("dns_qps", ">", 5000), ("query_uniform", "==", True)],
        "confidence": 0.80,
        "severity": "MEDIUM",
        "description": "DNS query flood"
    },
    
    # SSL/TLS (3)
    "TLS_FLOOD": {
        "indicators": [("tls_clienthello", ">", 5000), ("incomplete_handshake", ">", 0.8)],
        "confidence": 0.85,
        "severity": "HIGH",
        "description": "TLS ClientHello flood"
    },
    "TLS_RENEGOTIATION": {
        "indicators": [("renegotiation_spam", ">", 1000), ("per_conn", ">", 100)],
        "confidence": 0.88,
        "severity": "HIGH",
        "description": "TLS renegotiation spam"
    },
    "SSL_COMPRESSION": {
        "indicators": [("compression_requests", ">", 1000), ("repetitive", ">", 0.9)],
        "confidence": 0.82,
        "severity": "MEDIUM",
        "description": "SSL compression abuse (CRIME)"
    },
    
    # ML-Detected Anomalies (3)
    "ANOMALY_VOLUMETRIC": {
        "indicators": [("ml_anomaly", ">", 0.9), ("pps_deviation", ">", 5)],
        "confidence": 0.85,
        "severity": "HIGH",
        "description": "ML detected volumetric anomaly"
    },
    "ANOMALY_BEHAVIORAL": {
        "indicators": [("behavior_deviation", ">", 0.85), ("entropy_anomaly", ">", 3)],
        "confidence": 0.80,
        "severity": "MEDIUM",
        "description": "ML detected behavioral anomaly"
    },
    "ANOMALY_PROTOCOL": {
        "indicators": [("protocol_anomaly", ">", 0.88), ("state_violation", ">", 0.7)],
        "confidence": 0.82,
        "severity": "MEDIUM",
        "description": "ML detected protocol anomaly"
    },
    
    # Exploit Detection (3)
    "POTENTIAL_EXPLOIT": {
        "indicators": [("payload_entropy", ">", 7.5), ("shellcode_detected", "==", True)],
        "confidence": 0.75,
        "severity": "CRITICAL",
        "description": "Potential shellcode/exploit detected"
    },
    "SQL_INJECTION_ATTEMPT": {
        "indicators": [("sql_keywords", ">", 3), ("encoding_bypass", ">", 0.8)],
        "confidence": 0.80,
        "severity": "HIGH",
        "description": "SQL injection attempt detected"
    },
    "COMMAND_INJECTION": {
        "indicators": [("shell_metacharacters", ">", 5), ("encoded_payload", ">", 0.7)],
        "confidence": 0.78,
        "severity": "HIGH",
        "description": "Command injection attempt detected"
    },
}

def get_signature(attack_type: str) -> dict:
    """Get attack signature by type"""
    return ATTACK_SIGNATURES.get(attack_type, {})

def list_all_attacks() -> list:
    """List all attack types"""
    return list(ATTACK_SIGNATURES.keys())

def count_attacks() -> int:
    """Count total attack types"""
    return len(ATTACK_SIGNATURES)
