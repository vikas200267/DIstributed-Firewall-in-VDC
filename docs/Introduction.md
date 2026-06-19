# Introduction

## Overview

This document introduces the **Distributed Firewall in Virtual Data Center (VDC)** project — a final-year Cyber Security research and implementation project that explores how distributed firewall technology can secure east-west traffic inside virtualized environments.

## Background

The rapid adoption of virtualization in modern data centers has fundamentally changed how network security must be implemented. Traditional perimeter-based security models — which rely on a single physical firewall to protect the network boundary — are increasingly inadequate in environments where hundreds of virtual machines (VMs) communicate laterally within the same physical infrastructure.

VMware NSX, Microsoft Azure Network Security Groups, and AWS Security Groups all represent commercial implementations of the distributed firewall concept. This project replicates the core principles of these enterprise systems in a controlled lab environment using VMware Workstation, ESXi hypervisors, and pfSense — all running on commodity hardware.

## What is a Distributed Firewall?

A distributed firewall is a security model where firewall policies are enforced at the virtual network interface card (vNIC) of each individual virtual machine, rather than at a centralized choke point. This approach provides several critical advantages:

1. **Per-VM Policy Enforcement** — Each VM has its own security policy applied directly at the hypervisor level
2. **East-West Filtering** — Traffic between VMs on the same host or network segment is inspected and filtered
3. **Scalability** — Policies scale with VM deployment without creating bottlenecks
4. **Zero-Trust Implementation** — Supports the principle of least privilege for all inter-VM communication

## Project Scope

This project covers:

- **Infrastructure Deployment** — VMware Workstation 17 hosting two ESXi 7.0 hypervisors
- **Network Architecture** — VLAN segmentation, virtual switching, pfSense edge routing
- **Security Implementation** — Distributed firewall rules, microsegmentation, IDS/IPS
- **Threat Intelligence** — Integration of live threat feeds for automated blocking
- **Observability** — ELK Stack, Grafana, Prometheus for monitoring and logging
- **Security Testing** — Comprehensive testing of all security controls
- **Performance Analysis** — Measurement of overhead introduced by security controls

## Academic Context

This project is submitted in partial fulfillment of the requirements for the **Bachelor of Science (Honours) in Cyber Security**. It combines theoretical knowledge from network security, virtualization, and systems administration with practical implementation skills.

The project aligns with industry frameworks including:
- **NIST Zero Trust Architecture** (SP 800-207)
- **MITRE ATT&CK Framework** — for understanding attack vectors tested
- **CIS Benchmarks** — for hardening baseline configurations
- **ISO/IEC 27001** — for overall security management principles

## Report Structure

This documentation is organized as follows:

| Document | Description |
|---------|-------------|
| [Introduction](Introduction.md) | This document — project overview and context |
| [Literature Review](Literature-Review.md) | Academic and industry research review |
| [Objectives](Objectives.md) | Detailed project objectives and success criteria |
| [Requirements](Requirements.md) | Functional and non-functional requirements |
| [Methodology](Methodology.md) | Research and implementation methodology |
| [Installation](Installation.md) | Step-by-step installation guide |
| [Configuration](Configuration.md) | Detailed configuration reference |
| [Firewall Policies](Firewall-Policies.md) | Firewall rule design and implementation |
| [IDS/IPS](IDS-IPS.md) | Intrusion detection and prevention |
| [Threat Intelligence](Threat-Intelligence.md) | Threat feed integration |
| [Testing](Testing.md) | Security testing methodology and results |
| [Results](Results.md) | Performance and security results analysis |
| [Cost Breakdown](Cost-Breakdown.md) | Project cost analysis |
| [Risk Analysis](Risk-Analysis.md) | Risk assessment and mitigation |
| [Future Work](Future-Work.md) | Planned improvements and extensions |
| [Conclusion](Conclusion.md) | Final conclusions and recommendations |
| [References](References.md) | Academic and technical references |
