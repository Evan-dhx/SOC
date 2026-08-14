import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check which source tree has the updated pb files
i, o, e = c.exec_command('ls -la /root/SOC/ly_server_src/common/config.pb.h /root/SOC/ly_server_src/common/config.pb.cc 2>/dev/null', timeout=30)
print('Server pb:', o.read().decode()[:300])

# Rebuild libcommon.so
i, o, e = c.exec_command('cd /root/SOC/ly_server_src/common && make 2>&1 | tail -10', timeout=120)
print('libcommon build:', o.read().decode()[:500])

# Now rebuild actl and config_updater (they'll link against new libcommon.so)
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f actl.o config_updater.o && make actl config_updater 2>&1 | tail -5', timeout=120)
print('Handlers build:', o.read().decode()[:500])

# Redeploy
i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/ && cp /root/SOC/ly_analyser_src/agent/handlers/config_updater /Agent/cmd/', timeout=30)

# Test config_updater
i, o, e = c.exec_command('printf "dev { id: 1 psk: \"test123\" }" > /tmp/pt_psk.txt && curl -s -w "\nHTTP:%{http_code}\n" -X POST -d @/tmp/pt_psk.txt http://127.0.0.1:10081/config_updater 2>&1 | head -3', timeout=30)
print('PSK test:', o.read().decode()[:200])

c.close()