# Leo Quick Start Guide

Get Leo running in 5 minutes.

## 1. Automatic Installation

```bash
cd /tmp
wget https://your-repo/leo-install.sh
sudo bash leo-install.sh
```

The installer will:
- Detect your Linux distribution
- Install Python and dependencies
- Create systemd service
- Configure logging
- Run health checks

## 2. Manual Installation

### Step 1: Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-dev libpcap-dev
```

**CentOS/Fedora:**
```bash
sudo dnf install -y python3 python3-pip python3-devel libpcap-devel
```

**Alpine:**
```bash
sudo apk add --no-cache python3 py3-pip python3-dev libpcap-dev
```

### Step 2: Install Python Packages

```bash
pip3 install -r requirements.txt
```

### Step 3: Setup Directories

```bash
sudo mkdir -p /opt/leo /opt/leo/data
sudo chmod 755 /opt/leo
```

### Step 4: Deploy Files

```bash
sudo cp leo*.py /opt/leo/
sudo chmod +x /opt/leo/leo.py
```

### Step 5: Create Configuration

```bash
sudo cp leo.conf /opt/leo/
sudo chmod 644 /opt/leo/leo.conf
```

## 3. Create Systemd Service

```bash
sudo tee /etc/systemd/system/leo.service > /dev/null << 'EOF'
[Unit]
Description=Leo DDoS Detection System
After=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/leo
ExecStart=/usr/bin/python3 /opt/leo/leo.py start
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable leo
```

## 4. Start Detection

```bash
sudo systemctl start leo
```

The dashboard appears immediately with real-time metrics.

## 5. Verify Installation

Check status:
```bash
leo status
```

View logs:
```bash
tail -f /var/log/leo-detection.log
```

View incidents:
```bash
tail -f /var/log/leo-incidents.jsonl
```

## Next Steps

### Configure Leo

Edit `/opt/leo/leo.conf` to customize:

```ini
# Change network interface
INTERFACE=eth1

# Adjust detection window
DETECTION_WINDOW=60

# Lower confidence for more alerts
MIN_CONFIDENCE=0.60

# Enable/disable features
ENABLE_ML=false
ENABLE_DPI=true
```

Then restart:
```bash
sudo systemctl restart leo
```

### Monitor Attacks

View real-time dashboard:
```bash
sudo leo start
```

View recent attacks:
```bash
sudo leo logs
```

Check performance:
```bash
sudo leo performance
```

### Integration

Export incidents to Elasticsearch:
```bash
while read line; do
  curl -X POST "elasticsearch:9200/leo/_doc" -d "$line"
done < /var/log/leo-incidents.jsonl
```

Forward logs to syslog:
```bash
tail -f /var/log/leo-detection.log | nc syslog-server 514
```

## Troubleshooting

### Service won't start
```bash
sudo systemctl status leo
sudo journalctl -u leo -n 50
```

### Check packet capture
```bash
sudo leo start    # Should show "Starting packet capture"
```

### Verify network interface
```bash
ip link show
```

### Check Python
```bash
python3 --version
pip3 list | grep scapy
```

## Commands Reference

```
leo start           Start detection + dashboard
leo status          Show current statistics
leo logs            Show recent attacks (JSON)
leo config          Show configuration
leo health          System health
leo performance     Performance metrics
leo help            Show all options
```

Options:
```
-i, --interface     Network interface (default: eth0)
-w, --window        Detection window seconds (default: 30)
-c, --confidence    Confidence threshold (default: 0.70)
```

## Common Tasks

### Change interface
```bash
sudo leo start -i eth1
# or edit /opt/leo/leo.conf and restart
```

### Increase sensitivity
```bash
# Lower confidence threshold
sudo leo start -c 0.50
```

### Adjust detection speed
```bash
# Smaller window = faster response
sudo leo start -w 10
```

### View top attackers
```bash
grep "type" /var/log/leo-incidents.jsonl | jq -r '.type' | sort | uniq -c | sort -rn
```

### Export to CSV
```bash
tail -f /var/log/leo-incidents.jsonl | jq -r '[.timestamp, .type, .severity, .pps, .mbps] | @csv'
```

## Getting Help

Check logs:
```bash
grep ERROR /var/log/leo-detection.log
```

View full documentation:
```bash
cat LEO_DOCUMENTATION.md
```

Common issues:
```bash
cat README.md | grep Troubleshooting -A 50
```

---

**Leo is now running and monitoring your network!**

See README.md for detailed documentation.
