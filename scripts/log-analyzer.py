#!/usr/bin/env python3
"""
log-analyzer.py - Distributed Firewall VDC Log Analysis Tool

Parsed and analyzes logs from pfSense, Suricata, and system logs.
Generates security reports and detects anomalies.

Usage:
    python log-analyzer.py --source suricata --report
    python log-analyzer.py --source pfsense --output report.json

Author: VDC Security Project Team
Version: 2.0.0
"""

import argparse
import json
import re
import sys
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Sample Suricata EVE log entries for demonstration
SAMPLE_SURICATA_EVE_LOGS = [
    '{"timestamp":"2025-03-15T14:23:01.456781+0000","flow_id":1234567890,"event_type":"alert","src_ip":"192.168.40.15","src_port":54321,"dest_ip":"192.168.20.10","dest_port":80,"proto":"TCP","alert":{"action":"allowed","signature_id":2019236,"rev":3,"signature":"ET SCAN Nmap Scripting Engine User-Agent Detected","category":"Web Application Attack","severity":1}}',
    '{"timestamp":"2025-03-15T14:25:33.123456+0000","flow_id":9876543210,"event_type":"alert","src_ip":"192.168.40.15","src_port":12345,"dest_ip":"192.168.30.10","dest_port":3306,"proto":"TCP","alert":{"action":"allowed","signature_id":9000004,"rev":1,"signature":"VDC Lateral Movement - WS to DB MySQL","category":"Policy Violation","severity":2}}',
    '{"timestamp":"2025-03-15T14:28:11.789012+0000","flow_id":1111111111,"event_type":"alert","src_ip":"203.0.113.45","src_port":44321,"dest_ip":"192.168.20.10","dest_port":80,"proto":"TCP","alert":{"action":"dropped","signature_id":9000006,"rev":1,"signature":"VDC SQL Injection Attempt","category":"Web Application Attack","severity":1}}',
]

SAMPLE_PFSENSE_LOGS = [
    'Mar 15 14:22:00 pfSense filterlog[12345]: 5,,,1234567890,em1,match,block,in,4,0x0,,64,12345,0,DF,6,tcp,60,203.0.113.100,192.168.10.1,45678,443,0,S,3987654321,,65535,,mss',
    'Mar 15 14:23:15 pfSense filterlog[12345]: 5,,,1234567891,em0,match,pass,in,4,0x0,,64,12346,0,DF,6,tcp,60,10.0.0.5,192.168.20.10,34567,80,0,S,3987654322,,65535,,mss',
    'Mar 15 14:25:00 pfSense filterlog[12345]: 5,,,1234567893,em1,match,block,in,4,0x0,,64,12348,0,DF,17,udp,28,192.168.40.10,192.168.30.10,55000,3306,0',
]


class SuricataEVEParser:
    """Parser for Suricata EVE JSON log format."""

    def parse_line(self, line: str) -> Dict[str, Any]:
        """Parse a single EVE JSON log line."""
        try:
            event = json.loads(line.strip())
            return self._normalize(event)
        except json.JSONDecodeError as e:
            return {'error': str(e), 'raw': line[:200]}

    def _normalize(self, event: Dict) -> Dict:
        """Normalize EVE event to standard format."""
        normalized = {
            'timestamp': event.get('timestamp', ''),
            'event_type': event.get('event_type', ''),
            'src_ip': event.get('src_ip', ''),
            'src_port': event.get('src_port', 0),
            'dst_ip': event.get('dest_ip', ''),
            'dst_port': event.get('dest_port', 0),
            'proto': event.get('proto', ''),
            'source': 'suricata',
        }
        if event.get('event_type') == 'alert' and 'alert' in event:
            alert = event['alert']
            normalized.update({
                'alert_action': alert.get('action', ''),
                'signature_id': alert.get('signature_id', 0),
                'signature': alert.get('signature', ''),
                'category': alert.get('category', ''),
                'severity': alert.get('severity', 0),
            })
        return normalized

    def parse_file(self, filepath: str) -> List[Dict]:
        """Parse all events from EVE JSON file."""
        events = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    if line.strip():
                        events.append(self.parse_line(line))
        except FileNotFoundError:
            print(f'[INFO] File not found, using sample data: {filepath}')
            for line in SAMPLE_SURICATA_EVE_LOGS:
                events.append(self.parse_line(line))
        return events


