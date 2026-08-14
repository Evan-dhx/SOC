import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for cmd in [
    'cat /Agent/etc/nftls.status 2>/dev/null; echo "==="; ls -la /Agent/etc/nftls.status 2>/dev/null',
    'echo "=== tcpdump TLS on lo (2 sec) ==="; timeout 3 tcpdump -i lo -c 3 -X port 19996 -Q inout 2>&1 | tail -25',
    'echo "=== nfcapd recent data ==="; nfdump -r /data/flow/1/nfcapd.current -s ip -o "fmt:%ts %te %sa %da %pkt" 2>/dev/null | head -5',
    'echo "=== indexer status ==="; cat /Agent/data/indexer_process 2>/dev/null | tail -3; echo; ps -e | grep indexer',
]:
    print(f"\n=== {cmd[:50]} ===")
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')[:1500]
    err = e.read().decode('utf-8', errors='replace')[:200]
    if out: print(out)
    if err: print('ERR:', err)
c.close()