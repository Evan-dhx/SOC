import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Deploy and test
i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/', timeout=30)
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1', timeout=120)
print('Push:', o.read().decode()[:1000])

time.sleep(3)
i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -4; echo ===; ps -e | grep tsensor | wc -l', timeout=30)
print('Result:', o.read().decode()[:400])

c.close()