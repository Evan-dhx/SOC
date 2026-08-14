import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== 1. Check server-side config.pb.h for psk ===')
i, o, e = c.exec_command("grep -l 'psk' /root/SOC/ly_analyser_src/common/config.pb.h 2>/dev/null; echo 'rc='$?", timeout=10)
print(o.read().decode().strip())

print('=== 2. Check ly_server config.pb.h for psk ===')
i, o, e = c.exec_command("grep -l 'psk' /root/SOC/ly_server_src/common/config.pb.h 2>/dev/null; echo 'rc='$?", timeout=10)
print(o.read().decode().strip())

print('=== 3. Check server protoc version ===')
i, o, e = c.exec_command("protoc --version 2>&1; which protoc 2>/dev/null", timeout=10)
print(o.read().decode().strip())

print('=== 4. Check if ly_server libcommon.so has psk symbols ===')
i, o, e = c.exec_command("strings /root/SOC/ly_server_src/common/libcommon.so | grep -c 'psk'; echo '---'; strings /root/SOC/ly_analyser_src/common/libcommon.so | grep -c 'psk'", timeout=10)
print(o.read().decode().strip())

print('=== 5. Check config.pb.h timestamps ===')
i, o, e = c.exec_command("ls -la /root/SOC/ly_analyser_src/common/config.pb.h /root/SOC/ly_analyser_src/common/config.pb.cc /root/SOC/ly_analyser_src/common/config.proto 2>/dev/null", timeout=10)
print(o.read().decode().strip())

print('=== 6. Check ly_server config.pb.h timestamps ===')
i, o, e = c.exec_command("ls -la /root/SOC/ly_server_src/common/config.pb.h /root/SOC/ly_server_src/common/config.pb.cc /root/SOC/ly_server_src/common/config.proto 2>/dev/null", timeout=10)
print(o.read().decode().strip())

c.close()