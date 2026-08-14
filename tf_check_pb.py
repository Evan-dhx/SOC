import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

i, o, e = c.exec_command('grep -c "psk" /root/SOC/ly_analyser_src/common/config.pb.cc', timeout=30)
print('pb.cc psk count:', o.read().decode()[:100])
i, o, e = c.exec_command('ls -la /root/SOC/ly_analyser_src/common/config.pb.cc /root/SOC/ly_analyser_src/common/config.pb.h 2>/dev/null', timeout=30)
print('pb files:', o.read().decode()[:300])
c.close()