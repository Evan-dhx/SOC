import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check more thoroughly for config.dev
i, o, e = c.exec_command('strings /root/SOC/ly_analyser_src/agent/handlers/actl | grep -i "dev" | head -10', timeout=30)
print('dev strings:', o.read().decode()[:500])

# Check the object file directly
i, o, e = c.exec_command('strings /root/SOC/ly_analyser_src/agent/config/cached_config.o | grep -i dev | head -10', timeout=30)
print('dev in obj:', o.read().decode()[:500])

# Check if config.dev is embedded
i, o, e = c.exec_command('grep -oba "config.dev" /root/SOC/ly_analyser_src/agent/config/cached_config.o 2>/dev/null', timeout=30)
print('Binary search:', o.read().decode()[:300])

c.close()