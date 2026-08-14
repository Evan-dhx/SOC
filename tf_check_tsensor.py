import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('tsensor setup', 'cat /Agent/etc/tsensor.conf 2>/dev/null; echo "==="; cat /Agent/etc/tsensor_start.sh 2>/dev/null; echo "==="; systemctl cat tsensor 2>/dev/null'),
    ('former probe conf', 'find /Agent/etc -name "*.conf" -o -name "probe*" 2>/dev/null; echo "---"; ls -la /Agent/etc/'),
    ('check cmd directory', 'ls /Agent/cmd/; echo "---"; ls /Agent/bin/'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()