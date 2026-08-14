import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== 1. Check /lib64 symlinks ===')
i, o, e = c.exec_command("ls -la /lib64/libcommon.so /usr/lib64/libcommon.so 2>/dev/null; echo '---'; ls -la /lib64 2>/dev/null | head -5; echo '---'; readlink -f /lib64 2>/dev/null", timeout=10)
print(o.read().decode().strip())

print()
print('=== 2. Check if actl has setuid or capabilities ===')
i, o, e = c.exec_command("ls -la /Agent/cmd/actl; echo '---'; getcap /Agent/cmd/actl 2>/dev/null; echo '---'; file /Agent/cmd/actl | grep -i 'setuid\|setgid'", timeout=10)
print(o.read().decode().strip())

print()
print('=== 3. Check Apache CGI environment (LD_LIBRARY_PATH) ===')
i, o, e = c.exec_command("cat /etc/httpd/conf.d/ly_server.conf 2>/dev/null | head -40", timeout=10)
print(o.read().decode().strip()[:2000])

print()
print('=== 4. Check RPATH/RUNPATH in actl binary ===')
i, o, e = c.exec_command("readelf -d /Agent/cmd/actl 2>/dev/null | grep -i 'rpath\|runpath'; echo '---'; chrpath -l /Agent/cmd/actl 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== 5. Check /lib64/libcommon.so md5 and size ===')
i, o, e = c.exec_command("md5sum /lib64/libcommon.so; ls -la /lib64/libcommon.so; md5sum /usr/lib64/libcommon.so; ls -la /usr/lib64/libcommon.so", timeout=10)
print(o.read().decode().strip())

c.close()