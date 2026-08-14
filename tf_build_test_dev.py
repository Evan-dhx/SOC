import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\config_updater.cpp',
         '/root/SOC/ly_analyser_src/agent/handlers/config_updater.cpp')
sftp.close()

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f config_updater.o && make config_updater 2>&1 | tail -3', timeout=120)
r = o.read().decode()
print('Build:', r[:200])
if 'Error' not in r and 'error' not in r:
    i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/', timeout=30)
    i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 > /dev/null', timeout=120)
    time.sleep(2)
    i, o, e = c.exec_command('wc -c /Agent/data/config /Agent/data/config.dev; echo ---; grep -c "^mo {" /Agent/data/config.dev 2>/dev/null', timeout=30)
    print('Mo count in dev:', o.read().decode()[:200])
    i, o, e = c.exec_command('grep "^mo {\|^event_config {" /Agent/data/config.dev 2>/dev/null', timeout=30)
    mo_lines = o.read().decode()[:200]
    print('Filtered blocks:', mo_lines if mo_lines else 'NONE (good!)')
    if not mo_lines.strip():
        # Now config.dev should be parseable - run actl restart
        i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | head -10', timeout=120)
        print('Push:', o.read().decode()[:800])
        time.sleep(3)
        i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -3', timeout=30)
        print('tsensor.conf:', o.read().decode()[:200])
c.close()