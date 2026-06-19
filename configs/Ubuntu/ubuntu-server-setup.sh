#!/bin/bash
# =============================================================================
# ubuntu-server-setup.sh
# Ubuntu Server 22.04 LTS - Initial Setup and Hardening Script
# Project: Distributed Firewall VDC
#
# Run this script after initial Ubuntu Server installation.
# Applies baseline security hardening and installs required packages.
#
# Usage: sudo bash ubuntu-server-setup.sh [--role web|db|monitoring|ids]
# =============================================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ROLE="${1:---role}"
ROLE_VALUE="${2:-generic}"

log()     { echo -e "[$(date '+%H:%M:%S')] $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# =============================================================================
# BASELINE SETUP
# =============================================================================

baseline_setup() {
    log "Running baseline Ubuntu setup..."

    # Update system
    apt update && apt upgrade -y
    success "System updated"

    # Install common tools
    apt install -y \
        curl wget git vim htop iotop \
        nmap tcpdump netcat-openbsd \
        unzip jq \
        auditd apparmor \
        fail2ban \
        rsyslog \
        prometheus-node-exporter

    success "Common tools installed"

    # Set timezone
    timedatectl set-timezone UTC
    success "Timezone set to UTC"

    # Configure NTP
    cat > /etc/systemd/timesyncd.conf << EOF
[Time]
NTP=192.168.10.1
FallbackNTP=0.pool.ntp.org 1.pool.ntp.org
EOF
    systemctl restart systemd-timesyncd
    success "NTP configured"
}

# =============================================================================
# SECURITY HARDENING
# =============================================================================

harden_ssh() {
    log "Hardening SSH configuration..."

    # Backup original config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

    # Apply hardened SSH config
    cat > /etc/ssh/sshd_config << 'EOF'
# SSH Server Configuration - VDC Hardened
# Project: Distributed Firewall VDC

Port 22
AddressFamily inet
ListenAddress 0.0.0.0

# Authentication
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
ChallengeResponseAuthentication no

# Security
Protocol 2
X11Forwarding no
AllowTcpForwarding no
GatewayPorts no
PermitUserEnvironment no
AllowAgentForwarding no

# Timeouts
LoginGraceTime 30
MaxAuthTries 3
MaxSessions 5
ClientAliveInterval 300
ClientAliveCountMax 3

# Logging
SyslogFacility AUTH
LogLevel VERBOSE

# Banner
Banner /etc/ssh/banner.txt
EOF

    # SSH Banner
    cat > /etc/ssh/banner.txt << 'EOF'
*******************************************************************************
*  AUTHORIZED ACCESS ONLY  -  Distributed Firewall VDC Lab Environment        *
*  All connections are logged and monitored.                                   *
*  Unauthorized access is prohibited and will be prosecuted.                  *
*******************************************************************************
EOF

    systemctl restart sshd
    success "SSH hardened"
}

harden_kernel() {
    log "Applying kernel security parameters..."

    cat > /etc/sysctl.d/99-vdc-security.conf << 'EOF'
# VDC Security Kernel Parameters

# Disable IPv4 forwarding (enable on router VMs only)
net.ipv4.ip_forward = 0

# TCP SYN flood protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_syn_retries = 2
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_max_syn_backlog = 4096

# ICMP protection
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Disable IP source routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0

# Disable ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0

# Log suspicious packets
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# ARP protection
net.ipv4.conf.all.arp_filter = 1
net.ipv4.conf.all.rp_filter = 1

# Disable IPv6 (not used in lab)
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1

# Shared memory security
kernel.shmmax = 268435456
kernel.randomize_va_space = 2

# Core dumps disabled
fs.suid_dumpable = 0
EOF

    sysctl -p /etc/sysctl.d/99-vdc-security.conf
    success "Kernel hardened"
}

configure_auditd() {
    log "Configuring auditd..."

    cat > /etc/audit/rules.d/vdc-audit.rules << 'EOF'
# VDC Audit Rules
-D
-b 8192

# Monitor authentication
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k sudoers

# Monitor SSH
-w /etc/ssh/sshd_config -p wa -k ssh_config

# Monitor network config
-w /etc/network/ -p wa -k network
-w /etc/nftables.conf -p wa -k firewall

# Monitor cron
-w /etc/cron.d/ -p wa -k cron
-w /var/spool/cron/ -p wa -k cron

# Privilege escalation
-a always,exit -F arch=b64 -S setuid -k priv_esc
-a always,exit -F arch=b64 -S setgid -k priv_esc

# System calls
-a always,exit -F arch=b64 -S execve -k exec
EOF

    systemctl enable auditd
    systemctl restart auditd
    success "auditd configured"
}

configure_fail2ban() {
    log "Configuring fail2ban..."

    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd
action = %(action_mwl)s

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
maxretry = 3
bantime = 7200

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 5
EOF

    systemctl enable fail2ban
    systemctl restart fail2ban
    success "fail2ban configured"
}

configure_syslog_forwarding() {
    log "Configuring syslog forwarding to ELK Stack..."

    cat > /etc/rsyslog.d/50-vdc-remote.conf << 'EOF'
# Forward all logs to ELK Stack / Syslog server
# VDC Monitoring: 192.168.50.10

# Forward using UDP
*.* @192.168.50.10:514

# Forward using TCP (more reliable)
# *.* @@192.168.50.10:514
EOF

    systemctl restart rsyslog
    success "Syslog forwarding configured"
}

# =============================================================================
# ROLE-SPECIFIC SETUP
# =============================================================================

setup_web_server() {
    log "Setting up web server role..."
    apt install -y nginx certbot python3-certbot-nginx

    # Basic nginx config
    cat > /etc/nginx/sites-available/vdc-app << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name web01.vdc.local;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header Content-Security-Policy "default-src 'self'";

    location / {
        root /var/www/html;
        index index.html;
    }

    # Access log
    access_log /var/log/nginx/vdc-access.log;
    error_log /var/log/nginx/vdc-error.log;
}
EOF

    ln -sf /etc/nginx/sites-available/vdc-app /etc/nginx/sites-enabled/
    systemctl enable nginx
    systemctl start nginx
    success "Web server configured"
}

