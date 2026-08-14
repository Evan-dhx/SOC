import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Run config_pusher again, see full output
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1', timeout=120)
out = o.read().decode()
print('Push output length:', len(out))
print(out[:2000])

time.sleep(5)

# Check processes
i, o, e = c.exec_command("ps -ef | grep -E 'sensor|probe' | grep -v grep; echo COUNT:; ps -e | grep -c tsensor; echo --tsensor.conf--; cat /Agent/etc/tsensor.conf 2>/dev/null; echo --config--; head -5 /Agent/data/config", timeout=30)
print('\nAfter push:', o.read().decode()[:1000])

c.close()