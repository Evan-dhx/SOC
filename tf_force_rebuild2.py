import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Force rebuild config lib by removing .o files
i, o, e = c.exec_command('rm -f /root/SOC/ly_analyser_src/agent/config/*.o /root/SOC/ly_analyser_src/agent/config/config.a', timeout=30)
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/config && make 2>&1 | tail -5', timeout=120)
print('Config lib:', o.read().decode()[:500])

# Then force rebuild actl
i, o, e = c.exec_command('rm -f /root/SOC/ly_analyser_src/agent/handlers/actl /root/SOC/ly_analyser_src/agent/handlers/actl.o', timeout=30)
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && make actl 2>&1 | tail -5', timeout=120)
print('Actl:', o.read().decode()[:300])

# Verify
i, o, e = c.exec_command('strings /root/SOC/ly_analyser_src/agent/handlers/actl | grep "config.dev" | head -3', timeout=30)
r = o.read().decode()
print('config.dev in binary:', r.strip() if r.strip() else 'STILL NOT FOUND')

c.close()