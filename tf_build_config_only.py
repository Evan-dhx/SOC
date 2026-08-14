import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\config\cached_config.cpp',
         '/root/SOC/ly_analyser_src/agent/config/cached_config.cpp')
sftp.close()

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/config && make cached_config.o 2>&1', timeout=120)
print('Build output:', o.read().decode()[:1000])
c.close()