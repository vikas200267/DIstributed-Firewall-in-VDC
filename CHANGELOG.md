# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- VMware NSX-T real deployment integration
- AI-powered anomaly detection module
- Kubernetes network policy extension

## [2.0.0] - 2025-04-15

### Added
- Full IPS (Intrusion Prevention System) mode with Suricata inline blocking
- Threat Intelligence automation with AbuseIPDB API integration
- GeoIP blocking via pfSense pfBlockerNG
- Grafana dashboards for real-time firewall metrics
- Automated firewall policy generator script
- Comprehensive performance benchmarking suite
- ELK Stack 8.x deployment configuration
- Prometheus + AlertManager integration

### Changed
- Upgraded Suricata from 5.x to 6.x for improved performance
- Refactored firewall policy YAML schema for better extensibility
- Improved log-analyzer.py with JSON output support
- Updated ESXi host configurations for VLAN 50 (Monitoring)

### Fixed
- Resolved DNS resolution failures in VLAN 30 (Database segment)
- Fixed syslog forwarding configuration for Ubuntu VMs
- Corrected pfSense NAT rule ordering issue

## [1.5.0] - 2025-02-20

### Added
- IDS (Intrusion Detection System) deployment with Snort 3.x
- Custom Snort rules for east-west traffic patterns
- Centralized syslog server (rsyslog) configuration
- VM health monitoring script (vm-health.py)
- Network testing automation (network-test.sh)
- Backup and restore configuration scripts

### Changed
- Migrated from single ESXi host to dual-host architecture
- Expanded VLAN segmentation from 3 to 6 VLANs
- Improved microsegmentation policies

### Fixed
- Resolved inter-VLAN routing issue between VLAN 20 and VLAN 30
- Fixed Ubuntu UFW rules conflicting with distributed firewall policies

## [1.0.0] - 2024-11-10

### Added
- Initial Virtual Data Center deployment
- VMware ESXi 7.0 host configuration
- pfSense firewall deployment and basic rules
- Windows Server 2019 DNS configuration
- Ubuntu Server and Desktop VM deployment
- Basic VLAN segmentation (VLANs 10, 20, 30)
- Virtual Switch configuration
- Basic firewall policies (allow/deny rules)
- Initial project documentation
- Architecture diagrams

## [0.1.0] - 2024-09-01

### Added
- Project initialization
- Repository structure
- Initial README and documentation skeleton
- Project proposal document
