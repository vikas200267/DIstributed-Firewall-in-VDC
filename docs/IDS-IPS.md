# IDS/IPS Configuration Guide

## Overview

This project implements both Intrusion Detection System (IDS) and Intrusion Prevention System (IPS) functionality using **Suricata 6.x** deployed on the monitoring VLAN. Suricata receives a mirrored copy of all east-west and north-south traffic for inspection.

## Architecture

```
                    ┌─────────────────────────────────┐
                    │         VDC Network              │
                    │                                  │
  [All VM Traffic]  │   vSwitch (with SPAN port)       │
       │            │         │                        │
       │            │         │ Mirror copy of          │
       │            │         │ all traffic             │
       ▼            │         ▼                        │
  Normal path ──────│──► [Suricata VM]                 │
                    │    eth0: Management              │
                    │    eth1: SPAN/Mirror input       │
                    │    Mode: IDS (passive)           │
                    │       or IPS (inline)            │
                    └─────────────────────────────────┘
```

## Suricata Installation

```bash
#!/bin/bash
# Install Suricata on Ubuntu 22.04

# Add Suricata PPA
sudo add-apt-repository ppa:oisf/suricata-stable -y
sudo apt update

# Install Suricata
sudo apt install suricata suricata-update -y

# Verify installation
suricata --build-info

# Update rules
sudo suricata-update

# Enable Emerging Threats Open rules
sudo suricata-update enable-source et/open

# Update and download rules
sudo suricata-update
```

## IDS Mode Configuration

```yaml
# /etc/suricata/suricata.yaml - Key sections

%YAML 1.1
---

# Suricata version: 6.0.x

# Network interface in AF_PACKET mode (IDS - passive)
af-packet:
  - interface: eth1
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    tpacket-v3: yes

# HOME_NET definition
vars:
  address-groups:
    HOME_NET: "[192.168.0.0/16]"
    EXTERNAL_NET: "!$HOME_NET"
    HTTP_SERVERS: "192.168.20.0/24"
    SMTP_SERVERS: "192.168.10.0/24"
    SQL_SERVERS: "192.168.30.0/24"
    DNS_SERVERS: "[192.168.10.20]"
    TELNET_SERVERS: "$HOME_NET"
    AIM_SERVERS: "$EXTERNAL_NET"
    DC_SERVERS: "$HOME_NET"
    DNP3_SERVER: "$HOME_NET"
    DNP3_CLIENT: "$HOME_NET"
    MODBUS_CLIENT: "$HOME_NET"
    MODBUS_SERVER: "$HOME_NET"
    ENIP_CLIENT: "$HOME_NET"
    ENIP_SERVER: "$HOME_NET"
  port-groups:
    HTTP_PORTS: "80"
    SHELLCODE_PORTS: "0"
    ORACLE_PORTS: 1521
    SSH_PORTS: 22
    DNP3_PORTS: 20000
    MODBUS_PORTS: 502
    FILE_DATA_PORTS: "[$HTTP_PORTS,110,143]"
    FTP_PORTS: 21
    GENEVE_PORTS: 6081
    VXLAN_PORTS: 4789
    TEREDO_PORTS: 3544

# Output configuration
outputs:
  - fast:
      enabled: yes
      filename: fast.log
      append: yes

  - eve-log:
      enabled: yes
      filename: eve.json
      types:
        - alert:
            payload: yes
            payload-buffer-size: 4kb
            payload-printable: yes
            packet: yes
            metadata: no
            http-body: yes
            http-body-printable: yes
            tagged-packets: yes
        - http:
            extended: yes
        - dns:
            version: 2
        - tls:
            extended: yes
        - files:
            force-magic: no
        - smtp: {}
        - ftp
        - rdp
        - nfs
        - smb
        - tftp
        - ikev2
        - krb5
        - quic
        - dhcp:
            enabled: yes
            extended: yes
        - ssh
        - flow
        - netflow

# Logging configuration
logging:
  default-log-level: notice
  outputs:
    - console:
        enabled: yes
    - file:
        enabled: yes
        level: info
        filename: /var/log/suricata/suricata.log
```

## IPS Mode Configuration

```bash
# Switch Suricata to IPS (inline) mode using NFQUEUE

# Configure iptables to redirect traffic to Suricata
sudo iptables -I FORWARD -j NFQUEUE --queue-num 0
sudo iptables -I INPUT -j NFQUEUE --queue-num 0
sudo iptables -I OUTPUT -j NFQUEUE --queue-num 0

# Save iptables rules
sudo iptables-save > /etc/iptables/rules.v4
```

```yaml
# IPS mode in suricata.yaml
nfq:
  mode: repeat
  repeat-mark: 1
  repeat-mask: 1
  route-queue: 2
  batchcount: 20
  fail-open: yes

# Run Suricata in IPS mode
# sudo suricata -c /etc/suricata/suricata.yaml -q 0
```

## Custom Rules

