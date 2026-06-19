# Future Work

## Overview

This document outlines planned enhancements and extensions to the Distributed Firewall VDC project, organized by priority and complexity.

## Phase 3: NSX-T Integration (High Priority)

### VMware NSX-T Deployment

**Rationale**: The current implementation simulates distributed firewall behavior using pfSense and host-based nftables. VMware NSX-T provides true hypervisor-kernel-level enforcement, offering significantly stronger security guarantees.

**Planned Work**:
- Deploy NSX-T Manager as a VM
- Configure NSX-T transport zones and segments
- Migrate VMs to NSX-T logical switches
- Implement NSX-T Distributed Firewall rules
- Configure NSX-T load balancer for web tier
- Implement microsegmentation using NSX-T Security Groups

**Estimated Effort**: 4-6 weeks

**Dependencies**: VMware NSX-T license (requires vSphere Enterprise Plus)

### NSX-T Security Groups

```yaml
# Planned NSX-T Security Group definitions
security_groups:
  - name: SG-WebServers
    criteria:
      - type: VM_TAG
        tag: role=web
  - name: SG-DatabaseServers
    criteria:
      - type: VM_TAG
        tag: role=database
  - name: SG-Management
    criteria:
      - type: VM_TAG
        tag: role=management
```

## Phase 4: Zero Trust Architecture

### ZTNA Implementation

**Rationale**: Zero Trust Architecture takes microsegmentation further by requiring continuous verification of user identity and device health for every access request.

**Planned Components**:
- Identity Provider (IdP) - FreeIPA or Azure AD
- Zero Trust proxy (e.g., Teleport)
- Device trust verification
- Continuous authorization
- Conditional access policies

### Multi-Factor Authentication

- Implement TOTP-based MFA for all administrative access
- Integrate with Teleport for SSH certificate-based access
- Yubikey hardware token for admin accounts

## Phase 4: AI/ML Threat Detection

### Behavioral Anomaly Detection

**Rationale**: Suricata's signature-based detection cannot identify novel attacks. ML-based anomaly detection would provide coverage for unknown threats.

**Planned Approach**:
```python
# Planned: ML anomaly detector using scikit-learn
# Features extracted from netflow/eve.json:
# - Bytes per flow
# - Packets per flow
# - Flow duration
# - Port entropy
# - IP reputation score

from sklearn.ensemble import IsolationForest
import pandas as pd

clf = IsolationForest(contamination=0.01, random_state=42)
# Train on baseline 'normal' traffic
clf.fit(normal_traffic_features)

# Detect anomalies in new traffic
anomaly_scores = clf.decision_function(new_traffic_features)
```

**Planned Tools**: Zeek (Bro), scikit-learn, Apache Kafka for streaming

## Phase 5: SOAR Integration

### Automated Incident Response

**Rationale**: Manual incident response is slow. SOAR automation can contain threats in seconds.

**Planned Stack**:
- **TheHive** - Incident case management
- **Cortex** - Automated analysis and response
- **MISP** - Threat intelligence sharing

**Example Playbook** (planned):
1. Suricata detects lateral movement
2. ELK alert triggers → TheHive creates case
3. Cortex analyzer checks IP against threat feeds
4. If confirmed malicious: automatically add IP to pfSense block list
5. Isolate affected VM (remove from network segment)
6. Notify SOC via Slack/email
7. Generate forensic evidence package

## Phase 6: Kubernetes Security

### Container Microsegmentation

**Rationale**: Modern workloads run in containers. Security must extend to Kubernetes pods.

**Planned Implementation**:
- Deploy Kubernetes cluster (k3s or kubeadm)
- Implement Cilium CNI with eBPF-based network policies
- Define Kubernetes NetworkPolicy objects
- Integrate with NSX-T for consistent policy management
- Container image scanning with Trivy

## Phase 7: Hybrid Cloud Extension

**Planned**:
- AWS VPC peering with VDC
- Azure ExpressRoute simulation
- Cloud security group alignment with on-prem policies
- Unified policy management across on-prem and cloud

## Research Areas

| Area | Research Question |
|------|------------------|
| Quantum-safe cryptography | How will post-quantum algorithms affect VPN/TLS in VDC? |
| eBPF-based firewalling | Can eBPF replace nftables for lower overhead? |
| Software-defined perimeter | How does SDP compare to VLAN-based microsegmentation? |
| 5G network slicing | Can VDC concepts apply to 5G network slice security? |
