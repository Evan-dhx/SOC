import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check syslog for config_updater messages
i, o, e = c.exec_command('grep "config_updater" /var/log/messages 2>/dev/null | tail -10', timeout=30)
print('=== syslog config_updater ===')
print(o.read().decode()[:1000])

# Also check /Agent/data/log for config_updater
i, o, e = c.exec_command('grep "config_updater\|POST\|parse\|Raw\|atomic\|write" /Agent/data/log 2>/dev/null | tail -10', timeout=30)
print('=== agent log ===')
print(o.read().decode()[:500])

# Check journalctl for recent 
i, o, e = c.exec_command('journalctl -u httpd -n 20 --no-pager 2>/dev/null | grep -i "config_updater\|POST\|config" | tail -10', timeout=30)
print('=== journalctl httpd ===')
print(o.read().decode()[:1000])

# Restore config, try CGI simulation POST (which worked before)
i, o, e = c.exec_command("echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; wc -c /Agent/data/config", timeout=30)
print('=== restore ===')
print(o.read().decode()[:100])

# CGI sim POST
i, o, e = c.exec_command("echo 'dev { id: 1 name: \"test\" psk: \"abc123\" }' > /tmp/post_test.txt; CONTENT_LENGTH=$(wc -c < /tmp/post_test.txt) REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=POST /Agent/cmd/config_updater < /tmp/post_test.txt 2>&1", timeout=30)
print('=== CGI sim POST ===')
print(o.read().decode()[:500])

# Check config after CGI sim
i, o, e = c.exec_command('echo === after CGI sim ===; cat /Agent/data/config; echo; wc -c /Agent/data/config', timeout=30)
print(o.read().decode()[:500])

c.close()