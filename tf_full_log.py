import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Get the FULL error log
i, o, e = c.exec_command('tail -10 /var/log/httpd/ly_error_log 2>/dev/null', timeout=30)
print('Full tail:', o.read().decode()[:2000])

c.close()