class PfSenseLogParser:
    """Parser for pfSense filterlog format."""

    PATTERN = re.compile(
        r'(?P<month>\w+)\s+(?P<day>\d+)\s+(?P<time>\S+)\s+'
        r'(?P<host>\S+)\s+filterlog\[\d+\]:\s+(?P<fields>.+)'
    )

    def parse_line(self, line: str) -> Dict[str, Any]:
        """Parse a pfSense filterlog line."""
        match = self.PATTERN.match(line)
        if not match:
            return {}
        fields = match.group('fields').split(',')
        try:
            return {
                'timestamp': f"{match.group('month')} {match.group('day')} {match.group('time')}",
                'source': 'pfsense',
                'interface': fields[4] if len(fields) > 4 else '',
                'action': fields[6] if len(fields) > 6 else '',
                'direction': fields[7] if len(fields) > 7 else '',
                'protocol': fields[16] if len(fields) > 16 else '',
                'src_ip': fields[18] if len(fields) > 18 else '',
                'dst_ip': fields[19] if len(fields) > 19 else '',
                'src_port': int(fields[20]) if len(fields) > 20 and fields[20].isdigit() else 0,
                'dst_port': int(fields[21]) if len(fields) > 21 and fields[21].isdigit() else 0,
            }
        except (IndexError, ValueError):
            return {'raw': line, 'source': 'pfsense'}

    def parse_file(self, filepath: str) -> List[Dict]:
        """Parse all events from pfSense log file."""
        events = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    if 'filterlog' in line:
                        event = self.parse_line(line.strip())
                        if event:
                            events.append(event)
        except FileNotFoundError:
            print(f'[INFO] File not found, using sample data')
            for line in SAMPLE_PFSENSE_LOGS:
                event = self.parse_line(line)
                if event:
                    events.append(event)
        return events


class SecurityAnalyzer:
    """Analyzes log events to identify security patterns."""

    def __init__(self):
        self.events: List[Dict] = []

    def load_events(self, events: List[Dict]):
        """Load events into the analyzer."""
        self.events.extend(events)

    def top_attackers(self, n: int = 10) -> List[tuple]:
        """Identify top source IPs generating events."""
        src_ips = Counter(e['src_ip'] for e in self.events if e.get('src_ip'))
        return src_ips.most_common(n)

    def top_signatures(self, n: int = 10) -> List[tuple]:
        """Identify most triggered IDS signatures."""
        sigs = Counter(e.get('signature', 'Unknown') for e in self.events if e.get('event_type') == 'alert')
        return sigs.most_common(n)

    def detect_lateral_movement(self) -> List[Dict]:
        """Detect potential lateral movement patterns."""
        lateral = []
        internal = ['192.168.', '10.', '172.16.']
        suspicious_ports = {22, 3389, 445, 139, 3306, 5432, 1433}
        for event in self.events:
            src = event.get('src_ip', '')
            dst = event.get('dst_ip', '')
            src_int = any(src.startswith(n) for n in internal)
            dst_int = any(dst.startswith(n) for n in internal)
            if src_int and dst_int and event.get('dst_port', 0) in suspicious_ports:
                lateral.append({'type': 'lateral_movement', 'src': src, 'dst': dst,
                                'port': event.get('dst_port'), 'timestamp': event.get('timestamp', '')})
        return lateral

    def generate_report(self) -> Dict:
        """Generate a comprehensive security analysis report."""
        alert_events = [e for e in self.events if e.get('event_type') == 'alert']
        block_events = [e for e in self.events if e.get('action') == 'block']
        lateral = self.detect_lateral_movement()
        return {
            'report_generated': datetime.utcnow().isoformat(),
            'summary': {
                'total_events': len(self.events),
                'total_alerts': len(alert_events),
                'total_blocks': len(block_events),
                'lateral_movement': len(lateral),
            },
            'top_attackers': [{'ip': ip, 'count': c} for ip, c in self.top_attackers()],
            'top_signatures': [{'signature': s, 'count': c} for s, c in self.top_signatures()],
            'lateral_movement': lateral,
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='VDC Security Log Analyzer')
    parser.add_argument('--source', choices=['suricata', 'pfsense', 'all'], default='all')
    parser.add_argument('--file', help='Log file path')
    parser.add_argument('--report', action='store_true')
    parser.add_argument('--output', help='Output JSON file')
    parser.add_argument('--format', choices=['json', 'text'], default='text')
    args = parser.parse_args()

    print('=' * 60)
    print(' VDC Security Log Analyzer v2.0.0')
    print('=' * 60)

    analyzer = SecurityAnalyzer()

    if args.source in ('suricata', 'all'):
        p = SuricataEVEParser()
        events = p.parse_file(args.file or '/var/log/suricata/eve.json')
        analyzer.load_events(events)
        print(f'[INFO] Loaded {len(events)} Suricata events')

    if args.source in ('pfsense', 'all'):
        p = PfSenseLogParser()
        events = p.parse_file(args.file or '/var/log/pfsense/filter.log')
        analyzer.load_events(events)
        print(f'[INFO] Loaded {len(events)} pfSense events')

    report = analyzer.generate_report()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f'[OK] Report saved to: {args.output}')
    elif args.format == 'json':
        print(json.dumps(report, indent=2, default=str))
    else:
        s = report['summary']
        print(f"\nTotal Events: {s['total_events']}")
        print(f"IDS Alerts:   {s['total_alerts']}")
        print(f"FW Blocks:    {s['total_blocks']}")
        print(f"Lateral Mvmt: {s['lateral_movement']}")
        print('\nTop Attackers:')
        for item in report['top_attackers'][:5]:
            print(f"  {item['ip']:<20} {item['count']} events")


if __name__ == '__main__':
    main()
