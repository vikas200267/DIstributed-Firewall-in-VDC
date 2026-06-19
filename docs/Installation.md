# Installation Guide

## Overview

This guide walks through the complete installation of the Distributed Firewall VDC lab environment. Follow the steps in order to ensure correct configuration.

**Estimated Setup Time**: 8–12 hours (first time) | 2–3 hours (scripted)

---

## Phase 1: Host Preparation

### 1.1 System Requirements Verification

```powershell
# Verify CPU virtualization support
(Get-WmiObject -Class Win32_Processor).VirtualizationFirmwareEnabled

# Check available RAM
(Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB

# Check disk space
Get-PSDrive -PSProvider FileSystem
```

### 1.2 Enable Hyper-V / VT-x in BIOS

1. Restart host machine
2. Enter BIOS/UEFI settings (F2/Del/F12 depending on manufacturer)
3. Navigate to **CPU Configuration** → **Virtualization Technology**
4. Set to **Enabled**
5. Save and exit

### 1.3 Install VMware Workstation 17

```powershell
# Run the installer (adjust path as needed)
Start-Process -FilePath 'VMware-workstation-full-17.x.x-XXXXX.exe' `
  -ArgumentList '/s /v/qn REBOOT=ReallySuppress' `
  -Wait

# Verify installation
Get-ItemProperty HKLM:\SOFTWARE\VMware,\ Inc.\VMware\ Workstation
```

---

## Phase 2: Network Configuration

### 2.1 Create VMware Virtual Networks

Open VMware Workstation → **Edit** → **Virtual Network Editor** (Run as Administrator)

Create the following networks:

| Network | Type | Subnet | VLAN Purpose |
|---------|------|--------|---------------|
| VMnet1 | Host-only | 192.168.10.0/24 | Management |
| VMnet2 | Host-only | 192.168.20.0/24 | DMZ |
| VMnet3 | Host-only | 192.168.30.0/24 | Database |
| VMnet4 | Host-only | 192.168.40.0/24 | Workstations |
| VMnet5 | Host-only | 192.168.50.0/24 | Monitoring |
| VMnet8 | NAT | 192.168.99.0/24 | WAN/Transit |

```powershell
# Alternatively, use the deployment script
.\scripts\deploy.ps1 -Action setup-networking
```

---

## Phase 3: ESXi Host Deployment

### 3.1 Deploy ESXi Host 1

1. In VMware Workstation, create a new VM:
   - **Type**: VMware ESXi 7.x
   - **Name**: ESXi-Host-01
   - **RAM**: 16 GB
   - **CPU**: 4 cores (enable nested virtualization)
   - **Disk**: 200 GB
   - **Network**: Add adapters for VMnet1, VMnet2, VMnet3

2. Attach ESXi 7.0 ISO and power on

3. Follow ESXi installer:
   ```
   - Accept EULA
   - Select disk for installation
   - Set keyboard layout: US
   - Set root password: [Your secure password]
   - Confirm installation
   ```

4. After reboot, configure management IP:
   - Press **F2** at DCUI
   - **Configure Management Network** → **IPv4 Configuration**
   - Set IP: `192.168.10.10`
   - Netmask: `255.255.255.0`
   - Gateway: `192.168.10.1`

### 3.2 Deploy ESXi Host 2

Repeat above with:
- **Name**: ESXi-Host-02
- **IP**: `192.168.10.11`
- **Network**: Add adapters for VMnet1, VMnet4, VMnet5

### 3.3 Verify ESXi Access

```bash
# Test ESXi management interface
curl -k https://192.168.10.10/ui/
curl -k https://192.168.10.11/ui/
```

Access the ESXi web interface at:
- Host 1: `https://192.168.10.10/ui`
- Host 2: `https://192.168.10.11/ui`

---

## Phase 4: pfSense Deployment

### 4.1 Create pfSense VM

- **Name**: pfSense-Edge
- **OS**: FreeBSD 64-bit
- **RAM**: 2 GB
- **CPU**: 2 cores
- **Disk**: 20 GB
- **Network Adapter 1**: VMnet8 (WAN/NAT)
- **Network Adapter 2**: VMnet1 (LAN/Management)

### 4.2 Install pfSense

1. Attach pfSense 2.7.x ISO
2. Boot and follow installer:
   ```
   - Accept license
   - Install → Continue with default keymap
   - ZFS auto → Proceed → Stripe → select disk → confirm
   - Reboot (remove ISO)
   ```

