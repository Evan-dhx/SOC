import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== 1. tsensor processes NOW ===')
i, o, e = c.exec_command("ps aux | grep tsensor | grep -v grep", timeout=10)
print(o.read().decode().strip())

print()
print('=== 2. config.dev interface ===')
i, o, e = c.exec_command("grep interface /Agent/data/config.dev 2>/dev/null", timeout=10)
print(o.read().decode().strip())

print()
print('=== 3. config (full) interface ===')
i, o, e = c.exec_command("grep interface /Agent/data/config 2>/dev/null | head -3", timeout=10)
print(o.read().decode().strip())

print()
print('=== 4. tsensor.conf ===')
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== 5. Force run config_pusher and check after ===')
i, o, e = c.exec_command("/Server/bin/config_pusher 2>&1 | head -5", timeout=120)
print(o.read().decode().strip()[:500])

time.sleep(8)

print()
print('=== 6. tsensor processes AFTER push ===')
i, o, e = c.exec_command("ps aux | grep tsensor | grep -v grep", timeout=10)
print(o.read().decode().strip())

print()
print('=== 7. tsensor.conf AFTER push ===')
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== 8. config_pusher log ===')
i, o, e = c.exec_command("tail -10 /data/log/config_pusher.log 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:500])

c.close()