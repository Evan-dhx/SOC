import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check full config_pusher output
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1', timeout=120)
print('Full push output:')
print(o.read().decode()[:3000])

# Check config and tsensor
i, o, e = c.exec_command('grep -E "interface|collector" /Agent/etc/tsensor.conf 2>/dev/null', timeout=30)
print('\ntsensor.conf:', o.read().decode()[:200])

i, o, e = c.exec_command('grep -E "interface|port:" /Agent/data/config | head -4', timeout=30)
print('data/config:', o.read().decode()[:200])

i, o, e = c.exec_command('ps -e | grep -c tsensor; echo -; pidof tsensor 2>/dev/null', timeout=30)
print('tsensor:', o.read().decode()[:100])

c.close()