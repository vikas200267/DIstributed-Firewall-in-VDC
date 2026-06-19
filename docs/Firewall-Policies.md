# Firewall Policy Documentation

## Overview

This document describes the complete firewall policy design for the Distributed Firewall VDC project. Policies are organized by network segment and traffic direction.

## Policy Design Principles

1. **Default Deny** — All traffic is denied by default unless explicitly permitted
2. **Least Privilege** — Only minimum required traffic is permitted
3. **Explicit Allow** — Every permitted traffic flow must have a documented rule
4. **Logging** — All deny actions and selected allow actions are logged
5. **Stateful Inspection** — Established/related traffic follows session state

## Rule Numbering Convention

```
[SEGMENT]-[DIRECTION]-[SEQUENCE]
Example: DMZ-IN-001 = DMZ Segment, Inbound, Rule 1

Directions: IN (inbound to segment), OUT (outbound from segment), EW (east-west)
Segments: MGT, DMZ, DB, WS, MON, EDGE
```

---

## 1. Edge Firewall Rules (pfSense)

### Inbound (WAN → LAN)

| Rule ID | Source | Destination | Protocol | Port | Action | Log | Description |
|---------|--------|-------------|----------|------|--------|-----|-------------|
| EDGE-IN-001 | ANY | pfSense WAN | TCP | 443 | BLOCK | Yes | Block HTTPS mgmt from WAN |
| EDGE-IN-002 | ANY | 192.168.20.10 | TCP | 80 | ALLOW | Yes | HTTP to DMZ web server |
| EDGE-IN-003 | ANY | 192.168.20.10 | TCP | 443 | ALLOW | Yes | HTTPS to DMZ web server |
| EDGE-IN-004 | ANY | ANY | TCP | 22 | BLOCK | Yes | Block SSH from internet |
| EDGE-IN-005 | ANY | ANY | TCP | 3389 | BLOCK | Yes | Block RDP from internet |
| EDGE-IN-006 | ANY | ANY | TCP | 445 | BLOCK | Yes | Block SMB from internet |
| EDGE-IN-007 | ANY | ANY | TCP | 1433 | BLOCK | Yes | Block MSSQL from internet |
| EDGE-IN-008 | ANY | ANY | TCP | 3306 | BLOCK | Yes | Block MySQL from internet |
| EDGE-IN-009 | ANY | ANY | ICMP | - | BLOCK | Yes | Block ping from internet |
| EDGE-IN-010 | ANY | ANY | ANY | ANY | BLOCK | Yes | Default deny all inbound |

### Outbound (LAN → WAN)

| Rule ID | Source | Destination | Protocol | Port | Action | Log | Description |
|---------|--------|-------------|----------|------|--------|-----|-------------|
| EDGE-OUT-001 | 192.168.0.0/16 | ANY | TCP | 80 | ALLOW | No | HTTP updates |
| EDGE-OUT-002 | 192.168.0.0/16 | ANY | TCP | 443 | ALLOW | No | HTTPS updates |
| EDGE-OUT-003 | 192.168.0.0/16 | ANY | TCP | 587 | ALLOW | Yes | SMTP submission |
| EDGE-OUT-004 | 192.168.10.20 | ANY | UDP | 53 | ALLOW | No | DNS resolver |
| EDGE-OUT-005 | 192.168.0.0/16 | ANY | UDP | 123 | ALLOW | No | NTP |
| EDGE-OUT-006 | 192.168.0.0/16 | ANY | ANY | ANY | BLOCK | Yes | Default deny outbound |

---

## 2. Management VLAN Policy (VLAN 10)

