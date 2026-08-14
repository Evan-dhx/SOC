import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\config_updater.cpp', '/root/SOC/ly_analyser_src/agent/handlers/config_updater.cpp')
sftp.close()

i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f config_updater.o && make config_updater 2>&1 | tail -5', timeout=120)
print('Build:', o.read().decode()[:500])

i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/ 2>/dev/null; cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /home/Agent/cmd/ 2>/dev/null; echo done', timeout=30)
print('Deploy done')

# Clean stale config.tmp
i, o, e = c.exec_command('rm -f /Agent/data/config.tmp', timeout=30)

# Restore config and test
i, o, e = c.exec_command("echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; chmod 644 /Agent/data/config; wc -c /Agent/data/config", timeout=30)
print('Restored:', o.read().decode()[:100])

# Clear syslog for clean test
import time
time.sleep(2)

i, o, e = c.exec_command("curl -s -X POST -H 'Content-Type: text/plain' -d 'dev { id: 1 name: \"test\" psk: \"abc123\" }' http://127.0.0.1:10081/config_updater 2>&1; echo; echo CURL_EXIT=$?", timeout=30)
print('Curl:', o.read().decode()[:200])

time.sleep(2)

# Check ALL related files
i, o, e = c.exec_command('echo === config ===; ls -la /Agent/data/config; wc -c /Agent/data/config; echo === config.tmp ===; ls -la /Agent/data/config.tmp 2>/dev/null || echo "not found"; echo === syslog ===; tail -6 /var/log/messages 2>/dev/null | grep config_updater', timeout=30)
print(o.read().decode()[:1000])

c.close()