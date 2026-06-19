#!/bin/bash
# =============================================================================
# network-test.sh - VDC Network Connectivity and Firewall Test Suite
# Version: 2.0.0
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

PFSENSE_IP="192.168.10.1"
DNS_IP="192.168.10.20"
WEB_IP="192.168.20.10"
DB_IP="192.168.30.10"
CLIENT_IP="192.168.40.10"
ELK_IP="192.168.50.20"

mkdir -p ./logs

log_result() {
    local name="$1" result="$2" detail="$3"
    case "$result" in
        PASS) echo -e "  ${GREEN}[PASS]${NC} ${name}: ${detail}"; ((PASS++)) ;;
        FAIL) echo -e "  ${RED}[FAIL]${NC} ${name}: ${detail}"; ((FAIL++)) ;;
        WARN) echo -e "  ${YELLOW}[WARN]${NC} ${name}: ${detail}"; ((WARN++)) ;;
    esac
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$result] $name: $detail" >> ./logs/network-test.log
}

test_ping() {
    local name="$1" ip="$2" expected="$3"
    if ping -c 1 -W 2 "$ip" >/dev/null 2>&1; then
        [ "$expected" = "reachable" ] && log_result "Ping $name" PASS "Host responds" || log_result "Ping $name" FAIL "Should be blocked"
    else
        [ "$expected" = "blocked" ] && log_result "Ping $name" PASS "Correctly blocked" || log_result "Ping $name" FAIL "Host unreachable"
    fi
}

test_tcp() {
    local name="$1" ip="$2" port="$3" expected="$4"
    if timeout 3 bash -c "</dev/tcp/${ip}/${port}" 2>/dev/null; then
        [ "$expected" = "open" ] && log_result "TCP $name ($ip:$port)" PASS "Port open" || log_result "TCP $name ($ip:$port)" FAIL "Should be blocked"
    else
        [ "$expected" = "closed" ] && log_result "TCP $name ($ip:$port)" PASS "Correctly blocked" || log_result "TCP $name ($ip:$port)" FAIL "Port should be open"
    fi
}

test_http() {
    local name="$1" url="$2" expected="$3"
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")
    [ "$code" = "$expected" ] && log_result "HTTP $name" PASS "HTTP $code" || log_result "HTTP $name" FAIL "Got $code, expected $expected"
}

run_ping_tests() {
    echo -e "\n${BLUE}=== ICMP Ping Tests ===${NC}"
    test_ping "pfSense Edge" "$PFSENSE_IP" reachable
    test_ping "DNS Server"   "$DNS_IP"     reachable
    test_ping "Web Server"   "$WEB_IP"     reachable
    test_ping "DB Server"    "$DB_IP"      reachable
    test_ping "ELK Stack"    "$ELK_IP"     reachable
}

run_port_tests() {
    echo -e "\n${BLUE}=== TCP Port Tests ===${NC}"
    test_tcp "pfSense HTTPS" "$PFSENSE_IP" 443  open
    test_tcp "DNS TCP"       "$DNS_IP"     53   open
    test_tcp "Web HTTP"      "$WEB_IP"     80   open
    test_tcp "Web HTTPS"     "$WEB_IP"     443  open
    test_tcp "ELK Kibana"    "$ELK_IP"     5601 open
    test_tcp "DB MySQL (blocked)" "$DB_IP" 3306 closed
    test_tcp "Web SSH (blocked)"  "$WEB_IP" 22  closed
}

run_http_tests() {
    echo -e "\n${BLUE}=== HTTP Service Tests ===${NC}"
    test_http "Web Server"   "http://${WEB_IP}"      "200"
    test_http "pfSense GUI"  "http://${PFSENSE_IP}"  "200"
    test_http "Kibana"       "http://${ELK_IP}:5601" "200"
}

main() {
    echo -e "${BLUE}\n=========================================="
    echo " Distributed Firewall VDC - Network Tests"
    echo -e "==========================================${NC}\n"
    echo "Started: $(date)"

    case "${1:-all}" in
        --verify-all) run_ping_tests; run_port_tests; run_http_tests ;;
        --ping-only)  run_ping_tests ;;
        --port-only)  run_port_tests ;;
        all)          run_ping_tests; run_port_tests; run_http_tests ;;
    esac

    echo ""
    echo -e "=== SUMMARY ==="
    echo -e "  ${GREEN}PASS: ${PASS}${NC} | ${RED}FAIL: ${FAIL}${NC} | ${YELLOW}WARN: ${WARN}${NC}"
    [ $FAIL -gt 0 ] && echo -e "${RED}Tests FAILED${NC}" && exit 1 || echo -e "${GREEN}All tests PASSED${NC}"
}

main "$@"
