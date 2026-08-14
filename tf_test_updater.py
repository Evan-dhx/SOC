import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# First fix the config file
i, o, e = c.exec_command("echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; wc -c /Agent/data/config", timeout=30)
print('Config restored:', o.read().decode()[:200])

# Test config_updater GET
i, o, e = c.exec_command("REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=GET /home/Agent/cmd/config_updater 2>/dev/null | head -5", timeout=30)
print('GET response:', o.read().decode()[:300])

# Test POST with simple valid protobuf text
i, o, e = c.exec_command("echo 'dev { id: 1 name: \"test\" psk: \"abc123\" }' > /tmp/post_test.txt; CONTENT_LENGTH=$(wc -c < /tmp/post_test.txt) REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=POST /home/Agent/cmd/config_updater < /tmp/post_test.txt 2>&1", timeout=30)
print('POST result:', o.read().decode()[:500])

# Check config after POST
i, o, e = c.exec_command("echo 'Config after POST:'; cat /Agent/data/config; echo; wc -c /Agent/data/config", timeout=30)
print(o.read().decode()[:500])

c.close()