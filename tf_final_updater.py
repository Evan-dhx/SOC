import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\config_updater.cpp', '/root/SOC/ly_analyser_src/agent/handlers/config_updater.cpp')
sftp.close()

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f config_updater.o && make config_updater 2>&1 | tail -5', timeout=120)
print('Build:', o.read().decode()[:500])

i, o, e = c.exec_command('cp config_updater /Agent/cmd/ && cp config_updater /home/Agent/cmd/ && ls -la /Agent/cmd/config_updater', timeout=30)
print('Deploy:', o.read().decode()[:200])

# Restore config
i, o, e = c.exec_command("echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; rm -f /Agent/data/config.tmp; chmod 644 /Agent/data/config; ls -la /Agent/data/config", timeout=30)
print('Restored:', o.read().decode()[:200])

time.sleep(2)

# Test curl POST (minimal - single dev section)
i, o, e = c.exec_command("curl -s -X POST -H 'Content-Type: text/plain' -d 'dev { id: 1 name: \"test\" psk: \"abc123\" }' http://127.0.0.1:10081/config_updater 2>&1; echo; echo CURL_EXIT=$?", timeout=30)
print('Curl1:', o.read().decode()[:200])

time.sleep(1)
i, o, e = c.exec_command('ls -la /Agent/data/config; wc -c /Agent/data/config; cat /Agent/data/config', timeout=30)
print('After curl1:', o.read().decode()[:500])

# Test curl POST with full config (what config_pusher sends)
i, o, e = c.exec_command("echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; wc -c /Agent/data/config", timeout=30)
print('Restored2:', o.read().decode()[:100])

time.sleep(1)

i, o, e = c.exec_command("curl -s -X POST -H 'Content-Type: text/plain' -d 'controller { host: \"127.0.0.1\" port: \"10081\" } dev { id: 1 name: \"test\" psk: \"abc123\" }' http://127.0.0.1:10081/config_updater 2>&1; echo; echo CURL_EXIT=$?", timeout=30)
print('Curl2:', o.read().decode()[:200])

time.sleep(1)
i, o, e = c.exec_command('ls -la /Agent/data/config; wc -c /Agent/data/config; cat /Agent/data/config', timeout=30)
print('After curl2:', o.read().decode()[:500])

c.close()