### 4.3 Initial pfSense Configuration

```
WAN Interface: em0 → DHCP (from VMnet8/NAT)
LAN Interface: em1 → Static: 192.168.10.1/24
```

Access web GUI at `https://192.168.10.1`

Default credentials: `admin` / `pfsense` (change immediately)

See [Configuration.md](Configuration.md) for full pfSense setup.

---

## Phase 5: VM Deployment

### 5.1 Windows Server 2019 (DNS)

- **Name**: WinSrv-DNS-01
- **Host**: ESXi-Host-01
- **RAM**: 4 GB | **CPU**: 2 cores | **Disk**: 60 GB
- **Network**: VMnet1 (VLAN 10 Management)
- **IP**: `192.168.10.20` | **Gateway**: `192.168.10.1`

```powershell
# Install DNS Server Role after OS installation
Install-WindowsFeature DNS -IncludeManagementTools

# Configure primary DNS zone
Add-DnsServerPrimaryZone -Name "vdc.local" -ZoneFile "vdc.local.dns"
Add-DnsServerPrimaryZone -Name "10.168.192.in-addr.arpa" -ZoneFile "reverse.dns"
```

### 5.2 Ubuntu Server (Web Application)

- **Name**: Ubuntu-Web-01
- **Host**: ESXi-Host-01
- **RAM**: 2 GB | **CPU**: 2 cores | **Disk**: 40 GB
- **Network**: VMnet2 (VLAN 20 DMZ)
- **IP**: `192.168.20.10`

```bash
# Post-installation setup
sudo apt update && sudo apt upgrade -y
sudo apt install nginx ufw -y

# Configure UFW (host firewall)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny ssh  # SSH handled by distributed FW policy
sudo ufw enable
```

### 5.3 Ubuntu Server (Database)

- **Name**: Ubuntu-DB-01
- **Host**: ESXi-Host-01
- **RAM**: 4 GB | **CPU**: 2 cores | **Disk**: 80 GB
- **Network**: VMnet3 (VLAN 30 Database)
- **IP**: `192.168.30.10`

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install mysql-server -y
sudo mysql_secure_installation
```

### 5.4 Ubuntu Desktop (Client)

- **Name**: Ubuntu-Desktop-01
- **Host**: ESXi-Host-02
- **RAM**: 4 GB | **CPU**: 2 cores | **Disk**: 40 GB
- **Network**: VMnet4 (VLAN 40 Workstations)
- **IP**: `192.168.40.10` (DHCP)

### 5.5 Suricata IDS/IPS VM

- **Name**: Suricata-IDS-01
- **Host**: ESXi-Host-02
- **RAM**: 4 GB | **CPU**: 4 cores | **Disk**: 100 GB (for PCAP)
- **Network**: VMnet5 (VLAN 50 Monitoring) + Mirror port

```bash
# Install Suricata
sudo add-apt-repository ppa:oisf/suricata-stable
sudo apt update && sudo apt install suricata -y
suricata-update
suricata-update enable-conf /etc/suricata/enable.conf
```

### 5.6 ELK Stack VM

- **Name**: ELK-Stack-01
- **Host**: ESXi-Host-02
- **RAM**: 8 GB | **CPU**: 4 cores | **Disk**: 200 GB
- **Network**: VMnet5 (VLAN 50 Monitoring)
- **IP**: `192.168.50.10`

```bash
# Install Elasticsearch
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt update && sudo apt install elasticsearch logstash kibana -y
```

---

## Phase 6: IDS/IPS Configuration

See [IDS-IPS.md](IDS-IPS.md) for full configuration.

---

## Phase 7: Monitoring Stack

See [Configuration.md](Configuration.md) for Grafana/Prometheus setup.

---

## Verification Checklist

```bash
# Run automated verification
bash scripts/network-test.sh --verify-all

# Expected output:
# [OK] ESXi Host 1 reachable: 192.168.10.10
# [OK] ESXi Host 2 reachable: 192.168.10.11
# [OK] pfSense reachable: 192.168.10.1
# [OK] DNS resolution working: vdc.local
# [OK] VLAN 10 isolated from VLAN 20 (default-deny)
# [OK] Web server reachable on port 443
# [OK] Database isolated from Workstations
# [OK] ELK Stack receiving logs
# [OK] Suricata IDS active
```