setup_db_server() {
    log "Setting up database server role..."
    apt install -y mysql-server

    # Secure MySQL
    mysql_secure_installation --use-default

    # Create VDC application user
    mysql -e "CREATE USER 'vdcapp'@'192.168.20.%' IDENTIFIED BY 'VDC@SecurePass2025!';"
    mysql -e "CREATE DATABASE vdc_app;"
    mysql -e "GRANT SELECT, INSERT, UPDATE, DELETE ON vdc_app.* TO 'vdcapp'@'192.168.20.%';"
    mysql -e "FLUSH PRIVILEGES;"

    # Bind MySQL to listen only on VLAN 30 interface
    sed -i 's/bind-address.*/bind-address = 192.168.30.10/' /etc/mysql/mysql.conf.d/mysqld.cnf

    systemctl enable mysql
    systemctl restart mysql
    success "Database server configured"
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    log "================================================"
    log " VDC Ubuntu Server Setup Script v2.0.0"
    log " Role: ${ROLE_VALUE}"
    log "================================================"

    # Must run as root
    [ "$(id -u)" -ne 0 ] && error "Must run as root" && exit 1

    baseline_setup
    harden_ssh
    harden_kernel
    configure_auditd
    configure_fail2ban
    configure_syslog_forwarding

    # Role-specific setup
    case "$ROLE_VALUE" in
        web)        setup_web_server ;;
        db)         setup_db_server ;;
        monitoring) log "Monitoring role - see monitoring/ directory for ELK/Grafana setup" ;;
        ids)        log "IDS role - run configs/IDS setup separately" ;;
        *)          log "Generic role - no role-specific setup" ;;
    esac

    success "Setup complete! Reboot recommended."
    log "================================================"
}

main "$@"
