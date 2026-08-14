import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Step 1: Kill all tsensor processes
print('=== Kill all tsensor ===')
i, o, e = c.exec_command("pkill -9 tsensor 2>/dev/null; sleep 1; ps aux | grep tsensor | grep -v grep || echo '(none)'", timeout=15)
print(o.read().decode().strip())

# Step 2: Write Python test script to remote
print()
print('=== Write test script to server ===')
script = """#!/usr/bin/env python3
import urllib.request
data = b"node: NODE_PROBE\\nsrv: SRV_ALL\\nop: RESTART\\nid: \\"1\\"\\n"
req = urllib.request.Request("http://127.0.0.1:10081/actl", data=data, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=15)
    print("HTTP:", resp.status)
    body = resp.read()
    print("Body hex:", body.hex()[:200])
except Exception as e:
    print("ERROR:", str(e)[:300])
"""
i, o, e = c.exec_command("cat > /tmp/test_restart.py << 'SCRIPT'\n" + script + "\nSCRIPT", timeout=10)
time.sleep(1)
print('Written OK')

# Step 3: Run the test
print()
print('=== Run RESTART test ===')
i, o, e = c.exec_command("python3 /tmp/test_restart.py 2>&1", timeout=30)
print(o.read().decode().strip()[:500])

# Step 4: Wait and check
time.sleep(8)
print()
print('=== tsensor processes ===')
i, o, e = c.exec_command("ps aux | grep tsensor | grep -v grep", timeout=10)
out = o.read().decode().strip()
if out:
    print(out[:500])
    i2, o2, e2 = c.exec_command("ps aux | grep tsensor | grep -v grep | grep -oP '(?<=-i )\\S+'", timeout=10)
    print('Interface:', o2.read().decode().strip())
else:
    print('(no tsensor)')

print()
print('=== tsensor.conf ===')
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf", timeout=10)
print(o.read().decode().strip()[:400])

print()
print('=== Apache errors (recent, no sshd) ===')
i, o, e = c.exec_command("tail -10 /var/log/httpd/ly_error_log 2>/dev/null | grep -v sshd", timeout=10)
print(o.read().decode().strip()[:1000])

c.close()