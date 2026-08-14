import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check the actual file on the server
i, o, e = c.exec_command('cat /root/SOC/ly_analyser_src/agent/config/cached_config.cpp', timeout=30)
print('File on server:', o.read().decode()[:1000])

c.close()