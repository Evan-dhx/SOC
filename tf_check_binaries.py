import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check binary timestamps and sizes
i, o, e = c.exec_command('ls -la /Agent/cmd/actl /root/SOC/ly_analyser_src/agent/handlers/actl 2>/dev/null; echo ---; strings /Agent/cmd/actl | grep "config.dev" | head -3', timeout=30)
print('Binary info:', o.read().decode()[:500])

# If config.dev not found in binary, the new CachedConfig code isn't deployed
i, o, e = c.exec_command('ls -la /root/SOC/ly_analyser_src/agent/config/config.a 2>/dev/null; ls -la /root/SOC/ly_analyser_src/agent/handlers/actl.o 2>/dev/null', timeout=30)
print('Lib info:', o.read().decode()[:500])

c.close()