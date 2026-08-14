import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check raw file content
i, o, e = c.exec_command('od -c /Agent/data/config', timeout=30)
print('od:', o.read().decode()[:300])

# Write file with explicit quoting
i, o, e = c.exec_command("printf 'controller { host: \"127.0.0.1\" port: \"10081\" }\\n' > /Agent/data/config; wc -c /Agent/data/config; od -c /Agent/data/config", timeout=30)
print('printf:', o.read().decode()[:300])

# Now CGI sim POST
i, o, e = c.exec_command('printf "dev { id: 1 name: \\"test\\" psk: \\"abc123\\" }\\n" > /tmp/pt2.txt; od -c /tmp/pt2.txt', timeout=30)
print('post data:', o.read().decode()[:200])

i, o, e = c.exec_command('CONTENT_LENGTH=$(wc -c < /tmp/pt2.txt) REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=POST /Agent/cmd/config_updater < /tmp/pt2.txt 2>&1 | head -3', timeout=30)
print('CGI POST:', o.read().decode()[:200])

i, o, e = c.exec_command('od -c /Agent/data/config; echo; wc -c /Agent/data/config', timeout=30)
print('After POST:', o.read().decode()[:300])

c.close()