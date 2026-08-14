import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Deploy actl
print('=== Deploy actl ===')
i, o, e = c.exec_command("cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/actl && chmod +x /Agent/cmd/actl && ls -la /Agent/cmd/actl", timeout=10)
print(o.read().decode().strip())

# Restart Apache
print()
print('=== Restart Apache ===')
i, o, e = c.exec_command("systemctl restart httpd 2>&1; sleep 2; echo OK", timeout=30)
print(o.read().decode().strip())

# Run config_pusher and wait
print()
print('=== Run config_pusher ===')
i, o, e = c.exec_command("/Server/bin/config_pusher 2>&1 | head -30", timeout=120)
print(o.read().decode().strip()[:2000])

time.sleep(5)

# Check tsensor.conf
print()
print('=== tsensor.conf ===')
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:500])

# Check tsensor processes
print()
print('=== tsensor processes ===')
i, o, e = c.exec_command("ps aux | grep tsensor | grep -v grep", timeout=10)
print(o.read().decode().strip()[:500])

# Latest error log
print()
print('=== Latest Apache errors ===')
i, o, e = c.exec_command("tail -15 /var/log/httpd/ly_error_log 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:1500])

c.close()