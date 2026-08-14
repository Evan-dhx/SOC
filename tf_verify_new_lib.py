import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== 1. Test actl HTTP directly ===')
# Write test request to temp file on server
python_test = """
import urllib.request
req = urllib.request.Request("http://127.0.0.1:10081/actl",
    data=b"node: NODE_PROBE\\nsrv: SRV_ALL\\nop: STATUS\\nid: \\"1\\"\\n",
    method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=10)
    print("HTTP:", resp.status)
except Exception as ex:
    print("ERROR:", str(ex)[:300])
"""
i, o, e = c.exec_command("cat > /tmp/actl_test.py << 'EOF'\n" + python_test + "\nEOF", timeout=10)
time.sleep(1)
i, o, e = c.exec_command("python3 /tmp/actl_test.py 2>&1", timeout=30)
print(o.read().decode().strip())

print()
print('=== 2. Check Apache error log for psk errors (last 20 lines) ===')
i, o, e = c.exec_command("tail -30 /var/log/httpd/ly_error_log 2>/dev/null | grep -i 'psk'", timeout=10)
out = o.read().decode().strip()
if out:
    print('STILL HAS PSK ERRORS:', out[:1000])
else:
    print('NO PSK ERRORS - GOOD!')

print()
print('=== 3. Run config_pusher ===')
i, o, e = c.exec_command("/Server/bin/config_pusher 2>&1 | head -20", timeout=120)
print(o.read().decode().strip()[:2000])

print()
print('=== 4. Check tsensor.conf ===')
time.sleep(3)
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== 5. Check tsensor processes ===')
i, o, e = c.exec_command("ps aux | grep tsensor | grep -v grep", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== 6. Check config file interface ===')
i, o, e = c.exec_command("grep interface /Agent/data/config /Agent/data/config.dev 2>/dev/null", timeout=10)
print(o.read().decode().strip())

print()
print('=== 7. Latest error log (no filter) ===')
i, o, e = c.exec_command("tail -10 /var/log/httpd/ly_error_log 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:1000])

c.close()