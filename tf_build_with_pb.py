import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check common Makefile and rebuild libcommon
i, o, e = c.exec_command('cat /root/SOC/ly_analyser_src/common/Makefile | head -40', timeout=30)
print('Makefile:', o.read().decode()[:500])

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/common && make libcommon.a 2>&1 | tail -10', timeout=120)
print('libcommon.a build:', o.read().decode()[:500])

# Then rebuild config.a and actl with the new libcommon
i, o, e = c.exec_command('rm -f /root/SOC/ly_analyser_src/agent/config/*.o /root/SOC/ly_analyser_src/agent/config/config.a', timeout=30)
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/config && make 2>&1 | tail -3', timeout=120)
print('config.a:', o.read().decode()[:200])

i, o, e = c.exec_command('rm -f /root/SOC/ly_analyser_src/agent/handlers/actl /root/SOC/ly_analyser_src/agent/handlers/actl.o', timeout=30)
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && make actl 2>&1 | tail -5', timeout=120)
r = o.read().decode()
print('actl:', r[:300])
if 'Error' not in r and 'error' not in r:
    i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/', timeout=30)
    i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | tail -5', timeout=120)
    print('Push:', o.read().decode()[:500])
    time.sleep(3)
    import time
    i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -3', timeout=30)
    print('tsensor.conf:', o.read().decode()[:200])
c.close()