import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Upload actl.cpp
print('=== Upload actl.cpp ===')
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\actl.cpp', '/root/SOC/ly_analyser_src/agent/handlers/actl.cpp')
sftp.close()
print('Uploaded')

# Build
print()
print('=== Build actl ===')
i, o, e = c.exec_command("cd /root/SOC/ly_analyser_src/agent/handlers && make clean && make actl 2>&1 | tail -10", timeout=120)
print(o.read().decode().strip()[:1000])

# Deploy
print()
print('=== Deploy actl with setuid ===')
i, o, e = c.exec_command("cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/actl && chown root:root /Agent/cmd/actl && chmod u+s /Agent/cmd/actl && ls -la /Agent/cmd/actl", timeout=10)
print(o.read().decode().strip())

# Restart Apache
print()
print('=== Restart Apache ===')
i, o, e = c.exec_command("systemctl restart httpd 2>&1; sleep 2; echo RESTARTED", timeout=30)
print(o.read().decode().strip())

# Write and run comprehensive final test
print()
print('=== Final comprehensive test ===')
test_script = """#!/usr/bin/env python3
import urllib.request, time

# 1. Test STATUS
data = b"node: NODE_PROBE\\nsrv: SRV_ALL\\nop: STATUS\\nid: \\"1\\"\\n"
req = urllib.request.Request("http://127.0.0.1:10081/actl", data=data, method="POST")
resp = urllib.request.urlopen(req, timeout=15)
print("1. STATUS HTTP:", resp.status)

# 2. Test RESTART
data = b"node: NODE_PROBE\\nsrv: SRV_ALL\\nop: RESTART\\nid: \\"1\\"\\n"
req = urllib.request.Request("http://127.0.0.1:10081/actl", data=data, method="POST")
resp = urllib.request.urlopen(req, timeout=30)
print("2. RESTART HTTP:", resp.status)
body = resp.read()
# Check if probe restart was success
if b"probe" in body and b"succeed" in body and b"active" in body:
    print("   RESULT: PROBE RESTART SUCCESS")
else:
    print("   RESULT:", body[:100].hex())

time.sleep(5)
"""
i, o, e = c.exec_command("cat > /tmp/final_test.py << 'SCRIPT'\n" + test_script + "\nSCRIPT", timeout=10)
time.sleep(1)
i, o, e = c.exec_command("python3 /tmp/final_test.py 2>&1", timeout=60)
print(o.read().decode().strip()[:1000])

time.sleep(5)
print()
print('=== Final state ===')
i, o, e = c.exec_command("ps aux | grep tsensor | grep -v grep", timeout=10)
out = o.read().decode().strip()
if out:
    print(out[:500])
    i2, o2, e2 = c.exec_command("ps aux | grep tsensor | grep -v grep | grep -oP '(?<=-i )\\S+'", timeout=10)
    print('Interface:', o2.read().decode().strip())
else:
    print('No tsensor')

print()
print('=== tsensor.conf ===')
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== config.dev interface ===')
i, o, e = c.exec_command("grep interface /Agent/data/config.dev 2>/dev/null", timeout=10)
print(o.read().decode().strip())

c.close()