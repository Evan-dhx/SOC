import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check all devices in the config
i, o, e = c.exec_command(r'grep -E "id:|interface:|name:" /Agent/data/config | head -20', timeout=30)
print('All devices:', o.read().decode()[:1000])

# Check running tsensor params
i, o, e = c.exec_command("cat /proc/26355/cmdline 2>/dev/null | tr '\\0' ' '; echo", timeout=30)
print('Running tsensor:', o.read().decode()[:300])

c.close()