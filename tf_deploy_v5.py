import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\config\cached_config.cpp',
         '/root/SOC/ly_analyser_src/agent/config/cached_config.cpp')
sftp.close()

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/config && make 2>&1 | tail -3', timeout=120)
r = o.read().decode()
print('Config lib:', r[:300])
if 'Error' in r or 'error' in r:
    print('Config lib BUILD FAILED')
    c.close()
    sys.exit(1)

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f config_updater.o && make config_updater actl 2>&1 | tail -5', timeout=120)
r = o.read().decode()
print('Handlers:', r[:300])
if 'Error' in r or 'error' in r:
    print('Handlers BUILD FAILED')
    c.close()
    sys.exit(1)

i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/')
i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/')

i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | head -10', timeout=120)
print('Push output:', o.read().decode()[:800])

time.sleep(3)
i, o, e = c.exec_command('wc -c /Agent/data/config /Agent/data/config.dev 2>/dev/null', timeout=30)
r = o.read().decode()
print('Files:', r)
dev_conf_exists = 'config.dev' in r

i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -3', timeout=30)
print('tsensor.conf:', o.read().decode()[:300])

i, o, e = c.exec_command('echo -n "PID: "; pidof tsensor 2>/dev/null; echo; cat /proc/$(pidof tsensor 2>/dev/null)/cmdline 2>/dev/null | tr "\\0" " "', timeout=30)
print('Running tsensor:', o.read().decode()[:300])
c.close()