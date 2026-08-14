import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check config.proto for psk field
i, o, e = c.exec_command('grep psk /root/SOC/ly_analyser_src/common/config.proto', timeout=30)
print('config.proto psk:', o.read().decode()[:300])

# Check pb.h for psk
i, o, e = c.exec_command('grep psk /root/SOC/ly_analyser_src/common/config.pb.h 2>/dev/null | head -5', timeout=30)
print('config.pb.h psk:', o.read().decode()[:300])

# Also check on ly_server side
i, o, e = c.exec_command('grep psk /root/SOC/ly_server_src/common/config.proto 2>/dev/null | head -3', timeout=30)
print('Server config.proto:', o.read().decode()[:300])

i, o, e = c.exec_command('grep psk /root/SOC/ly_server_src/common/config.pb.h 2>/dev/null | head -3', timeout=30)
print('Server config.pb.h:', o.read().decode()[:300])

c.close()