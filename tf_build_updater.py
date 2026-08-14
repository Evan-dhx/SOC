import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\config_updater.cpp', '/root/SOC/ly_analyser_src/agent/handlers/config_updater.cpp')
sftp.close()
print('Synced config_updater.cpp')

# Compile
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f config_updater.o config_updater && make config_updater 2>&1 | tail -15', timeout=120)
out = o.read().decode('utf-8', errors='replace')
print('Compile:', out[:1000])
err = e.read().decode('utf-8', errors='replace')
if err: print('ERR:', err[:300])

# Deploy
i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /home/Agent/cmd/; cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/; ls -la /Agent/cmd/config_updater; md5sum /Agent/cmd/config_updater', timeout=30)
print('Deploy:', o.read().decode()[:300])
c.close()

# Test
print('Waiting for next test...')
time.sleep(2)

c2 = paramiko.SSHClient()
c2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c2.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

i, o, e = c2.exec_command("echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; wc -c /Agent/data/config", timeout=30)
print('Config restored:', o.read().decode()[:100])

# curl POST test
i, o, e = c2.exec_command("curl -s -X POST -H 'Content-Type: text/plain' -d 'dev { id: 1 name: \"test\" psk: \"abc123\" }' http://127.0.0.1:10081/config_updater 2>&1; echo; echo CURL_EXIT=$?", timeout=30)
print('Curl:', o.read().decode()[:200])

# Check config
i, o, e = c2.exec_command('echo === after curl ===; cat /Agent/data/config; echo; wc -c /Agent/data/config; ls -la /Agent/data/config', timeout=30)
print(o.read().decode()[:500])

# Check agent log for debug messages
i, o, e = c2.exec_command('tail -5 /Agent/data/log', timeout=30)
print('Log:', o.read().decode()[:500])

c2.close()