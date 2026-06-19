# Project Objectives

## Primary Objectives

This project has the following primary objectives, each measurable against defined success criteria.

---

### Objective 1: Virtual Data Center Deployment

**Description**: Design and deploy a functional Virtual Data Center (VDC) using VMware technology, comprising multiple ESXi hypervisors, virtual switches, and a diverse set of virtual machines representing different workload types.

**Success Criteria**:
- [ ] Two ESXi 7.0 hosts deployed and accessible via vSphere
- [ ] All VMs deployed and operational (DNS, Web, DB, Client, Monitoring)
- [ ] Virtual switches configured with appropriate port groups
- [ ] Network connectivity verified between all intended paths
- [ ] VLAN segmentation operational (6 VLANs)

**Priority**: High | **Status**: ✅ Complete

---

### Objective 2: Distributed Firewall Implementation

**Description**: Implement a distributed firewall model that enforces security policies at the virtual machine level, simulating VMware NSX-style microsegmentation.

**Success Criteria**:
- [ ] Per-VM firewall policies defined and operational
- [ ] Firewall enforcement at vNIC/hypervisor level confirmed
- [ ] Policy management centralized and documented
- [ ] Rule evaluation order verified correct

**Priority**: High | **Status**: ✅ Complete

---

### Objective 3: VLAN-Based Microsegmentation

**Description**: Segment the VDC network into isolated zones using VLANs, with inter-zone communication controlled by firewall policies.

**Success Criteria**:
- [ ] 6 VLANs configured and isolated at Layer 2
- [ ] Inter-VLAN routing through pfSense only
- [ ] Default-deny policy between segments
- [ ] Permitted inter-segment flows documented and tested

**Priority**: High | **Status**: ✅ Complete

---

### Objective 4: North-South Traffic Protection

**Description**: Deploy pfSense as the edge firewall to control all traffic entering and leaving the VDC.

**Success Criteria**:
- [ ] pfSense deployed and routing internet traffic
- [ ] NAT/PAT configured for internal VMs
- [ ] Ingress filtering rules operational
- [ ] Egress filtering rules operational
- [ ] Firewall logs confirming block/allow decisions

**Priority**: High | **Status**: ✅ Complete

---

### Objective 5: East-West Traffic Protection

**Description**: Implement controls that filter traffic flowing between VMs within the same VDC, using distributed firewall policies.

**Success Criteria**:
- [ ] Inter-VM firewall rules operational
- [ ] Lateral movement between segments blocked
- [ ] Evidence of east-west filtering in firewall logs
- [ ] Wireshark captures confirming blocked lateral traffic

**Priority**: High | **Status**: ✅ Complete

---

### Objective 6: Intrusion Detection System (IDS)

**Description**: Deploy Suricata/Snort as an IDS sensor to detect known attack signatures and anomalous traffic patterns.

**Success Criteria**:
- [ ] Suricata deployed and receiving mirrored traffic
- [ ] Emerging Threats ruleset operational
- [ ] Custom rules for VDC-specific traffic created
- [ ] Alerts generated for simulated attacks
- [ ] Alert output forwarded to ELK Stack

**Priority**: High | **Status**: ✅ Complete

---

### Objective 7: Intrusion Prevention System (IPS)

**Description**: Configure the IDS in inline mode to actively block detected threats in real-time.

**Success Criteria**:
- [ ] Suricata operating in IPS (inline AF_PACKET) mode
- [ ] Drop rules operational for high-confidence signatures
- [ ] IPS blocking verified via test attacks
- [ ] Performance impact of IPS mode measured

**Priority**: Medium | **Status**: ✅ Complete

---

### Objective 8: Threat Intelligence Integration

**Description**: Integrate external threat intelligence feeds to automatically update firewall and IDS rules with known malicious indicators.

**Success Criteria**:
- [ ] Emerging Threats ruleset auto-updating
- [ ] AbuseIPDB IP reputation integration operational
- [ ] pfBlockerNG GeoIP blocking configured
- [ ] IOC matching operational for known-bad IPs and domains
- [ ] Automated rule update schedule configured

**Priority**: Medium | **Status**: ✅ Complete

---

### Objective 9: Centralized Logging with ELK Stack

**Description**: Deploy Elasticsearch, Logstash, and Kibana to aggregate, parse, and visualize logs from all VDC components.

**Success Criteria**:
- [ ] ELK Stack 8.x deployed and operational
- [ ] Log sources: pfSense, Suricata, Windows Event Log, Ubuntu syslog
- [ ] Logstash parsing pipelines operational
- [ ] Kibana dashboards configured
- [ ] Alert rules in Kibana operational

**Priority**: High | **Status**: ✅ Complete

---

### Objective 10: Performance Evaluation

**Description**: Measure the performance impact of the distributed firewall implementation compared to an unsecured baseline.

**Success Criteria**:
- [ ] Baseline throughput measured (no firewall)
- [ ] Firewall throughput measured (with all rules)
- [ ] Latency impact quantified
- [ ] CPU utilization measured on ESXi hosts
- [ ] Memory utilization measured
- [ ] Results documented with statistical analysis

**Priority**: Medium | **Status**: ✅ Complete

---

### Objective 11: Security Testing

**Description**: Conduct a comprehensive security testing programme to validate the effectiveness of all implemented controls.

**Success Criteria**:
- [ ] Penetration testing scenarios executed
- [ ] All firewall rules tested (positive and negative)
- [ ] IDS detection verified with simulated attacks
- [ ] IPS prevention verified with simulated attacks
- [ ] Threat intelligence blocking verified
- [ ] All test results documented

**Priority**: High | **Status**: ✅ Complete

---

### Objective 12: Automation and Repeatability

**Description**: Develop automation scripts to enable rapid, repeatable deployment of the VDC configuration.

**Success Criteria**:
- [ ] PowerShell deployment script operational
- [ ] Bash firewall configuration script operational
- [ ] Python monitoring agent operational
- [ ] Backup/restore scripts operational
- [ ] All scripts documented and commented

**Priority**: Medium | **Status**: ✅ Complete

---

## Secondary Objectives

| Objective | Description | Status |
|-----------|-------------|--------|
| S1 | Document all configurations for reproducibility | ✅ |
| S2 | Produce academic report meeting university standards | ✅ |
| S3 | Create GitHub repository as professional portfolio piece | ✅ |
| S4 | Cost analysis of the solution | ✅ |
| S5 | Risk analysis and mitigation | ✅ |
| S6 | Future enhancement roadmap | ✅ |
