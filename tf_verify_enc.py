import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("Waiting 60s for NetFlow data accumulation...")
time.sleep(60)

for cmd in [
    'ls -la /data/flow/1/ 2>/dev/null | tail -8',
    'ps -e | grep -E "tsensor|nftls|fcapd|indexer|fsd" | head -10',
    'ss -uln | grep -E "999[56]"',
]:
    print(f"\n=== {cmd[:50]} ===")
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')[:1000]
    err = e.read().decode('utf-8', errors='replace')[:200]
    if out: print(out)
    if err: print('ERR:', err)

print("\n=== tcpdump port 19996 (5 packets) ===")
i, o, e = c.exec_command('timeout 5 tcpdump -i lo -c 3 -X port 19996 2>&1', timeout=30)
out = o.read().decode('utf-8', errors='replace')[:1500]
print(out[:1500] if out else "(no output)")

c.close()