import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix: set setuid bit on actl
print('=== Set setuid on actl ===')
i, o, e = c.exec_command("chown root:root /Agent/cmd/actl; chmod u+s /Agent/cmd/actl; ls -la /Agent/cmd/actl", timeout=10)
print(o.read().decode().strip())

# Restart Apache
print()
print('=== Restart Apache ===')
i, o, e = c.exec_command("systemctl restart httpd 2>&1; sleep 2; echo RESTARTED", timeout=30)
print(o.read().decode().strip())

time.sleep(2)

# Test RESTART via curl
print()
print('=== Test RESTART via curl ===')
i, o, e = c.exec_command(
    "printf 'node: NODE_PROBE\nsrv: SRV_ALL\nop: RESTART\nid: \"1\"\n' > /tmp/ctl_test2.txt && "
    "curl -s -X POST -d @/tmp/ctl_test2.txt http://127.0.0.1:10081/actl 2>&1 | head -5",
    timeout=30)
print(o.read().decode().strip()[:500])

# Wait for restart to complete
time.sleep(8)

# Verify
print()
print('=== tsensor processes ===')
i, o, e = c.exec_command("ps aux | grep tsensor | grep -v grep", timeout=10)
print(o.read().decode().strip()[:400])

print()
print('=== tsensor.conf ===')
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf", timeout=10)
print(o.read().decode().strip()[:400])

print()
print('=== Check for kill errors ===')
i, o, e = c.exec_command("tail -5 /var/log/httpd/ly_error_log 2>/dev/null | grep -i 'kill\\|operation\\|permit'", timeout=10)
out = o.read().decode().strip()
if out:
    print('KILL ERRORS:', out[:500])
else:
    print('No kill errors!')

print()
print('=== Apache error log (last 3 lines) ===')
i, o, e = c.exec_command("tail -3 /var/log/httpd/ly_error_log 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:500])

c.close()