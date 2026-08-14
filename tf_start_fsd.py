import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('start fsd', 'nohup /home/Agent/bin/fsd > /dev/null 2>&1 &; sleep 3; pgrep -x fsd; echo "fsd_pid=$?"'),
    ('check processes', 'ps -e | grep -E "fsd|nftls|probe|fcapd" | head -10'),
    ('log last 5', 'tail -5 /Agent/data/log'),
    ('verify nftls listening', 'ss -tlnp | grep 199'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()