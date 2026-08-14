import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('probe available', 'which fprobe nprobe 2>/dev/null; echo "---"; ls -la /usr/local/bin/fprobe /usr/local/bin/nprobe /usr/bin/fprobe /usr/bin/nprobe 2>/dev/null'),
    ('check probe.conf', 'cat /Agent/etc/probe.conf 2>/dev/null | head -30'),
    ('interface check', 'ip addr show | grep -E "ens33|eth0|ens" | head -5'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()

print('\nWaiting 65s for fsd cycle...')
time.sleep(65)

client2 = paramiko.SSHClient()
client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client2.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
for label, cmd in [
    ('log after wait', 'tail -15 /Agent/data/log'),
    ('processes after wait', 'ps -e | grep -E "fsd|nftls|probe|fcapd" | head -10'),
    ('UDP listener', 'ss -uln | grep -E "999[56]"'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client2.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client2.close()