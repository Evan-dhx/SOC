import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Kill old tsensor + nftls, restart fresh with systemctl
i, o, e = c.exec_command('pkill -9 tsensor 2>/dev/null; sleep 2; systemctl restart tsensor 2>&1; sleep 3; echo ===; ps -e | grep tsensor; echo ===; cat /proc/$(pidof tsensor)/cmdline 2>/dev/null | tr "\\0" " "', timeout=30)
print('Restart:', o.read().decode()[:500])

# Now run config_pusher - the new actl should find tsensor (now running with -n 127.0.0.1:9996)
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | head -10', timeout=120)
print('Push:', o.read().decode()[:800])

time.sleep(5)
i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -3', timeout=30)
print('tsensor.conf:', o.read().decode()[:200])
i, o, e = c.exec_command('cat /proc/$(pidof tsensor)/cmdline 2>/dev/null | tr "\\0" " "', timeout=30)
print('New cmd:', o.read().decode()[:300])

c.close()