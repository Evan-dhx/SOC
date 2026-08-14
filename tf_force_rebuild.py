import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Force full rebuild: remove binary first, then recompile config lib and actl
i, o, e = c.exec_command('rm -f /root/SOC/ly_analyser_src/agent/handlers/actl /root/SOC/ly_analyser_src/agent/handlers/actl.o', timeout=30)
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/config && make 2>&1 | tail -2', timeout=120)
print('Config lib:', o.read().decode()[:200])

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && make actl 2>&1 | tail -5', timeout=120)
r = o.read().decode()
print('Actl build:', r[:300])
if 'Error' not in r and 'error' not in r:
    # Verify strings
    i, o, e = c.exec_command('strings /root/SOC/ly_analyser_src/agent/handlers/actl | grep "config.dev" | head -3', timeout=30)
    r2 = o.read().decode()
    print('config.dev in binary:', r2.strip() if r2.strip() else 'NOT FOUND!')
    
    if r2.strip():
        i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/', timeout=30)
        i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | tail -5', timeout=120)
        print('Push:', o.read().decode()[:500])
        time.sleep(3)
        i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -3', timeout=30)
        print('tsensor.conf:', o.read().decode()[:200])
c.close()