| Rule ID | Source | Destination | Protocol | Port | Action | Log | Description |
|---------|--------|-------------|----------|------|--------|-----|-------------|
| MGT-IN-001 | 192.168.10.0/24 | 192.168.10.20 | TCP | 53 | ALLOW | No | DNS TCP queries |
| MGT-IN-002 | 192.168.0.0/16 | 192.168.10.20 | UDP | 53 | ALLOW | No | DNS UDP queries |
| MGT-IN-003 | 192.168.10.0/24 | ANY | TCP | 3389 | ALLOW | Yes | RDP within mgmt VLAN |
| MGT-IN-004 | 192.168.10.0/24 | ANY | TCP | 22 | ALLOW | Yes | SSH within mgmt VLAN |
| MGT-IN-005 | ANY | 192.168.10.0/24 | TCP | 22 | BLOCK | Yes | Block SSH from other VLANs |
| MGT-IN-006 | ANY | 192.168.10.0/24 | TCP | 3389 | BLOCK | Yes | Block RDP from other VLANs |
| MGT-IN-007 | ANY | ANY | ANY | ANY | BLOCK | Yes | Default deny to mgmt |

---

## 3. DMZ Policy (VLAN 20)

| Rule ID | Source | Destination | Protocol | Port | Action | Log | Description |
|---------|--------|-------------|----------|------|--------|-----|-------------|
| DMZ-IN-001 | ANY | 192.168.20.0/24 | TCP | 80 | ALLOW | Yes | HTTP inbound |
| DMZ-IN-002 | ANY | 192.168.20.0/24 | TCP | 443 | ALLOW | Yes | HTTPS inbound |
| DMZ-IN-003 | ANY | 192.168.20.0/24 | TCP | 22 | BLOCK | Yes | Block SSH to DMZ |
| DMZ-IN-004 | ANY | 192.168.20.0/24 | ANY | ANY | BLOCK | Yes | Default deny to DMZ |
| DMZ-OUT-001 | 192.168.20.0/24 | 192.168.30.0/24 | TCP | 3306 | ALLOW | Yes | MySQL to DB VLAN |
| DMZ-OUT-002 | 192.168.20.0/24 | 192.168.10.20 | UDP | 53 | ALLOW | No | DNS queries |
| DMZ-OUT-003 | 192.168.20.0/24 | ANY | TCP | 80 | ALLOW | No | HTTP updates |
| DMZ-OUT-004 | 192.168.20.0/24 | ANY | TCP | 443 | ALLOW | No | HTTPS updates |
| DMZ-OUT-005 | 192.168.20.0/24 | 192.168.10.0/24 | ANY | ANY | BLOCK | Yes | Block DMZ to mgmt |
| DMZ-OUT-006 | 192.168.20.0/24 | 192.168.40.0/24 | ANY | ANY | BLOCK | Yes | Block DMZ to workstations |
| DMZ-OUT-007 | 192.168.20.0/24 | ANY | ANY | ANY | BLOCK | Yes | Default deny from DMZ |

---

## 4. Database Policy (VLAN 30)

| Rule ID | Source | Destination | Protocol | Port | Action | Log | Description |
|---------|--------|-------------|----------|------|--------|-----|-------------|
| DB-IN-001 | 192.168.20.0/24 | 192.168.30.0/24 | TCP | 3306 | ALLOW | Yes | MySQL from DMZ |
| DB-IN-002 | 192.168.10.0/24 | 192.168.30.0/24 | TCP | 22 | ALLOW | Yes | SSH from mgmt |
| DB-IN-003 | ANY | 192.168.30.0/24 | TCP | 3306 | BLOCK | Yes | Block DB from non-DMZ |
| DB-IN-004 | 192.168.40.0/24 | 192.168.30.0/24 | ANY | ANY | BLOCK | Yes | Block workstations to DB |
| DB-IN-005 | ANY | 192.168.30.0/24 | ANY | ANY | BLOCK | Yes | Default deny to DB |
| DB-OUT-001 | 192.168.30.0/24 | 192.168.10.20 | UDP | 53 | ALLOW | No | DNS |
| DB-OUT-002 | 192.168.30.0/24 | ANY | TCP | 443 | ALLOW | No | HTTPS updates |
| DB-OUT-003 | 192.168.30.0/24 | ANY | ANY | ANY | BLOCK | Yes | Default deny from DB |

