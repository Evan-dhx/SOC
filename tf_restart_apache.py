import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Restart Apache to clear cgid cache
i, o, e = c.exec_command('apachectl restart 2>&1; sleep 2; systemctl is-active httpd', timeout=30)
print('Apache restart:', o.read().decode()[:200])

# Run config_pusher again
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1', timeout=120)
print('Push:', o.read().decode()[:1000])

time.sleep(3)
i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -3', timeout=30)
print('tsensor.conf:', o.read().decode()[:200])

c.close()