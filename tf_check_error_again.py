import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

i, o, e = c.exec_command('tail -5 /var/log/httpd/ly_error_log 2>/dev/null', timeout=30)
print('Apache error:', o.read().decode()[:500])

# Check the exact line in config.dev that fails
i, o, e = c.exec_command("sed -n '17,21p' /Agent/data/config.dev", timeout=30)
print('Config.dev lines 17-21:', o.read().decode()[:300])

c.close()