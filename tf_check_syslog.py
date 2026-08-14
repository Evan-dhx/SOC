import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

i, o, e = c.exec_command('tail -10 /var/log/messages 2>/dev/null | grep config_updater', timeout=30)
print(o.read().decode()[:1000])
c.close()