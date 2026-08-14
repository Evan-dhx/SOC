import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Sync modified actl.cpp
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\actl.cpp',
         '/root/SOC/ly_analyser_src/agent/handlers/actl.cpp')
sftp.close()
print('Uploaded actl.cpp')

# Rebuild actl
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f actl.o && make actl 2>&1 | tail -10', timeout=120)
print('Compile:', o.read().decode()[:500])

# Deploy
i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/', timeout=30)
print('Deploy done')

# Run config_pusher to trigger full flow
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1; echo EX=$?', timeout=120)
print('Push:', o.read().decode()[:1500])

time.sleep(3)

# Check tsensor
i, o, e = c.exec_command("ps -e | grep -E 'sensor|probe' 2>/dev/null; echo ---; cat /Agent/etc/tsensor.conf 2>/dev/null", timeout=30)
print('After push:', o.read().decode()[:800])

c.close()
print('\nDone')