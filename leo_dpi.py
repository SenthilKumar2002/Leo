"""
Leo DPI (Deep Packet Inspection) Module
Detects SQL injection, shellcode, command injection
"""

import math
from typing import Tuple
from leo_config import config

class DPI:
    """Deep Packet Inspection for attack detection"""
    
    def __init__(self):
        # SQL injection keywords
        self.sql_keywords = [
            "select", "union", "drop", "insert", "update", "delete",
            "exec", "execute", "script", "javascript", "alert",
            "xp_", "sp_", "table", "database", "admin", "password"
        ]
        
        # Shell metacharacters
        self.shell_chars = [";", "|", "&", "`", "$", "(", ")", "<", ">", "\n"]
        
        # Suspicious strings
        self.dangerous_strings = [
            "shellcode", "0x90", "0xCC", "payload", "msfvenom",
            "metasploit", "exploit", "ropchain", "gadget"
        ]
    
    def check_sql_injection(self, payload: bytes) -> Tuple[bool, float]:
        """Check for SQL injection patterns"""
        if not payload:
            return False, 0
        
        try:
            decoded = payload.decode('utf-8', errors='ignore').lower()
            matches = sum(1 for keyword in self.sql_keywords if keyword in decoded)
            
            if matches >= config.DPI_SQL_KEYWORDS_MIN:
                confidence = 0.7 + (matches * 0.05)
                return True, min(confidence, 0.95)
        except Exception:
            pass
        
        return False, 0
    
    def check_command_injection(self, payload: bytes) -> Tuple[bool, float]:
        """Check for command injection"""
        if not payload:
            return False, 0
        
        try:
            decoded = payload.decode('utf-8', errors='ignore')
            matches = sum(1 for char in self.shell_chars if char in decoded)
            
            if matches >= config.DPI_SHELL_CHARS_MIN:
                confidence = 0.6 + (matches * 0.05)
                return True, min(confidence, 0.90)
        except Exception:
            pass
        
        return False, 0
    
    def check_shellcode(self, payload: bytes) -> Tuple[bool, float]:
        """Check for potential shellcode"""
        if not payload:
            return False, 0
        
        try:
            # Calculate entropy
            entropy = self.calculate_entropy(payload)
            
            # Decode and check for dangerous strings
            decoded = payload.decode('utf-8', errors='ignore').lower()
            has_suspicious = sum(1 for s in self.dangerous_strings if s in decoded)
            
            # High entropy + suspicious strings = likely shellcode
            if entropy > config.DPI_ENTROPY_THRESHOLD and has_suspicious:
                confidence = 0.85
                return True, confidence
            
            # Very high entropy alone is suspicious
            elif entropy > 7.8:
                confidence = 0.75
                return True, confidence
        except Exception:
            pass
        
        return False, 0
    
    def check_encoding_bypass(self, payload: bytes) -> Tuple[bool, float]:
        """Check for encoding bypass attempts"""
        if not payload:
            return False, 0
        
        try:
            decoded = payload.decode('utf-8', errors='ignore').lower()
            
            # Check for common encoding patterns
            bypass_patterns = [
                "%20", "%27", "%22", "0x",
                "char(", "chr(", "unhex(", "concat(",
                "@@version", "information_schema",
                "sleep(", "benchmark(", "time_based"
            ]
            
            matches = sum(1 for pattern in bypass_patterns if pattern in decoded)
            
            if matches > 0:
                confidence = 0.7 + (matches * 0.05)
                return True, min(confidence, 0.90)
        except Exception:
            pass
        
        return False, 0
    
    @staticmethod
    def calculate_entropy(data: bytes) -> float:
        """Calculate Shannon entropy"""
        if not data:
            return 0
        
        entropy = 0
        for i in range(256):
            freq = data.count(bytes([i]))
            if freq:
                p = freq / len(data)
                entropy -= p * math.log2(p)
        
        return entropy
    
    def analyze_payload(self, payload: bytes) -> dict:
        """Comprehensive payload analysis"""
        if not payload:
            return {
                "is_suspicious": False,
                "confidence": 0,
                "sql_injection": (False, 0),
                "command_injection": (False, 0),
                "shellcode": (False, 0),
                "encoding_bypass": (False, 0),
                "entropy": 0
            }
        
        sql_inj = self.check_sql_injection(payload)
        cmd_inj = self.check_command_injection(payload)
        shellcode = self.check_shellcode(payload)
        encoding = self.check_encoding_bypass(payload)
        entropy = self.calculate_entropy(payload)
        
        # Aggregate suspicious indicators
        suspicious = any([sql_inj[0], cmd_inj[0], shellcode[0], encoding[0]])
        
        # Overall confidence
        confidence = max([sql_inj[1], cmd_inj[1], shellcode[1], encoding[1], 0])
        
        return {
            "is_suspicious": suspicious,
            "confidence": confidence,
            "sql_injection": sql_inj,
            "command_injection": cmd_inj,
            "shellcode": shellcode,
            "encoding_bypass": encoding,
            "entropy": entropy
        }

# Global DPI instance
dpi = DPI()