---

## 5. Workstation Policy (VLAN 40)

| Rule ID | Source | Destination | Protocol | Port | Action | Log | Description |
|---------|--------|-------------|----------|------|--------|-----|-------------|
| WS-OUT-001 | 192.168.40.0/24 | ANY | TCP | 80 | ALLOW | No | HTTP browsing |
| WS-OUT-002 | 192.168.40.0/24 | ANY | TCP | 443 | ALLOW | No | HTTPS browsing |
| WS-OUT-003 | 192.168.40.0/24 | 192.168.10.20 | UDP | 53 | ALLOW | No | DNS |
| WS-OUT-004 | 192.168.40.0/24 | 192.168.20.0/24 | TCP | 80 | ALLOW | Yes | HTTP to DMZ |
| WS-OUT-005 | 192.168.40.0/24 | 192.168.20.0/24 | TCP | 443 | ALLOW | Yes | HTTPS to DMZ |
| WS-OUT-006 | 192.168.40.0/24 | 192.168.30.0/24 | ANY | ANY | BLOCK | Yes | Block workstations to DB |
| WS-OUT-007 | 192.168.40.0/24 | 192.168.10.0/24 | TCP | 22 | BLOCK | Yes | Block SSH to mgmt |
| WS-OUT-008 | 192.168.40.0/24 | 192.168.40.0/24 | ANY | ANY | BLOCK | Yes | Block lateral within WS |
| WS-OUT-009 | 192.168.40.0/24 | ANY | ANY | ANY | BLOCK | Yes | Default deny from WS |

---

## 6. Per-VM Distributed Firewall Policies

### Ubuntu-Web-01 (192.168.20.10)

```yaml
vm: Ubuntu-Web-01
ip: 192.168.20.10
vlan: 20
policies:
  inbound:
    - { src: ANY, dst: self, proto: TCP, port: 80, action: ALLOW, log: true }
    - { src: ANY, dst: self, proto: TCP, port: 443, action: ALLOW, log: true }
    - { src: 192.168.10.0/24, dst: self, proto: TCP, port: 22, action: ALLOW, log: true }
    - { src: ANY, dst: self, proto: ANY, port: ANY, action: DENY, log: true }
  outbound:
    - { src: self, dst: 192.168.30.10, proto: TCP, port: 3306, action: ALLOW, log: true }
    - { src: self, dst: 192.168.10.20, proto: UDP, port: 53, action: ALLOW }
    - { src: self, dst: ANY, proto: TCP, port: 443, action: ALLOW }
    - { src: self, dst: ANY, proto: ANY, port: ANY, action: DENY, log: true }
```

### Ubuntu-DB-01 (192.168.30.10)

```yaml
vm: Ubuntu-DB-01
ip: 192.168.30.10
vlan: 30
policies:
  inbound:
    - { src: 192.168.20.0/24, dst: self, proto: TCP, port: 3306, action: ALLOW, log: true }
    - { src: 192.168.10.0/24, dst: self, proto: TCP, port: 22, action: ALLOW, log: true }
    - { src: ANY, dst: self, proto: ANY, port: ANY, action: DENY, log: true }
  outbound:
    - { src: self, dst: 192.168.10.20, proto: UDP, port: 53, action: ALLOW }
    - { src: self, dst: ANY, proto: TCP, port: 443, action: ALLOW }
    - { src: self, dst: ANY, proto: ANY, port: ANY, action: DENY, log: true }
```

---

## 7. Rule Change Management

All firewall rule changes must follow this process:

1. **Request** — Raise GitHub Issue with `firewall-change` label
2. **Review** — Peer review of rule impact
3. **Test** — Test in isolated snapshot environment
4. **Approve** — Project lead approves
5. **Implement** — Apply change via automation script
6. **Verify** — Run automated test suite
7. **Document** — Update this document and CHANGELOG.md
