# Threat Intelligence Integration

## Overview

This document describes how external threat intelligence feeds are integrated into the Distributed Firewall VDC to provide automated, real-time protection against known malicious actors.

## Threat Intelligence Architecture

```
[External Threat Feeds]
        |
        v
[Update Scripts (cron)]
        |
        v
[Local Feed Processing]
        |
    ____|____
   |         |
   v         v
[Suricata] [pfBlockerNG]
 [Rules]    [IP/Domain Blocklists]
```

## Integrated Threat Feeds

| Feed | Type | Update Frequency | URL |
|------|------|-----------------|-----|
| Emerging Threats Open | IDS Rules | Daily | rules.emergingthreats.net |
| AbuseIPDB | IP Reputation | Every 6h | api.abuseipdb.com |
| Feodo Tracker | Botnet C2 IPs | Every 6h | feodotracker.abuse.ch |
| Spamhaus DROP | IP Blocklist | Daily | www.spamhaus.org |
| URLhaus | Malicious URLs | Every 4h | urlhaus-api.abuse.ch |
| MalwareBazaar | Malware Hashes | Hourly | bazaar.abuse.ch |

## AbuseIPDB Integration

### Automatic IP Reputation Check Script

```python
#!/usr/bin/env python3
# threat-feed-updater.py - Updates pfSense blocklist from AbuseIPDB

import json
import os
import requests
from datetime import datetime

ABUSEIPDB_API_KEY = os.environ.get('ABUSEIPDB_KEY', 'YOUR_API_KEY_HERE')
PFSENSE_ALIAS_FILE = '/tmp/abuseipdb-blocklist.txt'
MIN_CONFIDENCE = 75  # Block IPs with >= 75% confidence score

def fetch_abuseipdb_blacklist():
    """Fetch top malicious IPs from AbuseIPDB."""
    url = 'https://api.abuseipdb.com/api/v2/blacklist'
    headers = {
        'Key': ABUSEIPDB_API_KEY,
        'Accept': 'application/json'
    }
    params = {
        'confidenceMinimum': MIN_CONFIDENCE,
        'limit': 10000
    }
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return [entry['ipAddress'] for entry in data.get('data', [])]

def update_blocklist(ips):
    """Write IPs to pfSense alias file."""
    with open(PFSENSE_ALIAS_FILE, 'w') as f:
        f.write(f'# AbuseIPDB Blocklist - Updated: {datetime.utcnow().isoformat()}\n')
        f.write(f'# Entries: {len(ips)}\n')
        for ip in ips:
            f.write(f'{ip}\n')
    print(f'[OK] Blocklist updated: {len(ips)} IPs written to {PFSENSE_ALIAS_FILE}')

if __name__ == '__main__':
    ips = fetch_abuseipdb_blacklist()
    update_blocklist(ips)
```

## Feodo Tracker (Botnet C2) Integration

```bash
#!/bin/bash
# Update Feodo Tracker botnet C2 blocklist

FEODO_URL="https://feodotracker.abuse.ch/downloads/ipblocklist.txt"
OUTPUT_FILE="/etc/pf/feodo-c2-blocklist.txt"

curl -s "$FEODO_URL" | grep -v '^#' | grep -v '^$' > "$OUTPUT_FILE"
COUNT=$(wc -l < "$OUTPUT_FILE")
echo "[OK] Feodo Tracker: $COUNT C2 IPs updated at $(date)"

# Reload pfSense alias if running on pfSense
# pfctl -t feodo_c2 -T replace -f "$OUTPUT_FILE"
```

## GeoIP Blocking Configuration

pfSense pfBlockerNG GeoIP blocking configuration:

```
Countries to BLOCK (inbound):
- CN (China) - High attack volume
- RU (Russia) - High attack volume
- KP (North Korea) - Nation-state threats
- IR (Iran) - Nation-state threats

Countries to ALLOW:
- GB (United Kingdom) - Lab location
- US (United States) - Update servers
- IE (Ireland) - Cloud services
```

## IOC Matching with Suricata

Suricata custom rules for IOC matching:

```bash
# /etc/suricata/rules/vdc-ioc.rules
# Known malicious IP addresses (updated automatically)

alert ip [203.0.113.10, 203.0.113.11, 198.51.100.50] any -> $HOME_NET any \
  (msg:"VDC TI Known Malicious IP"; classtype:trojan-activity; sid:9001001; rev:1;)

# Known malicious domains (DNS)
alert dns $HOME_NET any -> any 53 \
  (msg:"VDC TI Malicious Domain Query"; dns.query; \
   content:"malware-domain.example"; nocase; \
   classtype:trojan-activity; sid:9001002; rev:1;)

# Known C2 ports
alert tcp $HOME_NET any -> $EXTERNAL_NET [4444,4445,5555,6666,8888] \
  (msg:"VDC TI Possible C2 Outbound - Common RAT Port"; \
   classtype:trojan-activity; sid:9001003; rev:1;)
```

## Automated Update Schedule

```bash
# /etc/cron.d/vdc-threat-intel
# Threat Intelligence Update Schedule

# Update Suricata rules daily at 03:00
0 3 * * * root suricata-update && systemctl reload suricata

# Update AbuseIPDB blocklist every 6 hours
0 */6 * * * root python3 /opt/vdc/scripts/threat-feed-updater.py

# Update Feodo Tracker every 6 hours
30 */6 * * * root bash /opt/vdc/scripts/update-feodo.sh

# Update Spamhaus DROP list daily
0 4 * * * root curl -s https://www.spamhaus.org/drop/drop.txt > /etc/pf/spamhaus-drop.txt
```

## Sample Threat Intelligence Alerts

```json
{
  "timestamp": "2025-03-15T15:30:00Z",
  "alert_type": "threat_intelligence",
  "feed": "AbuseIPDB",
  "src_ip": "45.33.32.156",
  "confidence_score": 97,
  "abuse_categories": ["Port Scan", "SSH Brute Force"],
  "action": "BLOCKED",
  "rule": "pfBlockerNG_AbuseIPDB",
  "destination": "192.168.20.10:443"
}

{
  "timestamp": "2025-03-15T16:45:00Z",
  "alert_type": "threat_intelligence",
  "feed": "Feodo Tracker",
  "dst_ip": "185.220.101.45",
  "malware_family": "Emotet",
  "action": "BLOCKED",
  "rule": "pfBlockerNG_FeodoC2",
  "source": "192.168.40.15"
}
```
