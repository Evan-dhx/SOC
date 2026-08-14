import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check config file state
i, o, e = c.exec_command('ls -la /Agent/data/config; wc -c /Agent/data/config; od -c /Agent/data/config | head -3', timeout=30)
print('Config state:', o.read().decode()[:500])

# Run config_pusher to restore
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | head -3; echo; wc -c /Agent/data/config', timeout=120)
print('Push restore:', o.read().decode()[:500])

# Check config again
i, o, e = c.exec_command('grep -c "dev {" /Agent/data/config 2>/dev/null; wc -c /Agent/data/config', timeout=30)
print('After push:', o.read().decode()[:200])

c.close()