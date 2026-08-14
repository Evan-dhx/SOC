import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ('cat /Agent/data/config 2>/dev/null'),
    ('ls -la /home/Server/bin/config_pusher'),
    ('/home/Server/bin/config_pusher > /tmp/pusher_test.log 2>&1; echo "EXIT=$?"'),
    ('cat /tmp/pusher_test.log 2>/dev/null'),
    ('cat /Agent/data/config 2>/dev/null'),
]
for cmd in cmds:
    print(f'\n=== {cmd[:60]} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1000])
    if err: print(f'STDERR: {err[:500]}')
client.close()