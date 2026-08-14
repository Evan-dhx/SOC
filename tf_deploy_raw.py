import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

i, o, e = c.exec_command('ls -la /root/SOC/ly_analyser_src/agent/handlers/config_updater', timeout=30)
print('Binary:', o.read().decode()[:200])

i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/ && cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /home/Agent/cmd/ && ls -la /Agent/cmd/config_updater', timeout=30)
print('Deploy:', o.read().decode()[:200])

i, o, e = c.exec_command('chown root:root /Agent/data/config 2>/dev/null; echo "controller { host: \"127.0.0.1\" port: \"10081\" }" > /Agent/data/config; rm -f /Agent/data/config.tmp; ls -la /Agent/data/config', timeout=30)
print('Restored:', o.read().decode()[:200])

time.sleep(2)
i, o, e = c.exec_command('curl -s -X POST -H "Content-Type: text/plain" -d "dev { id: 1 name: \"test\" psk: \"abc123\" }" http://127.0.0.1:10081/config_updater 2>&1; echo; echo EXIT=$?', timeout=30)
print('Curl:', o.read().decode()[:200])

time.sleep(1)
i, o, e = c.exec_command('ls -la /Agent/data/config; cat /Agent/data/config; echo; wc -c /Agent/data/config', timeout=30)
print('After:', o.read().decode()[:500])

# Also test with full config
i, o, e = c.exec_command('chown root:root /Agent/data/config 2>/dev/null; echo "controller { host: \"127.0.0.1\" port: \"10081\" }" > /Agent/data/config; rm -f /Agent/data/config.tmp', timeout=30)
time.sleep(1)
i, o, e = c.exec_command('curl -s -X POST -H "Content-Type: text/plain" -d "controller { host: \"127.0.0.1\" port: \"10081\" } dev { id: 1 name: \"test\" psk: \"abc123\" }" http://127.0.0.1:10081/config_updater 2>&1; echo; echo EXIT=$?', timeout=30)
time.sleep(1)
i, o, e = c.exec_command('echo --- full config test ---; cat /Agent/data/config; echo; wc -c /Agent/data/config; ls -la /Agent/data/config', timeout=30)
print('After full:', o.read().decode()[:500])

c.close()