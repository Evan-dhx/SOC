import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Run pusher and check both logs
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1', timeout=120)
print('Push:', o.read().decode()[:1000])

time.sleep(5)
i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -4', timeout=30)
print('tsensor.conf:', o.read().decode()[:300])

i, o, e = c.exec_command('tail -3 /var/log/httpd/ly_error_log 2>/dev/null | grep -c "psk\|no field\|Error"', timeout=30)
print('PSK errors in log:', o.read().decode()[:100])

i, o, e = c.exec_command('ps -e | grep tsensor | wc -l; echo PID:; pidof tsensor', timeout=30)
print('tsensor:', o.read().decode()[:100])

c.close()