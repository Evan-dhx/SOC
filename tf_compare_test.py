import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Test 1: CGI simulation as root (should work)
i, o, e = c.exec_command('echo "controller { host: \"127.0.0.1\" port: \"10081\" }" > /Agent/data/config; chown root:root /Agent/data/config; wc -c /Agent/data/config', timeout=30)
print('Restored:', o.read().decode()[:100])

i, o, e = c.exec_command('echo "dev { id: 1 name: \"test\" psk: \"abc123\" }" > /tmp/pt.txt; CONTENT_LENGTH=$(wc -c < /tmp/pt.txt) REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=POST /Agent/cmd/config_updater < /tmp/pt.txt 2>&1 | head -3', timeout=30)
print('CGI sim:', o.read().decode()[:200])

i, o, e = c.exec_command('cat /Agent/data/config; echo; wc -c /Agent/data/config', timeout=30)
print('After CGI sim:', o.read().decode()[:200])

# Test 2: curl POST
time.sleep(2)
i, o, e = c.exec_command('echo "controller { host: \"127.0.0.1\" port: \"10081\" }" > /Agent/data/config; chown root:root /Agent/data/config', timeout=30)

i, o, e = c.exec_command('curl -s -X POST -H "Content-Type: text/plain" -d "dev { id: 1 name: \"test\" psk: \"abc123\" }" http://127.0.0.1:10081/config_updater 2>&1; echo; echo EX=$?', timeout=30)
print('Curl result:', o.read().decode()[:200])

time.sleep(1)
i, o, e = c.exec_command('cat /Agent/data/config; echo; wc -c /Agent/data/config; ls -la /Agent/data/config', timeout=30)
print('After curl:', o.read().decode()[:300])

i, o, e = c.exec_command('tail -4 /var/log/messages 2>/dev/null | grep config_updater', timeout=30)
print('Recent syslog:', o.read().decode()[:500])

c.close()