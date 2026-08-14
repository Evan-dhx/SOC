import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check the 404 more carefully - test config_updater and actl directly
items = [
    ('config_updater curl', 'curl -s -X POST -d "test" http://127.0.0.1:10081/config_updater 2>&1 | head -3'),
    ('actl curl', 'curl -s -X POST -d "test" http://127.0.0.1:10081/actl 2>&1 | head -3'),
    ('httpd on 10081', 'ss -tlnp | grep 10081'),
    ('cmd dir ls', 'ls -la /Agent/cmd/ 2>/dev/null; echo ===; ls -la /home/Agent/cmd/ 2>/dev/null'),
]
for label, cmd in items:
    print(f'\n[{label}]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:500])
    if err: print(f'ERR: {err[:200]}')
c.close()