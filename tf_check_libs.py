import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check config_updater library linkage
i, o, e = c.exec_command('ldd /Agent/cmd/config_updater | grep proto; echo ---; ldd /Server/bin/config_pusher | grep proto', timeout=30)
print('Libs:', o.read().decode()[:300])

# Now run config_pusher and check what happens
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1; echo EX=$?; echo ===; wc -c /Agent/data/config; tail -3 /var/log/messages 2>/dev/null | grep config_updater', timeout=120)
print('Push:', o.read().decode()[:800])

c.close()