#!/usr/bin/env python3
"""
vm-health.py - VDC Virtual Machine Health Monitor

Monitors health and resource utilization of all VMs in the VDC.
Reports CPU, memory, disk, and service status.

Usage:
    python vm-health.py --check-all
    python vm-health.py --vm 192.168.20.10
    python vm-health.py --report --format json

Author: VDC Security Project Team
Version: 2.0.0
"""

import argparse
import json
import socket
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

VM_INVENTORY = [
    {'name': 'pfSense-Edge',  'ip': '192.168.10.1',  'os': 'freebsd', 'role': 'firewall'},
    {'name': 'DNS-Server',    'ip': '192.168.10.20', 'os': 'windows', 'role': 'dns'},
    {'name': 'Web-Server',    'ip': '192.168.20.10', 'os': 'ubuntu',  'role': 'web'},
    {'name': 'DB-Server',     'ip': '192.168.30.10', 'os': 'ubuntu',  'role': 'database'},
    {'name': 'Client-Ubuntu', 'ip': '192.168.40.10', 'os': 'ubuntu',  'role': 'workstation'},
    {'name': 'Suricata-IDS',  'ip': '192.168.50.10', 'os': 'ubuntu',  'role': 'ids'},
    {'name': 'ELK-Stack',     'ip': '192.168.50.20', 'os': 'ubuntu',  'role': 'logging'},
]

THRESHOLDS = {
    'cpu_percent': 80.0,
    'mem_percent': 85.0,
    'disk_percent': 90.0,
}


class VMHealthCheck:
    """Performs health checks on a VM."""

    def __init__(self, vm: Dict, ssh_user: str = 'ubuntu', ssh_key: Optional[str] = None):
        self.vm = vm
        self.ip = vm['ip']
        self.name = vm['name']
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key

    def is_reachable(self) -> bool:
        """Check if VM responds on port 22."""
        try:
            with socket.create_connection((self.ip, 22), timeout=3):
                return True
        except (socket.timeout, socket.error):
            return False

    def run_ssh(self, cmd: str) -> Optional[str]:
        """Execute command via SSH."""
        args = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=5',
                '-o', 'BatchMode=yes']
        if self.ssh_key:
            args.extend(['-i', self.ssh_key])
        args.extend([f'{self.ssh_user}@{self.ip}', cmd])
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=10)
            return r.stdout.strip() if r.returncode == 0 else None
        except Exception:
            return None

    def get_cpu(self) -> Optional[float]:
        """Get CPU usage."""
        out = self.run_ssh("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
        try:
            return float(out) if out else None
        except ValueError:
            return None

    def get_memory(self) -> Optional[Dict]:
        """Get memory usage."""
        out = self.run_ssh('free -m | awk \'NR==2{printf "%s %s %s", $2,$3,$4}\'')
        if out:
            p = out.split()
            if len(p) == 3:
                total, used, free = int(p[0]), int(p[1]), int(p[2])
                return {'total_mb': total, 'used_mb': used, 'free_mb': free,
                        'percent': round((used/total)*100, 1) if total > 0 else 0}
        return None

    def get_disk(self) -> Optional[Dict]:
        """Get disk usage."""
        out = self.run_ssh("df -h / | awk 'NR==2{print $2, $3, $4, $5}'")
        if out:
            p = out.split()
            if len(p) == 4:
                return {'total': p[0], 'used': p[1], 'available': p[2],
                        'percent': int(p[3].replace('%', ''))}
        return None

    def check(self) -> Dict:
        """Run complete health check."""
        print(f'  {self.name} ({self.ip})...', end=' ', flush=True)
        health = {
            'name': self.name, 'ip': self.ip, 'role': self.vm.get('role', ''),
            'timestamp': datetime.utcnow().isoformat(),
            'reachable': False, 'alerts': []
        }
        if not self.is_reachable():
            health['status'] = 'OFFLINE'
            health['alerts'].append({'level': 'CRITICAL', 'message': 'Host not reachable'})
            print('OFFLINE')
            return health
        health['reachable'] = True
        if self.vm.get('os') == 'ubuntu':
            cpu = self.get_cpu()
            mem = self.get_memory()
            disk = self.get_disk()
            health['metrics'] = {'cpu_percent': cpu, 'memory': mem, 'disk': disk}
            if cpu and cpu > THRESHOLDS['cpu_percent']:
                health['alerts'].append({'level': 'WARNING', 'message': f'High CPU: {cpu}%'})
            if mem and mem['percent'] > THRESHOLDS['mem_percent']:
                health['alerts'].append({'level': 'WARNING', 'message': f'High memory: {mem["percent"]}%'})
            if disk and disk['percent'] > THRESHOLDS['disk_percent']:
                health['alerts'].append({'level': 'CRITICAL', 'message': f'Disk critical: {disk["percent"]}%'})
        alert_levels = [a['level'] for a in health['alerts']]
        health['status'] = 'CRITICAL' if 'CRITICAL' in alert_levels else ('WARNING' if 'WARNING' in alert_levels else 'HEALTHY')
        print(health['status'])
        return health


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='VDC VM Health Monitor')
    parser.add_argument('--check-all', action='store_true')
    parser.add_argument('--vm', help='Specific VM IP')
    parser.add_argument('--ssh-user', default='ubuntu')
    parser.add_argument('--ssh-key')
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    args = parser.parse_args()

    print('=' * 60)
    print(f' VDC VM Health Monitor v2.0.0 | {datetime.utcnow().isoformat()}')
    print('=' * 60)

    vms = VM_INVENTORY
    if args.vm:
        vms = [v for v in VM_INVENTORY if v['ip'] == args.vm] or \
              [{'name': 'Custom', 'ip': args.vm, 'os': 'ubuntu', 'role': 'unknown'}]

    print(f'\nChecking {len(vms)} VM(s):\n')
    results = [VMHealthCheck(vm, args.ssh_user, args.ssh_key).check() for vm in vms]

    healthy = sum(1 for r in results if r.get('status') == 'HEALTHY')
    warning = sum(1 for r in results if r.get('status') == 'WARNING')
    critical = sum(1 for r in results if r.get('status') in ('CRITICAL', 'OFFLINE'))

    if args.format == 'json':
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f'\nSummary: {len(results)} total | {healthy} healthy | {warning} warning | {critical} critical')
        for r in results:
            for a in r.get('alerts', []):
                print(f"  [{a['level']}] {r['name']}: {a['message']}")


if __name__ == '__main__':
    main()
