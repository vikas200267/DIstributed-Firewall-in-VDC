#!/usr/bin/env python3
"""
firewall-policy-generator.py - VDC Distributed Firewall Policy Generator

Reads firewall policy definitions from YAML/JSON and generates deployable
firewall rule configurations for pfSense and nftables (Linux).

Usage:
    python firewall-policy-generator.py --input configs/FirewallRules/policies.yaml
    python firewall-policy-generator.py --validate
    python firewall-policy-generator.py --output-dir ./generated

Author: VDC Security Project Team
Version: 2.0.0
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

SAMPLE_POLICIES = {
    'version': '2.0',
    'segments': [
        {
            'name': 'DMZ',
            'vlan': 20,
            'subnet': '192.168.20.0/24',
            'rules': [
                {'id': 'DMZ-IN-001', 'direction': 'inbound', 'action': 'ALLOW',
                 'src': 'ANY', 'dst': '192.168.20.0/24', 'proto': 'TCP', 'port': 80,
                 'log': True, 'description': 'Allow HTTP to DMZ'},
                {'id': 'DMZ-IN-002', 'direction': 'inbound', 'action': 'ALLOW',
                 'src': 'ANY', 'dst': '192.168.20.0/24', 'proto': 'TCP', 'port': 443,
                 'log': True, 'description': 'Allow HTTPS to DMZ'},
                {'id': 'DMZ-IN-999', 'direction': 'inbound', 'action': 'DENY',
                 'src': 'ANY', 'dst': 'ANY', 'proto': 'ANY', 'port': 'ANY',
                 'log': True, 'description': 'Default deny all to DMZ'},
            ]
        },
        {
            'name': 'Database',
            'vlan': 30,
            'subnet': '192.168.30.0/24',
            'rules': [
                {'id': 'DB-IN-001', 'direction': 'inbound', 'action': 'ALLOW',
                 'src': '192.168.20.0/24', 'dst': '192.168.30.0/24', 'proto': 'TCP', 'port': 3306,
                 'log': True, 'description': 'Allow MySQL from DMZ only'},
                {'id': 'DB-IN-002', 'direction': 'inbound', 'action': 'ALLOW',
                 'src': '192.168.10.0/24', 'dst': '192.168.30.0/24', 'proto': 'TCP', 'port': 22,
                 'log': True, 'description': 'Allow SSH from management'},
                {'id': 'DB-IN-999', 'direction': 'inbound', 'action': 'DENY',
                 'src': 'ANY', 'dst': 'ANY', 'proto': 'ANY', 'port': 'ANY',
                 'log': True, 'description': 'Default deny all to Database'},
            ]
        }
    ]
}


class NFTablesGenerator:
    """Generates nftables rules from policy definitions."""

    def generate(self, segment: Dict) -> str:
        """Generate nftables ruleset for a network segment."""
        name = segment['name']
        subnet = segment['subnet']
        rules = segment.get('rules', [])
        lines = [
            f'# Generated nftables rules for: {name}',
            f'# Subnet: {subnet}',
            f'# Generated: {datetime.utcnow().isoformat()}',
            '',
            'flush ruleset',
            '',
            'table inet vdc_firewall {',
            f'    chain {name.lower()}_input {{',
            '        type filter hook input priority 0; policy drop;',
            '        ct state established,related accept',
            '        iif lo accept',
            '',
        ]
        for rule in rules:
            lines.extend(self._to_nftables(rule))
        lines.extend(['    }', '}'])
        return '\n'.join(lines)

    def _to_nftables(self, rule: Dict) -> List[str]:
        """Convert a policy rule to nftables syntax."""
        parts = []
        if rule.get('src') and rule['src'] != 'ANY':
            parts.append(f"ip saddr {rule['src']}")
        if rule.get('dst') and rule['dst'] != 'ANY':
            parts.append(f"ip daddr {rule['dst']}")
        if rule.get('proto') and rule['proto'] != 'ANY':
            proto = rule['proto'].lower()
            if rule.get('port') and rule['port'] != 'ANY':
                parts.append(f"{proto} dport {rule['port']}")
        action_map = {'ALLOW': 'accept', 'DENY': 'drop', 'REJECT': 'reject'}
        action = action_map.get(rule.get('action', 'DENY'), 'drop')
        rule_str = ' '.join(parts)
        comment = f"# {rule['id']}: {rule['description']}"
        if rule.get('log'):
            log_prefix = f"[VDC-{rule['id']}] "
            if rule_str:
                nft_line = f'        {rule_str} log prefix "{log_prefix}" {action}'
            else:
                nft_line = f'        log prefix "{log_prefix}" {action}'
        else:
            nft_line = f'        {rule_str} {action}' if rule_str else f'        {action}'
        return [f'        {comment}', nft_line, '']


class PolicyValidator:
    """Validates firewall policy definitions."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self, policies: Dict) -> bool:
        """Validate policy set. Returns True if valid."""
        self.errors = []
        self.warnings = []
        for segment in policies.get('segments', []):
            self._validate_segment(segment)
        return len(self.errors) == 0

    def _validate_segment(self, segment: Dict):
        """Validate a single segment."""
        name = segment.get('name', 'Unknown')
        rules = segment.get('rules', [])
        has_default_deny = any(
            r.get('action') == 'DENY' and r.get('src') == 'ANY' and r.get('dst') == 'ANY'
            for r in rules
        )
        if not has_default_deny:
            self.warnings.append(f"Segment '{name}': No default-deny rule")
        ids = [r.get('id') for r in rules]
        if len(ids) != len(set(ids)):
            self.errors.append(f"Segment '{name}': Duplicate rule IDs")

    def report(self):
        """Print validation report."""
        if self.errors:
            print(f'\n[ERROR] Validation FAILED - {len(self.errors)} error(s):')
            for err in self.errors:
                print(f'  - {err}')
        else:
            print('\n[OK] Policy validation PASSED')
        if self.warnings:
            print(f'\n[WARN] {len(self.warnings)} warning(s):')
            for w in self.warnings:
                print(f'  ! {w}')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='VDC Firewall Policy Generator')
    parser.add_argument('--input', help='Input YAML policy file')
    parser.add_argument('--output-dir', default='./generated', help='Output directory')
    parser.add_argument('--validate', action='store_true', help='Validate only')
    parser.add_argument('--format', choices=['nftables', 'json', 'all'], default='all')
    parser.add_argument('--deploy', action='store_true', help='Deploy generated rules')
    args = parser.parse_args()

    print('=' * 60)
    print(' VDC Firewall Policy Generator v2.0.0')
    print('=' * 60)

    try:
        import yaml
        if args.input and Path(args.input).exists():
            with open(args.input) as f:
                policies = yaml.safe_load(f)
            print(f'[INFO] Loaded: {args.input}')
        else:
            policies = SAMPLE_POLICIES
            print('[INFO] Using built-in sample policies')
    except ImportError:
        policies = SAMPLE_POLICIES
        print('[INFO] PyYAML not available, using sample policies')

    validator = PolicyValidator()
    is_valid = validator.validate(policies)
    validator.report()

    if args.validate:
        sys.exit(0 if is_valid else 1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    nft_gen = NFTablesGenerator()

    for segment in policies.get('segments', []):
        seg_name = segment['name'].lower()
        if args.format in ('nftables', 'all'):
            rules = nft_gen.generate(segment)
            f = output_dir / f'{seg_name}-nftables.rules'
            f.write_text(rules)
            print(f'[OK] Generated: {f}')
        if args.format in ('json', 'all'):
            f = output_dir / f'{seg_name}-policy.json'
            f.write_text(json.dumps(segment, indent=2))
            print(f'[OK] Generated: {f}')

    print(f'\n[OK] Complete. Output: {output_dir}')


if __name__ == '__main__':
    main()
