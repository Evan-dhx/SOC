import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Sync and rebuild config_updater
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\config_updater.cpp',
         '/root/SOC/ly_analyser_src/agent/handlers/config_updater.cpp')
sftp.close()
print('Uploaded config_updater.cpp')

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f config_updater.o && make config_updater 2>&1 | tail -5', timeout=120)
print('Compile:', o.read().decode()[:300])

i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/; ls -la /Agent/cmd/config_updater', timeout=30)
print('Deploy:', o.read().decode()[:200])

# Run config_pusher
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | head -3; echo ===; wc -c /Agent/data/config; tail -2 /var/log/messages 2>/dev/null | grep config_updater', timeout=120)
print('Push and check:', o.read().decode()[:500])

# Check tsensor.conf was updated
time.sleep(3)
i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null; echo ===; ps -e | grep -c tsensor', timeout=30)
print('tsensor.conf and count:', o.read().decode()[:500])

c.close()
print('\nDone')