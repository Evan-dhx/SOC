import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Restore with correct quoting
i, o, e = c.exec_command("printf 'controller { host: \"127.0.0.1\" port: \"10081\" }\\n' > /Agent/data/config; rm -f /Agent/data/config.tmp; ls -la /Agent/data/config; od -c /Agent/data/config | head -3", timeout=30)
print('Restored:', o.read().decode()[:300])

# Test curl POST
time.sleep(2)
i, o, e = c.exec_command('curl -s -X POST -H "Content-Type: text/plain" -d "dev { id: 1 name: \"test\" psk: \"abc123\" }" http://127.0.0.1:10081/config_updater 2>&1; echo; echo EX=$?', timeout=30)
print('Curl:', o.read().decode()[:200])

time.sleep(1)
i, o, e = c.exec_command('echo === file ===; od -c /Agent/data/config; echo; wc -c /Agent/data/config; ls -la /Agent/data/config', timeout=30)
print(o.read().decode()[:500])

i, o, e = c.exec_command('tail -3 /var/log/messages 2>/dev/null | grep config_updater', timeout=30)
print('Syslog:', o.read().decode()[:300])

c.close()