import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Copy pb files from ly_server_src (they still have them)
i, o, e = c.exec_command('cp /root/SOC/ly_server_src/common/config.pb.h /root/SOC/ly_analyser_src/common/ && cp /root/SOC/ly_server_src/common/config.pb.cc /root/SOC/ly_analyser_src/common/ && ls -la /root/SOC/ly_analyser_src/common/config.pb.*', timeout=30)
print('Copied pb files:', o.read().decode()[:300])

# Fix local_disk_config.cpp - remove log_warning
i, o, e = c.exec_command('sed -i "s/log_warning.*//" /root/SOC/ly_analyser_src/agent/config/local_disk_config.cpp', timeout=30)

# Rebuild config.a
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/config && rm -f *.o config.a && make 2>&1 | tail -3', timeout=120)
print('config.a:', o.read().decode()[:300])

# Rebuild actl
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f actl.o actl && make actl 2>&1 | tail -5', timeout=120)
print('actl:', o.read().decode()[:300])

# Deploy
i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/ && ./Server/bin/config_pusher 2>&1 | grep -c "restart"', timeout=120)
r = o.read().decode()[:100]
print('Push restart count:', r)

c.close()