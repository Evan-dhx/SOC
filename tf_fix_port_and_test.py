import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Fix port in MySQL (should be 9995 for nfcapd)
i, o, e = c.exec_command("mysql -u root -e \"UPDATE server.t_device SET port=9995 WHERE id=1; SELECT id,name,port,interface FROM server.t_device WHERE id=1\" 2>&1", timeout=30)
print('Fix port:', o.read().decode()[:300])

# Run config_pusher
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1 | head -3', timeout=120)
print('Push:', o.read().decode()[:300])

# Wait for probe restart
time.sleep(5)

# Check tsensor processes
i, o, e = c.exec_command("ps -ef | grep -E 'sensor|probe' | grep -v grep; echo ---; cat /Agent/etc/tsensor.conf 2>/dev/null", timeout=30)
print('After fix:', o.read().decode()[:800])

# Check if old tsensor was killed and new one started
i, o, e = c.exec_command("ps -e | grep -o 'tsensor' | wc -l; echo PIDs:; pidof tsensor", timeout=30)
print('Count:', o.read().decode()[:100])

c.close()
print('\nDone')