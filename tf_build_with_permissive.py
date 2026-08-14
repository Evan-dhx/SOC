import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Build with -fpermissive flag to work around GCC 11 + protobuf 3.21 incompatibility
print('=== Build libcommon.so with -fpermissive ===')
i, o, e = c.exec_command(
    "cd /root/SOC/ly_analyser_src/common && "
    "make CXXFLAGS='-Wall -g -fPIC -std=c++1y -O2 -fpermissive' -j4 2>&1 | tail -15",
    timeout=180)
result = o.read().decode().strip()
print(result[:3000])

print()
print('=== Check if libcommon.so was created ===')
i, o, e = c.exec_command("ls -la /root/SOC/ly_analyser_src/common/libcommon.so 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:200])

# If build succeeded, deploy
if 'libcommon.so' in result or 'error' not in result.lower():
    print()
    print('=== Deploy libcommon.so to all paths ===')
    i, o, e = c.exec_command("cp /root/SOC/ly_analyser_src/common/libcommon.so /usr/lib64/libcommon.so && "
        "cp /root/SOC/ly_analyser_src/common/libcommon.so /home/Agent/lib/libcommon.so && "
        "cp /root/SOC/ly_analyser_src/common/libcommon.so /home/Server/lib/libcommon.so && "
        "echo DEPLOYED && "
        "md5sum /usr/lib64/libcommon.so /home/Agent/lib/libcommon.so /home/Server/lib/libcommon.so", timeout=10)
    print(o.read().decode().strip())

print()
print('=== Restart Apache ===')
i, o, e = c.exec_command("systemctl restart httpd 2>&1; sleep 2; echo RESTARTED", timeout=30)
print(o.read().decode().strip())

c.close()