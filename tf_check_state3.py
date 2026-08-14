import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== 1. Latest 30 lines of error log (after last restart) ===')
i, o, e = c.exec_command("tail -30 /var/log/httpd/ly_error_log 2>/dev/null; echo '---'; tail -30 /var/log/httpd/error_log 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:2000])

print()
print('=== 2. config.dev content ===')
i, o, e = c.exec_command("cat /Agent/data/config.dev 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:1000])

print()
print('=== 3. How is config_pusher triggered? ===')
i, o, e = c.exec_command("crontab -l 2>/dev/null; echo '---'; ls -la /etc/cron.d/*cfg* /etc/cron.d/*push* 2>/dev/null; echo '---'; ls -la /Server/bin/ 2>/dev/null | head -20", timeout=10)
print(o.read().decode().strip()[:1000])

print()
print('=== 4. What triggers config push after Web UI save? ===')
i, o, e = c.exec_command("grep -r 'config_pusher' /Server/ 2>/dev/null | head -10", timeout=10)
print(o.read().decode().strip()[:1000])

print()
print('=== 5. Check ldd for actl libcommon ===')
i, o, e = c.exec_command("ldd /Agent/cmd/actl 2>/dev/null | grep -i common", timeout=10)
print(o.read().decode().strip())

print()
print('=== 6. Force config_pusher run and check result ===')
i, o, e = c.exec_command("/Server/bin/config_pusher 2>&1 | head -20", timeout=120)
print(o.read().decode().strip()[:2000])

time.sleep(3)
print()
print('=== 7. tsensor.conf after push ===')
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== 8. tsensor processes ===')
i, o, e = c.exec_command("ps aux | grep -E 'tsensor|probe' | grep -v grep", timeout=10)
print(o.read().decode().strip()[:500])

print()
print('=== 9. config file interface field ===')
i, o, e = c.exec_command("grep -E 'interface|psk' /Agent/data/config 2>/dev/null", timeout=10)
print(o.read().decode().strip())

print()
print('=== 10. Check if config_pusher CtlReq actually sent ===')
i, o, e = c.exec_command("tail -50 /var/log/httpd/ly_error_log 2>/dev/null | grep -i 'actl\|restart\|probe'", timeout=10)
print(o.read().decode().strip()[:2000])

c.close()