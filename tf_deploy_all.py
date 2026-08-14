import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()

# Sync all modified files
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\config\local_disk_config.cpp',
         '/root/SOC/ly_analyser_src/agent/config/local_disk_config.cpp')
print('Synced local_disk_config.cpp')

sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\config_updater.cpp',
         '/root/SOC/ly_analyser_src/agent/handlers/config_updater.cpp')
print('Synced config_updater.cpp')

sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\actl.cpp',
         '/root/SOC/ly_analyser_src/agent/handlers/actl.cpp')
print('Synced actl.cpp')
sftp.close()

# Rebuild all
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/config && make 2>&1 | tail -3', timeout=120)
print('Build config lib:', o.read().decode()[:300])

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f actl.o config_updater.o && make actl config_updater 2>&1 | tail -5', timeout=120)
print('Build handlers:', o.read().decode()[:500])

# Deploy
i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/ && cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/ && echo DEPLOYED', timeout=30)
print('Deploy:', o.read().decode()[:200])

# Run config_pusher
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | head -5', timeout=120)
print('Push:', o.read().decode()[:500])

time.sleep(5)

# Check everything
i, o, e = c.exec_command("ps -e | grep -E 'sensor|probe'; echo ---; cat /Agent/etc/tsensor.conf 2>/dev/null | head -4", timeout=30)
print('After push:', o.read().decode()[:500])

c.close()
print('\nDone')