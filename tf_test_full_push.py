import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Run config_pusher
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1; echo EX=$?', timeout=120)
print('Push:', o.read().decode()[:1000])

# Check syslog for restart
time.sleep(3)
items = [
    ('config_pusher log', 'tail -10 /var/log/messages 2>/dev/null | grep -E "restart|config_pusher|Push" | tail -5'),
    ('config_updater log', 'tail -5 /var/log/messages 2>/dev/null | grep config_updater'),
    ('actl log', 'tail -5 /var/log/messages 2>/dev/null | grep actl'),
    ('tsensor/probe processes', 'ps -e | grep -E "sensor|probe|nftls"'),
]
for l, cmd in items:
    print(f'\n[{l}]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode()[:600]
    if out: print(out)

# Verify config was pushed
i, o, e = c.exec_command('tail -3 /var/log/messages 2>/dev/null | grep config_updater', timeout=30)
print('\n[config_updater recent]')
print(o.read().decode()[:500])

c.close()