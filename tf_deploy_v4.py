import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()

files = [
    (r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\config_updater.cpp',
     '/root/SOC/ly_analyser_src/agent/handlers/config_updater.cpp'),
    (r'd:\QorderProject\SOC\ly_analyser\src\agent\config\cached_config.cpp',
     '/root/SOC/ly_analyser_src/agent/config/cached_config.cpp'),
]
for local, remote in files:
    sftp.put(local, remote)
    print(f'Synced {remote.split("/")[-1]}')
sftp.close()

# Build config lib
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/config && make 2>&1 | tail -3', timeout=120)
r = o.read().decode()
print('Config lib:', r[:300])
if 'Error' in r:
    print('BUILD FAILED')
    c.close()
    sys.exit(1)

# Build config_updater
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f config_updater.o && make config_updater 2>&1 | tail -3', timeout=120)
r = o.read().decode()
print('config_updater:', r[:200])

# Deploy
i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/ && cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/', timeout=30)

# Run pusher
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | head -10', timeout=120)
print('Push:', o.read().decode()[:800])

time.sleep(3)
i, o, e = c.exec_command('wc -c /Agent/data/config /Agent/data/config.dev 2>/dev/null; echo ---; cat /Agent/etc/tsensor.conf 2>/dev/null | head -3', timeout=30)
print('Files:', o.read().decode()[:500])

i, o, e = c.exec_command('ps -e | grep -c tsensor; echo PIDs:; pidof tsensor', timeout=30)
print('tsensor:', o.read().decode()[:100])

c.close()
print('\nDone')