import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Find ALL config.pb.h files
i, o, e = c.exec_command('find /root/SOC /usr/local/include -name "config.pb.h" 2>/dev/null', timeout=30)
print('All pb.h files:', o.read().decode()[:500])

# Check which one actl links against
i, o, e = c.exec_command('ldd /Agent/cmd/actl | grep common; echo ---; ldd /Agent/cmd/config_updater | grep common', timeout=30)
print('Library links:', o.read().decode()[:300])

# Check which .a files are linked
i, o, e = c.exec_command('grep -n "config.a\|config.pb\|common" /root/SOC/ly_analyser_src/agent/handlers/Makefile | head -10', timeout=30)
print('Makefile links:', o.read().decode()[:500])

c.close()