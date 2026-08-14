import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('tsensor config', 'cat /Agent/etc/tsensor.conf 2>/dev/null; echo "==="'),
    ('tsensor start script', 'cat /Agent/etc/tsensor_start.sh 2>/dev/null'),
    ('systemd tsensor', 'systemctl cat tsensor 2>/dev/null'),
    ('Agent etc files', 'ls -la /Agent/etc/'),
    ('Agent bin files', 'ls -la /Agent/bin/'),
    ('Agent cmd files', 'ls -la /Agent/cmd/'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()