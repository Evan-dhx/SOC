import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check config.dev content - does it have event blocks?
i, o, e = c.exec_command('grep -c "event {" /Agent/data/config.dev', timeout=30)
print('event count in config.dev:', o.read().decode()[:100])

i, o, e = c.exec_command('wc -l /Agent/data/config.dev; tail -5 /Agent/data/config.dev', timeout=30)
print('config.dev tail:', o.read().decode()[:200])

# Check if config.dev is parseable now
i, o, e = c.exec_command('strings /Agent/lib/libcommon.so | grep -c "config.Device.psk"', timeout=30)
print('psk desc in Agent lib:', o.read().decode()[:100])

c.close()