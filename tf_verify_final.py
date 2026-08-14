import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== 1. Check MySQL device config ===')
i, o, e = c.exec_command(
    "mysql -uroot -p123456 liuying -e \"SELECT id, name, interface, tls_psk, port, ip FROM t_device WHERE id=1\" 2>&1",
    timeout=10)
print(o.read().decode().strip())

print()
print('=== 2. Check config.dev current interface ===')
i, o, e = c.exec_command("grep interface /Agent/data/config.dev 2>/dev/null", timeout=10)
print(o.read().decode().strip())

print()
print('=== 3. Check tsensor.conf ===')
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== 4. Check tsensor cmdline ===')
i, o, e = c.exec_command("ps aux | grep tsensor | grep -v grep", timeout=10)
print(o.read().decode().strip()[:300])

print()
print('=== 5. Check latest error log for psk/config errors ===')
i, o, e = c.exec_command("tail -30 /var/log/httpd/ly_error_log 2>/dev/null | grep -v 'sshd\|AH01232\|AH02282\|AH00489\|AH00094\|AH00492\|suexec\|mpm_event\|lbmethod\|core:notice'", timeout=10)
print(o.read().decode().strip()[:500] or '(no relevant errors - clean!)')

print()
print('=== 6. Direct actl STATUS test ===')
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
i, o, e = c.exec_command("cat > /tmp/actl_test2.py << 'EOF'\n" + python_test + "\nEOF", timeout=10)
import time; time.sleep(1)
i, o, e = c.exec_command("python3 /tmp/actl_test2.py 2>&1", timeout=30)
print(o.read().decode().strip())

c.close()