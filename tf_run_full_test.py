import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Run config_pusher again
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1; echo EX=$?', timeout=120)
print('Push result:', o.read().decode()[:1500])

time.sleep(3)

# Check tsensor processes
i, o, e = c.exec_command("ps -ef | grep -E 'sensor|probe' | grep -v grep; echo ---; pidof tsensor", timeout=30)
print('TSensor processes:', o.read().decode()[:500])

# Check config_updater and actl logs
i, o, e = c.exec_command('tail -10 /var/log/messages 2>/dev/null | grep -E "config_updater|actl" | tail -5', timeout=30)
print('Recent logs:', o.read().decode()[:500])

c.close()
print('\nDone')