```bash
# /etc/suricata/rules/local.rules
# Custom rules for VDC east-west traffic monitoring

# Detect port scan (Nmap-style)
alert tcp any any -> $HOME_NET any (msg:"ET SCAN Nmap TCP SYN Scan"; flags:S,12; threshold: type threshold, track by_src, count 20, seconds 10; sid:9000001; rev:1;)

# Detect ICMP flood
alert icmp any any -> $HOME_NET any (msg:"VDC ICMP Flood Detected"; threshold: type threshold, track by_src, count 100, seconds 5; sid:9000002; rev:1;)

# Detect SSH brute force
alert tcp any any -> $SSH_SERVERS 22 (msg:"VDC SSH Brute Force Attempt"; flow:to_server; threshold: type threshold, track by_src, count 5, seconds 60; sid:9000003; rev:1;)

# Detect east-west lateral movement (workstation to DB direct)
alert tcp 192.168.40.0/24 any -> 192.168.30.0/24 3306 (msg:"VDC Lateral Movement - WS to DB MySQL"; flow:to_server,established; sid:9000004; rev:1;)

# Detect DNS tunneling
alert dns any any -> any 53 (msg:"VDC Possible DNS Tunneling"; dns.query; content:"."; byte_test:1,>,50,0,relative; threshold: type threshold, track by_src, count 30, seconds 10; sid:9000005; rev:1;)

# Block SQL injection attempt (IPS rule with drop action)
drop http $EXTERNAL_NET any -> $HTTP_SERVERS any (msg:"VDC SQL Injection Attempt"; http.uri; content:"SELECT"; nocase; content:"FROM"; nocase; within:100; sid:9000006; rev:1;)

# Detect SMB lateral movement
alert tcp $HOME_NET any -> $HOME_NET 445 (msg:"VDC SMB East-West Lateral Movement"; flow:to_server; sid:9000007; rev:1;)

# Detect Mimikatz-style LSASS access pattern
alert tcp $HOME_NET any -> $HOME_NET any (msg:"VDC Possible Credential Dumping"; flow:to_server; content:"|00 00 00 00 00 00 00 00|"; rawbytes; sid:9000008; rev:1;)
```

## Sample IDS Alerts

```json
{"timestamp":"2025-03-15T14:23:01.456781+0000","flow_id":1234567890,"in_iface":"eth1","event_type":"alert","src_ip":"192.168.40.15","src_port":54321,"dest_ip":"192.168.20.10","dest_port":80,"proto":"TCP","alert":{"action":"allowed","gid":1,"signature_id":2019236,"rev":3,"signature":"ET SCAN Nmap Scripting Engine User-Agent Detected","category":"Web Application Attack","severity":1},"http":{"hostname":"192.168.20.10","url":"/","http_user_agent":"Mozilla/5.0 (compatible; Nmap Scripting Engine)","http_method":"GET","protocol":"HTTP/1.1","length":0}}

{"timestamp":"2025-03-15T14:25:33.123456+0000","flow_id":9876543210,"in_iface":"eth1","event_type":"alert","src_ip":"192.168.40.15","src_port":12345,"dest_ip":"192.168.30.10","dest_port":3306,"proto":"TCP","alert":{"action":"allowed","gid":1,"signature_id":9000004,"rev":1,"signature":"VDC Lateral Movement - WS to DB MySQL","category":"Policy Violation","severity":2}}

{"timestamp":"2025-03-15T14:28:11.789012+0000","flow_id":1111111111,"in_iface":"eth1","event_type":"alert","src_ip":"203.0.113.45","src_port":44321,"dest_ip":"192.168.20.10","dest_port":80,"proto":"TCP","alert":{"action":"dropped","gid":1,"signature_id":9000006,"rev":1,"signature":"VDC SQL Injection Attempt","category":"Web Application Attack","severity":1},"http":{"url":"/search?q=1' OR 1=1--","http_method":"GET"}}
```

## Monitoring Suricata

```bash
# Check Suricata status
sudo systemctl status suricata

# View alerts in real-time
sudo tail -f /var/log/suricata/fast.log

# Count alerts by signature
cat /var/log/suricata/fast.log | awk '{print $NF}' | sort | uniq -c | sort -rn | head -20

# View EVE JSON log
jq '.alert.signature' /var/log/suricata/eve.json | sort | uniq -c | sort -rn

# Suricata statistics
sudo suricatasc -c stats 2>/dev/null
```

## Performance Tuning

```yaml
# Tune Suricata for high-throughput environments
detect:
  profile: high
  custom-values:
    toclient-groups: 20
    toserver-groups: 20
  sgh-mpm-context: auto
  inspection-recursion-limit: 3000

# Packet acquisition tuning
max-pending-packets: 65536
runmode: workers

# Memory usage
host-memory-use:
  memcap: 2gb

defrag:
  memcap: 128mb
  hash-size: 65536
  trackers: 65535
  max-frags: 65535
  prealloc: yes
  timeout: 60
```
