import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("Waiting 15s for TLS connection...")
time.sleep(15)

for cmd in [
    'cat /Agent/etc/nftls.status 2>/dev/null',
    'ss -tlnp | grep 19996',
    'ps -e | grep -E "tsensor|nftls" | head -5',
    'ls -la /data/flow/1/nfcapd.current 2>/dev/null',
]:
    print(f"\n=== {cmd[:40]} ===")
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')[:500]
    err = e.read().decode('utf-8', errors='replace')[:200]
    if out: print(out)
    if err: print('ERR:', err)
c.close()