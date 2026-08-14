import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Find ALL copies of libcommon that actl/config_updater might load
i, o, e = c.exec_command('find / -name "libcommon*" -type f 2>/dev/null', timeout=30)
print('All libcommon:', o.read().decode()[:500])

# Check what the running actl/config_updater loads
i, o, e = c.exec_command('ldd /Agent/cmd/actl | grep common; echo ---; ldd /Agent/cmd/config_updater | grep common', timeout=30)
print('Runtime links:', o.read().decode()[:200])

# Check LD_LIBRARY_PATH
i, o, e = c.exec_command('echo $LD_LIBRARY_PATH', timeout=30)
print('LD_LIBRARY_PATH:', o.read().decode()[:200])

c.close()