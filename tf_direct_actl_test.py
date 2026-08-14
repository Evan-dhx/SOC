import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== Direct actl RESTART test ===')
# Create a proper CtlReq text file and send via curl, capturing full response
i, o, e = c.exec_command(
    "printf 'node: NODE_PROBE\\nsrv: SRV_ALL\\nop: RESTART\\nid: \"1\"\\n' > /tmp/ctl_test.txt && "
    "curl -s -v -X POST -d @/tmp/ctl_test.txt http://127.0.0.1:10081/actl 2>&1 | head -20",
    timeout=30)
print(o.read().decode().strip()[:2000])

time.sleep(5)

print()
print('=== tsensor processes after direct RESTART ===')
i, o, e = c.exec_command("ps aux | grep tsensor | grep -v grep", timeout=10)
print(o.read().decode().strip()[:300])

print()
print('=== tsensor.conf ===')
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== Apache error log ===')
i, o, e = c.exec_command("tail -10 /var/log/httpd/ly_error_log 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:1000])

c.close()