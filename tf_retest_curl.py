import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Restore config
i, o, e = c.exec_command("echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; chmod 644 /Agent/data/config; ls -la /Agent/data/config", timeout=30)
print('Restored:', o.read().decode()[:200])

# Step 2: curl POST 
i, o, e = c.exec_command("curl -s -X POST -H 'Content-Type: text/plain' -d 'dev { id: 1 name: \"test\" psk: \"abc123\" }' http://127.0.0.1:10081/config_updater 2>&1; echo; echo CURL_EXIT=$?", timeout=30)
print('Curl:', o.read().decode()[:200])

# Step 3: Check config
i, o, e = c.exec_command('ls -la /Agent/data/config; wc -c /Agent/data/config; cat /Agent/data/config', timeout=30)
print('After curl:', o.read().decode()[:500])

# Step 4: Check syslog for new debug messages
i, o, e = c.exec_command('tail -5 /var/log/messages 2>/dev/null | grep config_updater', timeout=30)
print('Syslog:', o.read().decode()[:500])

c.close()