import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Rebuild libcommon.so from ly_analyser_src
print('=== Step 1: Cleaning old build ===')
i, o, e = c.exec_command("cd /root/SOC/ly_analyser_src/common && make clean 2>&1 | tail -5", timeout=30)
print(o.read().decode().strip()[:500])

print()
print('=== Step 2: Check if protoc works at all ===')
i, o, e = c.exec_command("cd /root/SOC/ly_analyser_src/common && protoc config.proto --cpp_out=. 2>&1; echo 'exit:'$?", timeout=30)
out = o.read().decode().strip()
print(out[:500])

print()
print('=== Step 3: Check if config.pb.cc/h exist and have psk ===')
i, o, e = c.exec_command("grep -c 'psk' /root/SOC/ly_analyser_src/common/config.pb.h /root/SOC/ly_analyser_src/common/config.pb.cc 2>/dev/null", timeout=10)
print(o.read().decode().strip())

print()
print('=== Step 4: Build libcommon.so ===')
i, o, e = c.exec_command("cd /root/SOC/ly_analyser_src/common && make -j4 2>&1 | tail -20", timeout=120)
print(o.read().decode().strip()[:2000])

print()
print('=== Step 5: Verify new libcommon.so has psk descriptor ===')
i, o, e = c.exec_command("ls -la /root/SOC/ly_analyser_src/common/libcommon.so && strings /root/SOC/ly_analyser_src/common/libcommon.so | grep -c 'psk'", timeout=10)
print(o.read().decode().strip())

print()
print('=== Step 6: Check config.pb.h for psk field name ===')
i, o, e = c.exec_command("grep 'psk' /root/SOC/ly_analyser_src/common/config.pb.h | head -5", timeout=10)
print(o.read().decode().strip()[:500])

c.close()