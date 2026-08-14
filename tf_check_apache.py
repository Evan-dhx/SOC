import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check Apache config for port 10081
i, o, e = c.exec_command('grep -rn "10081\|config_updater\|actl\|ScriptAlias\|CGIPassAuth" /etc/httpd/conf* /etc/httpd/conf.d/ 2>/dev/null | head -30', timeout=30)
print('Apache config:', o.read().decode()[:2000])

# Also check what happens with config_updater now
i, o, e = c.exec_command('curl -s -o /dev/null -w "%{http_code}" -X POST -d "test" http://127.0.0.1:10081/config_updater', timeout=30)
print('config_updater HTTP:', o.read().decode()[:100])

c.close()