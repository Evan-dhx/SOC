import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check if the pb files are from the RIGHT version
i, o, e = c.exec_command('grep -n "field.*psk\|17.*psk\|Device.*psk" /root/SOC/ly_analyser_src/common/config.pb.cc | head -10', timeout=30)
print('pb.cc psk fields:', o.read().decode()[:500])

# Check if the shared library has the psk descriptor
i, o, e = c.exec_command('strings /lib64/libcommon.so | grep -i "config.Device.psk\|psk.field\|field.psk" | head -5', timeout=30)
print('SO psk desc:', o.read().decode()[:300])

# Check the ldconfig cache
i, o, e = c.exec_command('ldconfig -p | grep libcommon', timeout=30)
print('ldconfig:', o.read().decode()[:200])

c.close()