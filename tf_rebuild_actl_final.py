import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Force full rebuild of actl with latest config lib
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f actl.o && make actl 2>&1 | tail -3', timeout=120)
r = o.read().decode()
print('Build actl:', r[:300])
if 'Error' not in r and 'error' not in r:
    i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/')
    i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | tail -5', timeout=120)
    print('Push:', o.read().decode()[:500])
    time.sleep(3)
    i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -3', timeout=30)
    print('tsensor.conf:', o.read().decode()[:200])
    i, o, e = c.exec_command('ps -e | grep -c tsensor; echo; cat /proc/$(pidof tsensor)/cmdline 2>/dev/null | tr "\\0" " "', timeout=30)
    print('Running:', o.read().decode()[:200])
else:
    print('FAIL')
c.close()