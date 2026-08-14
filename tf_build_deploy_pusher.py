import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Sync modified config_pusher.cpp
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_server\src\server\config_pusher.cpp',
         '/root/SOC/ly_server_src/server/config_pusher.cpp')
sftp.close()
print('Uploaded config_pusher.cpp')

# Compile
i, o, e = c.exec_command('cd /root/SOC/ly_server_src/server && make config_pusher 2>&1 | tail -10', timeout=120)
print('Compile:', o.read().decode()[:500])

# Deploy
i, o, e = c.exec_command('cp /root/SOC/ly_server_src/server/config_pusher /Server/bin/; ls -la /Server/bin/config_pusher', timeout=30)
print('Deploy:', o.read().decode()[:200])

# Run a manual push to test
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1; echo EX=$?', timeout=120)
print('Manual push:', o.read().decode()[:1000])

# Check syslog
i, o, e = c.exec_command('tail -10 /var/log/messages 2>/dev/null | grep -E "restart|config_pusher|Restart" | tail -5', timeout=30)
print('Syslog:', o.read().decode()[:500])

c.close()
print('\nDone')