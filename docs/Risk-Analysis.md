# Risk Analysis

## Overview

This document presents a formal risk analysis for the Distributed Firewall VDC project, identifying potential risks, assessing their likelihood and impact, and defining mitigation strategies.

## Risk Methodology

Risks are assessed using a 5x5 matrix:
- **Likelihood**: 1 (Very Low) to 5 (Very High)
- **Impact**: 1 (Negligible) to 5 (Critical)
- **Risk Score**: Likelihood × Impact (1-25)
- **Rating**: Low (1-6), Medium (7-12), High (13-19), Critical (20-25)

## Risk Matrix

| Risk ID | Description | Likelihood | Impact | Score | Rating | Mitigation |
|---------|-------------|-----------|--------|-------|--------|------------|
| R-001 | Hardware failure during testing | 2 | 4 | 8 | Medium | Regular backups, spare hardware |
| R-002 | Data loss from misconfiguration | 3 | 3 | 9 | Medium | Version control, snapshots |
| R-003 | VM escape in nested virtualization | 1 | 5 | 5 | Low | Isolation, patches |
| R-004 | Firewall bypass via misconfiguration | 2 | 5 | 10 | Medium | Rule testing, peer review |
| R-005 | IDS false positive flood | 3 | 2 | 6 | Low | Rule tuning, threshold setting |
| R-006 | Performance degradation beyond threshold | 2 | 3 | 6 | Low | Benchmarking, optimization |
| R-007 | ELK Stack disk space exhaustion | 3 | 3 | 9 | Medium | Log rotation, monitoring |
| R-008 | Network storm from misconfigured switch | 2 | 4 | 8 | Medium | STP, port isolation |
| R-009 | Academic deadline not met | 2 | 5 | 10 | Medium | Project planning, milestones |
| R-010 | Threat feed API rate limiting | 2 | 2 | 4 | Low | Caching, fallback |
| R-011 | Windows Server license expiry | 2 | 3 | 6 | Low | Academic MSDN renewal |
| R-012 | VMware ESXi evaluation expiry | 3 | 4 | 12 | Medium | Free license registration |
| R-013 | Suricata rule conflict | 2 | 2 | 4 | Low | Rule testing, disable conflicting |
| R-014 | pfSense configuration corruption | 1 | 5 | 5 | Low | XML backup, restore procedure |
| R-015 | Security test escaping lab environment | 1 | 5 | 5 | Low | Network isolation, monitoring |

## Detailed Risk Assessments

### R-001: Hardware Failure During Testing

**Description**: Physical host hardware (CPU, RAM, disk) fails during lab testing sessions, causing VM data loss.

**Likelihood**: Low (2) - Consumer hardware is generally reliable; SSD failures are rare.

**Impact**: High (4) - All VM data lost; significant time to rebuild.

**Mitigation Strategies**:
1. Take VMware Workstation snapshots before every major test session
2. Export VM configurations as OVF/OVA backups weekly
3. Run `backup-config.sh` daily to backup configuration files
4. Enable SMART monitoring on SSDs: `smartctl -a /dev/sda`
5. Keep spare SSD available

**Residual Risk**: Low (4) - After mitigation, data loss recovery time < 2 hours.

---

### R-004: Firewall Bypass via Misconfiguration

**Description**: Incorrectly configured firewall rules inadvertently permit traffic that should be blocked, creating security policy violations.

**Likelihood**: Low-Medium (2) - Complex rule sets increase probability of human error.

**Impact**: Critical (5) - Could allow lateral movement between segments, defeating project objective.

**Mitigation Strategies**:
1. Use automated test suite (`network-test.sh`) after every rule change
2. Implement peer review of all firewall rule changes
3. Default-deny policy means errors fail safe (block rather than allow)
4. Use `firewall-policy-generator.py --validate` before deploying rules
5. Check logs daily for unexpected allowed traffic

**Residual Risk**: Low (4) - Default-deny significantly reduces impact of rule errors.

---

### R-009: Academic Deadline Not Met

**Description**: Project complexity causes timeline slippage, risking submission deadline.

**Likelihood**: Low-Medium (2) - Complex multi-component project.

**Impact**: Critical (5) - Academic penalty or failure.

**Mitigation Strategies**:
1. Gantt chart project planning with milestone tracking
2. MVP approach: core DFW functionality first, enhancements later
3. Weekly supervisor check-ins
4. Use GitHub Issues for task tracking
5. Time-box each component: 2 weeks max per major feature

**Residual Risk**: Low (4) - With proper planning, deadline risk is manageable.

---

### R-012: VMware ESXi Evaluation License Expiry

**Description**: ESXi 60-day evaluation license expires mid-project, disabling hypervisor management features.

**Likelihood**: Medium (3) - ESXi free license requires registration.

**Impact**: High (4) - Cannot manage VMs without valid license.

**Mitigation Strategies**:
1. Register for free VMware Personal Use license before project start
2. Note expiry date and set calendar reminder 2 weeks before
3. Alternatively, use VMware Workstation Pro (already purchased) to host nested ESXi
4. Keep VMware Workstation as fallback if ESXi license issues arise

**Residual Risk**: Low (3) - Free license available, straightforward to apply.

## Risk Register Summary

| Rating | Count | Risk IDs |
|--------|-------|----------|
| Critical (20-25) | 0 | - |
| High (13-19) | 0 | - |
| Medium (7-12) | 5 | R-002, R-004, R-007, R-008, R-009, R-012 |
| Low (1-6) | 10 | R-001, R-003, R-005, R-006, R-010, R-011, R-013, R-014, R-015 |

## Overall Risk Assessment

**Overall Project Risk**: LOW-MEDIUM

The project has no high or critical risks after mitigation. The primary risk areas are:
1. **Technical complexity** - Managed through incremental implementation
2. **License expiry** - Managed through early registration
3. **Timeline** - Managed through project planning and MVP approach

The security of the lab environment itself is well-controlled through network isolation and monitoring.
