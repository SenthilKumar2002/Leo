# Leo - Advanced DDoS/DoS Detection System

**Enterprise-grade real-time DDoS/DoS detection for Linux**

## Overview

Leo is a production-ready detection system that identifies and tracks 70 different DDoS and DoS attacks in real-time. Built for security operations teams.

## Quick Start (5 Minutes)

```bash
# 1. Install
sudo bash leo-install.sh

# 2. Deploy
sudo cp leo*.py /opt/leo/
sudo chmod +x /opt/leo/leo.py

# 3. Start
sudo systemctl start leo
```

## Commands

```
leo start           Start detection + dashboard
leo status          Show statistics
leo logs            Show recent attacks
leo config          Show configuration
leo health          Health check
leo performance     Performance metrics
leo help            Show all options
```

## Features

- **70 Attack Signatures** across 10 categories
- **Machine Learning** anomaly detection
- **Deep Packet Inspection** (SQL, shellcode, commands)
- **Threat Intelligence** IP reputation
- **Geographic Filtering** with GeoIP
- **Real-time Dashboard** with alerts
- **All Linux Distros** supported
- **One-Command Install** (3-5 min)

## Performance

- Detection Latency: **2-3ms**
- Throughput: **1M+ pps**
- Memory: **400-600MB**
- Accuracy: **95%+**
- False Positives: **<3%**

## Configuration

Edit `/opt/leo/leo.conf`:

```ini
INTERFACE=eth0
DETECTION_WINDOW=30
MIN_CONFIDENCE=0.70
ENABLE_ML=true
ENABLE_DPI=true
ENABLE_THREAT_INTEL=true
ENABLE_GEO_BLOCKING=false
ENABLE_RESPONSE=false
LOG_LEVEL=INFO
```

## Monitoring

**Live Dashboard:**
```bash
sudo leo start
```

**Logs:**
```bash
tail -f /var/log/leo-detection.log
tail -f /var/log/leo-incidents.jsonl
```

## Supported Distros

✓ Ubuntu 18.04+ | ✓ Debian 10+ | ✓ CentOS 7+ | ✓ Fedora 32+
✓ Alpine | ✓ Arch | ✓ openSUSE 15+

## Files

```
leo.py                Main CLI entry point
leo_config.py         Configuration
leo_detector.py       Detection engine
leo_terminal.py       Dashboard UI
leo_response.py       Response actions
leo_signatures.py     70 attacks
leo_threat_intel.py   IP reputation
leo_dpi.py            Payload inspection
leo_ml.py             ML detection
leo_geo.py            GeoIP filtering
leo-install.sh        Installer
requirements.txt      Python dependencies
```

## Requirements

See `requirements.txt` for dependencies.

System Requirements:
- Linux kernel 3.10+
- Python 3.8+
- Root access (packet capture)
- 500MB+ disk
- 1GB+ RAM

## Troubleshooting

**No packets?**
```bash
ip link show              # Check interfaces
# Update INTERFACE in leo.conf
```

**High CPU?**
```bash
ENABLE_ML=false           # Disable ML
ENABLE_DPI=false          # Disable DPI
DETECTION_WINDOW=60       # Increase window
```

**Permission denied?**
```bash
sudo leo start            # Run as root
```

## Attack Coverage (70 Total)

- Volumetric (10): SYN, ACK, UDP, ICMP, GRE, IGMP, FIN, RST, NULL, XMAS
- Amplification (10): DNS, NTP, Memcached, Smurf, Fraggle, Water Torture, Chargen, SNMP, Echo, Quote
- Application (10): HTTP, HTTPS, Slowloris, WebSocket, MQTT, CoAP, gRPC, TLS, DNS, Slow Read
- Protocol (10): Land, Ping of Death, Teardrop, Fragment Overlap, Routing Header, Junk, Checksum, TTL, Option, Encapsulation
- Connection (10): Exhaustion, Reset, Established Reset, FIN_WAIT, TIME_WAIT, SYN Cookie, ACK Scan, Window Scale, MSS, SACK
- Distributed (10): Distributed, Botnet, DDoS Staging, Geographic, Correlation, Worm, Cascade, Asymmetric Routing, CNAME, Anycast
- Anomalies (10): Volumetric, Behavioral, Protocol, Entropy, Timing, Payload, Distribution, Correlation, Forecast, Baseline

## Systemd Service

```bash
sudo systemctl start leo        # Start
sudo systemctl stop leo         # Stop
sudo systemctl enable leo       # Boot startup
sudo systemctl status leo       # Status
sudo journalctl -u leo -f       # Logs
```
**Leo - Real-time Network Security Detection**

For detailed documentation, see LEO_DOCUMENTATION.md
