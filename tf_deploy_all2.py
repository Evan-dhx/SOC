import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\config\local_disk_config.cpp',
         '/root/SOC/ly_analyser_src/agent/config/local_disk_config.cpp')
sftp.close()
print('Sync OK')

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/config && make 2>&1 | tail -3', timeout=120)
r = o.read().decode()
print('Config lib:', r[:300])
if 'Error' in r:
    print('BUILD FAILED')
    c.close()
    sys.exit(1)

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f actl.o config_updater.o && make actl config_updater 2>&1 | tail -5', timeout=120)
r = o.read().decode()
print('Handlers:', r[:500])

i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/ && cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/ && echo DEPLOY_OK', timeout=30)
print('Deploy:', o.read().decode()[:100])

i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | head -5', timeout=120)
print('Push:', o.read().decode()[:500])

time.sleep(3)
i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -4; echo ---; ps -e | grep -c tsensor', timeout=30)
print('Result:', o.read().decode()[:500])
c.close()