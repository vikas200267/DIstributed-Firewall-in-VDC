# Project Screenshots

This folder is intended to hold screenshots of the working Distributed Firewall VDC lab environment. 

For the final academic submission, please replace these placeholder image filenames with your actual screenshots showing the working environment.

## Recommended Screenshots to Capture

### 1. Infrastructure (VMware)
- `esxi-host-summary.png`: ESXi host dashboard showing resources and networking.
- `vswitch-topology.png`: VMware virtual switch topology showing the VLAN segments.
- `pfsense-dashboard.png`: pfSense main dashboard showing interfaces and traffic.

### 2. Firewall Policies
- `pfsense-rules-dmz.png`: pfSense firewall rules configured for the DMZ interface.
- `nftables-rules.png`: Output of `nft list ruleset` on one of the Ubuntu VMs showing the distributed host-based rules.
- `policy-generator.png`: Terminal output running the `firewall-policy-generator.py` script.

### 3. Monitoring & IDS
- `suricata-alerts.png`: Suricata `fast.log` or `eve.json` output showing a detected attack.
- `kibana-dashboard.png`: ELK Stack/Kibana dashboard showing aggregated firewall logs.
- `grafana-metrics.png`: Grafana dashboard showing host performance and network traffic.
- `prometheus-targets.png`: Prometheus targets page showing all VDC nodes are UP.

### 4. Security Testing
- `test-script-execution.png`: Terminal output running `network-test.sh` showing PASS/FAIL results.
- `nmap-scan-blocked.png`: Nmap scan from Workstation VM to Database VM showing all ports filtered (Default Deny).
- `lateral-movement-blocked.png`: Ping attempt between DMZ Web Server and Database Server showing destination unreachable.

---

## Inserting Screenshots into Documentation

You can reference these screenshots in your main markdown files using the following syntax:

```markdown
![pfSense Dashboard](../architecture/screenshots/pfsense-dashboard.png)
```

## Adding Screenshots to GitHub

1. Take the screenshots using a tool like Snipping Tool (Windows) or Flameshot (Linux).
2. Save them in this directory (`architecture/screenshots/`) with the suggested filenames.
3. Commit and push them to your repository:
   ```bash
   git add architecture/screenshots/
   git commit -m "Add project screenshots"
   git push origin main
   ```
