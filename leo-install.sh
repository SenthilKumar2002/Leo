#!/bin/bash
# Leo Universal Installer
# Enterprise-grade installation with health checks and verification

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging
LOG_FILE="/tmp/leo-install.log"
exec 1> >(tee -a "$LOG_FILE")
exec 2>&1

# Configuration
LEO_HOME="/opt/leo"
LEO_DATA="$LEO_HOME/data"
LEO_LOG_DIR="/var/log"

# Banner
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                   LEO DETECTION SYSTEM                            ║"
echo "║          Advanced DDoS/DoS Detection Engine Installer              ║"
echo "║                                                                    ║"
echo "║              Enterprise-Grade Network Security                     ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
    log_success "Running as root"
}

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_NAME=$NAME
        DISTRO_VERSION=$VERSION_ID
    else
        log_error "Cannot detect Linux distribution"
        exit 1
    fi
    log_success "Detected: $DISTRO_NAME $DISTRO_VERSION"
}

install_dependencies() {
    log_info "Installing dependencies for $DISTRO_NAME..."
    
    case "$DISTRO" in
        ubuntu|debian)
            apt-get update -qq > /dev/null 2>&1
            apt-get install -y -qq python3 python3-pip python3-dev libpcap-dev build-essential curl wget git > /dev/null 2>&1
            ;;
        rhel|centos|fedora|rocky|alma)
            dnf install -y -q python3 python3-pip python3-devel libpcap-devel gcc gcc-c++ curl wget git > /dev/null 2>&1
            ;;
        alpine)
            apk update > /dev/null 2>&1
            apk add --no-cache -q python3 py3-pip python3-dev libpcap-dev gcc musl-dev curl wget git > /dev/null 2>&1
            ;;
        arch|manjaro)
            pacman -S --noconfirm -q python python-pip base-devel libpcap git curl wget > /dev/null 2>&1
            ;;
        opensuse*)
            zypper install -y -q python3 python3-pip python3-devel libpcap-devel gcc gcc-c++ curl wget git > /dev/null 2>&1
            ;;
        *)
            log_error "Unsupported distribution: $DISTRO"
            exit 1
            ;;
    esac
    
    log_success "Dependencies installed"
}

install_python_packages() {
    log_info "Installing Python packages..."
    
    pip3 install --quiet --upgrade pip setuptools wheel > /dev/null 2>&1
    
    for pkg in scapy numpy scikit-learn requests geoip2; do
        pip3 install --quiet "$pkg" > /dev/null 2>&1 || log_warning "Failed to install $pkg"
    done
    
    log_success "Python packages installed"
}

setup_directories() {
    log_info "Setting up directories..."
    mkdir -p "$LEO_HOME" "$LEO_DATA" "$LEO_LOG_DIR"
    chmod 755 "$LEO_HOME" "$LEO_DATA"
    log_success "Directories created"
}

create_config() {
    log_info "Creating configuration file..."
    cat > "$LEO_HOME/leo.conf" << 'CONFIG_EOF'
# Leo Configuration
INTERFACE=eth0
DETECTION_WINDOW=30
MIN_CONFIDENCE=0.70
ENABLE_ML=true
ENABLE_DPI=true
ENABLE_THREAT_INTEL=true
ENABLE_GEO_BLOCKING=false
ENABLE_RESPONSE=false
LOG_LEVEL=INFO
CONFIG_EOF
    log_success "Configuration file created"
}

create_service() {
    log_info "Creating systemd service..."
    cat > /etc/systemd/system/leo.service << 'SERVICE_EOF'
[Unit]
Description=Leo DDoS Detection System
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/leo
ExecStart=/usr/bin/python3 /opt/leo/leo.py start
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF
    systemctl daemon-reload > /dev/null 2>&1
    log_success "Systemd service created"
}

create_logrotate() {
    log_info "Setting up log rotation..."
    cat > /etc/logrotate.d/leo << 'LOGROTATE_EOF'
/var/log/leo*.log {
    daily
    rotate 10
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}

/var/log/leo-incidents.jsonl {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
LOGROTATE_EOF
    log_success "Log rotation configured"
}

init_logs() {
    log_info "Initializing log files..."
    touch "$LEO_LOG_DIR/leo-detection.log" "$LEO_LOG_DIR/leo-incidents.jsonl"
    chmod 666 "$LEO_LOG_DIR"/leo*.log "$LEO_LOG_DIR"/leo-incidents.jsonl
    log_success "Log files initialized"
}

health_check() {
    log_info "Running health checks..."
    python3 --version > /dev/null 2>&1 || { log_error "Python3 check failed"; return 1; }
    [ -d "$LEO_HOME" ] || { log_error "Directory check failed"; return 1; }
    [ -w "$LEO_HOME" ] || { log_error "Permission check failed"; return 1; }
    log_success "Health checks passed"
}

show_summary() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════╗"
    echo "║              Leo Installation Complete!                          ║"
    echo "╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Installation Summary:${NC}"
    echo "  Distribution: $DISTRO_NAME $DISTRO_VERSION"
    echo "  Installation Path: $LEO_HOME"
    echo "  Configuration: $LEO_HOME/leo.conf"
    echo "  Logs: $LEO_LOG_DIR"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo "  1. Copy Leo files to $LEO_HOME:"
    echo "     sudo cp leo*.py $LEO_HOME/"
    echo ""
    echo "  2. Make executable:"
    echo "     sudo chmod +x $LEO_HOME/leo.py"
    echo ""
    echo "  3. Start Leo:"
    echo "     sudo systemctl start leo"
    echo ""
    echo "  4. Check status:"
    echo "     sudo systemctl status leo"
    echo ""
    echo -e "${CYAN}Monitoring:${NC}"
    echo "  Dashboard: sudo leo start"
    echo "  Logs: tail -f $LEO_LOG_DIR/leo-detection.log"
    echo ""
}

main() {
    check_root
    detect_distro
    install_dependencies
    install_python_packages
    setup_directories
    create_config
    create_service
    create_logrotate
    init_logs
    health_check
    show_summary
    log_success "Installation completed successfully"
}

main
