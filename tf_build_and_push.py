import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\actl.cpp',
         '/root/SOC/ly_analyser_src/agent/handlers/actl.cpp')
sftp.close()

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f actl.o && make actl 2>&1 | tail -5', timeout=120)
r = o.read().decode()
print('Build:', r[:500])
if 'Error' not in r:
    i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/', timeout=30)
    i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | head -5', timeout=120)
    print('Push:', o.read().decode()[:500])
    time.sleep(3)
    i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -4', timeout=30)
    print('tsensor.conf:', o.read().decode()[:300])
    i, o, e = c.exec_command('ps -e | grep -c tsensor; echo --; systemctl is-active tsensor', timeout=30)
    print('tsensor:', o.read().decode()[:100])
else:
    print('Build failed!')
c.close()