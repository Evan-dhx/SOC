import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Try building with ly_analyser common (protoc might have different config)
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/common && which protoc && protoc --version 2>&1', timeout=30)
print('Protoc:', o.read().decode()[:200])

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/common && rm -f config.pb.cc config.pb.h && make config.pb.h 2>&1 | tail -5', timeout=120)
print('Proto gen:', o.read().decode()[:500])

c.close()