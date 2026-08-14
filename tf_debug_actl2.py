import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check the actl's CachedConfig behavior
# Verify config.pb.h has psk
i, o, e = c.exec_command('grep "psk" /root/SOC/ly_analyser_src/common/config.pb.h | head -3', timeout=30)
print('pb.h psk:', o.read().decode()[:200])

# Check the actual error from latest actl run
i, o, e = c.exec_command('tail -3 /var/log/httpd/ly_error_log 2>/dev/null', timeout=30)
print('Apache error:', o.read().decode()[:500])

# Verify config.dev is there
i, o, e = c.exec_command('head -5 /Agent/data/config.dev; echo ...; grep psk /Agent/data/config.dev', timeout=30)
print('config.dev psk:', o.read().decode()[:300])

c.close()