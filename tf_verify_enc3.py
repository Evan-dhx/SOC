import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for cmd in [
    # Read a completed nfcapd file (not the current one)
    'nfdump -r /data/flow/1/nfcapd.202608140845 -c 5 2>/dev/null | head -10',
    # Check indexer results
    'cat /Agent/data/indexer_feature 2>/dev/null | tail -5',
    # Check indexer cache
    'cat /Agent/data/indexer_cache 2>/dev/null | tail -5',
    # Check indexer process status
    'ps -e | grep indexer; cat /Agent/data/indexer_process 2>/dev/null',
    # Verify encryption - check no NetFlow v9 header on wire
    'echo "=== NetFlow header check (should be 0) ==="; timeout 3 tcpdump -i lo -c 10 -X port 19996 2>&1 | grep -c "0009" || echo "no 0009 found - 密文传输"',
    # Final status summary
    'ps -e | grep -c tsensor; ps -e | grep -c nftls; ps -e | grep -c nfcapd; ps -e | grep -c indexer; echo "nftls_status:"; cat /Agent/etc/nftls.status 2>/dev/null',
]:
    print(f"\n=== {cmd[:50]} ===")
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')[:1200]
    err = e.read().decode('utf-8', errors='replace')[:300]
    if out: print(out)
    if err: print('ERR:', err)
c.close()