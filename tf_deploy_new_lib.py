import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check libcommon.so
print('=== Check new libcommon.so ===')
i, o, e = c.exec_command("ls -la /root/SOC/ly_analyser_src/common/libcommon.so", timeout=10)
print(o.read().decode().strip())
i, o, e = c.exec_command("strings /root/SOC/ly_analyser_src/common/libcommon.so | grep -c psk", timeout=10)
print('psk count:', o.read().decode().strip())
i, o, e = c.exec_command("md5sum /root/SOC/ly_analyser_src/common/libcommon.so", timeout=10)
print('md5:', o.read().decode().strip())

# Deploy to all 3 paths
print()
print('=== Deploy to /usr/lib64 /home/Agent/lib /home/Server/lib ===')
cmds = "cp /root/SOC/ly_analyser_src/common/libcommon.so /usr/lib64/libcommon.so; cp /root/SOC/ly_analyser_src/common/libcommon.so /home/Agent/lib/libcommon.so; cp /root/SOC/ly_analyser_src/common/libcommon.so /home/Server/lib/libcommon.so; echo DONE; md5sum /usr/lib64/libcommon.so /home/Agent/lib/libcommon.so /home/Server/lib/libcommon.so"
i, o, e = c.exec_command(cmds, timeout=10)
print(o.read().decode().strip())

# Restart Apache
print()
print('=== Restart Apache ===')
i, o, e = c.exec_command("systemctl restart httpd 2>&1; sleep 2; systemctl status httpd 2>&1 | head -3", timeout=30)
print(o.read().decode().strip())

c.close()