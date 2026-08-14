import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

items = [
    ('tsensor processes', 'ps -e | grep -E "sensor|probe" 2>/dev/null'),
    ('nftls', 'ps -e | grep nftls 2>/dev/null | head -3'),
    ('config_updater log', 'tail -3 /var/log/messages 2>/dev/null | grep config_updater'),
    ('actl log', 'tail -5 /var/log/messages 2>/dev/null | grep -i actl'),
    ('old PID 26355', 'ls -la /proc/26355/exe 2>/dev/null && echo OLD_ALIVE || echo OLD_GONE'),
]
for l, cmd in items:
    print(f'\n[{l}]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode()[:500]
    if out: print(out)
c.close()