# Requirements Specification

## 1. Functional Requirements

### FR-01: Virtual Infrastructure

| ID | Requirement | Priority | Verification |
|----|------------|---------|---------------|
| FR-01.1 | The system SHALL deploy minimum two ESXi 7.0 hypervisor hosts | Must Have | Inspection |
| FR-01.2 | The system SHALL support a minimum of 8 concurrent virtual machines | Must Have | Test |
| FR-01.3 | The system SHALL implement virtual switches for VM connectivity | Must Have | Inspection |
| FR-01.4 | The system SHALL support VLAN tagging (802.1Q) across virtual switches | Must Have | Test |
| FR-01.5 | The system SHALL provide DNS resolution for all internal VMs | Must Have | Test |
| FR-01.6 | The system SHALL provide internet access via NAT for designated VMs | Should Have | Test |

### FR-02: Distributed Firewall

| ID | Requirement | Priority | Verification |
|----|------------|---------|---------------|
| FR-02.1 | The system SHALL enforce firewall policies at the virtual NIC level | Must Have | Test |
| FR-02.2 | The system SHALL support stateful TCP/UDP connection tracking | Must Have | Test |
| FR-02.3 | The system SHALL filter east-west traffic between VMs | Must Have | Test |
| FR-02.4 | The system SHALL filter north-south traffic at the VDC perimeter | Must Have | Test |
| FR-02.5 | The system SHALL implement default-deny between network segments | Must Have | Test |
| FR-02.6 | The system SHALL log all firewall decisions (allow and deny) | Must Have | Inspection |
| FR-02.7 | The system SHALL support rule-based policies with priority ordering | Must Have | Test |
| FR-02.8 | The system SHALL support ICMP, TCP, UDP, and any protocol filtering | Must Have | Test |

### FR-03: Network Segmentation

| ID | Requirement | Priority | Verification |
|----|------------|---------|---------------|
| FR-03.1 | The system SHALL implement minimum 5 isolated VLAN segments | Must Have | Inspection |
| FR-03.2 | The system SHALL route inter-VLAN traffic exclusively through pfSense | Must Have | Test |
| FR-03.3 | The system SHALL isolate database VMs in a dedicated segment | Must Have | Test |
| FR-03.4 | The system SHALL isolate web/DMZ VMs in a dedicated segment | Must Have | Test |
| FR-03.5 | The system SHALL isolate monitoring infrastructure in a dedicated segment | Should Have | Inspection |

### FR-04: IDS/IPS

| ID | Requirement | Priority | Verification |
|----|------------|---------|---------------|
| FR-04.1 | The system SHALL detect port scan activity | Must Have | Test |
| FR-04.2 | The system SHALL detect SQL injection attempts | Must Have | Test |
| FR-04.3 | The system SHALL detect brute-force authentication attempts | Must Have | Test |
| FR-04.4 | The system SHALL detect known malware command-and-control traffic | Should Have | Test |
| FR-04.5 | The system SHALL generate alerts for all detections | Must Have | Inspection |
| FR-04.6 | The IPS SHALL block traffic matching drop signatures | Must Have | Test |
| FR-04.7 | The system SHALL forward IDS alerts to the centralized logging platform | Must Have | Test |

### FR-05: Threat Intelligence

| ID | Requirement | Priority | Verification |
|----|------------|---------|---------------|
| FR-05.1 | The system SHALL integrate with minimum one external threat intelligence feed | Should Have | Inspection |
| FR-05.2 | The system SHALL automatically update IDS rules from Emerging Threats | Should Have | Test |
| FR-05.3 | The system SHALL block traffic to/from known-malicious IP addresses | Should Have | Test |
| FR-05.4 | The system SHALL support GeoIP-based access control | Could Have | Inspection |

### FR-06: Monitoring and Logging

| ID | Requirement | Priority | Verification |
|----|------------|---------|---------------|
| FR-06.1 | The system SHALL aggregate logs from all VDC components centrally | Must Have | Inspection |
| FR-06.2 | The system SHALL provide real-time dashboards for network metrics | Should Have | Demonstration |
| FR-06.3 | The system SHALL retain logs for minimum 30 days | Should Have | Inspection |
| FR-06.4 | The system SHALL generate automated alerts for security events | Should Have | Test |
| FR-06.5 | The system SHALL monitor CPU, memory, and network utilization of all VMs | Should Have | Demonstration |

## 2. Non-Functional Requirements

### NFR-01: Performance

| ID | Requirement | Target |
|----|------------|--------|
| NFR-01.1 | Firewall throughput SHALL NOT degrade below 90% of baseline | ≥ 90% baseline |
| NFR-01.2 | East-west firewall latency overhead SHALL NOT exceed 5ms | < 5ms |
| NFR-01.3 | IDS SHALL process traffic at line rate without dropping packets | 0% packet loss |
| NFR-01.4 | Monitoring system SHALL have maximum 60 second metric collection interval | ≤ 60s |

### NFR-02: Availability

| ID | Requirement | Target |
|----|------------|--------|
| NFR-02.1 | Firewall service SHALL be available for all lab sessions | 99% uptime |
| NFR-02.2 | Logging service SHALL be available for all lab sessions | 99% uptime |
| NFR-02.3 | System SHALL recover from power failure within 10 minutes | < 10 min |

### NFR-03: Security

| ID | Requirement |
|----|-------------|
| NFR-03.1 | All management interfaces SHALL require authentication |
| NFR-03.2 | All configuration changes SHALL be logged |
| NFR-03.3 | Default credentials SHALL be changed on all systems |
| NFR-03.4 | SSH SHALL be the only remote access method for Linux VMs |

### NFR-04: Maintainability

| ID | Requirement |
|----|-------------|
| NFR-04.1 | All scripts SHALL include inline comments |
| NFR-04.2 | All configuration files SHALL be version controlled |
| NFR-04.3 | Deployment SHALL be reproducible using provided scripts |
| NFR-04.4 | Backup/restore procedures SHALL be documented |

## 3. Hardware Requirements

| Component | Specification | Quantity |
|-----------|--------------|----------|
| Host CPU | Intel i7/i9 or AMD Ryzen 9 with VT-x/AMD-V | 1 |
| RAM | 64 GB DDR4 minimum | 1 |
| Storage | 1 TB NVMe SSD | 1 |
| Network | Gigabit Ethernet NIC | 2 |
| Display | 1080p monitor | 1 |

## 4. Software Requirements

| Software | Version | License |
|----------|---------|----------|
| VMware Workstation | 17.x | Commercial |
| VMware ESXi | 7.0 U3 | Free license |
| pfSense | 2.7.x | Apache 2.0 |
| Windows Server | 2019 | MSDN/Academic |
| Ubuntu Server | 22.04 LTS | Free |
| Suricata | 6.x | GPLv2 |
| ELK Stack | 8.x | Elastic License |
| Grafana | 10.x | AGPLv3 |
| Prometheus | 2.x | Apache 2.0 |
