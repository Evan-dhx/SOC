import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check syslog for config_pusher output
items = [
    ('config_pusher log', 'tail -20 /var/log/messages 2>/dev/null | grep -i "push\|config_pusher\|restart\|probe" | tail -10'),
    ('config_updater log', 'tail -10 /var/log/messages 2>/dev/null | grep -i config_updater'),
    ('actl log', 'tail -10 /var/log/messages 2>/dev/null | grep -i actl'),
    ('tsensor', 'ps -e | grep sensor; echo ---; ps -e | grep probe'),
    ('config file', 'grep -E "interface|filter|name:" /Agent/data/config | head -5'),
]
for label, cmd in items:
    print(f'\n[{label}]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:600])
    if err: print(f'ERR: {err[:200]}')
c.close()