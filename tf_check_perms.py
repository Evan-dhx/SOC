import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check directory permissions
i, o, e = c.exec_command('ls -la /Agent/; ls -la /Agent/data/ | head -5', timeout=30)
print('Perms:', o.read().decode()[:300])

# Test apache user write access
i, o, e = c.exec_command('sudo -u apache bash -c "echo test > /Agent/data/test_write.txt; cat /Agent/data/test_write.txt; wc -c /Agent/data/test_write.txt; rm /Agent/data/test_write.txt" 2>&1', timeout=30)
print('Apache write:', o.read().decode()[:300])

# Test rename as apache
i, o, e = c.exec_command('sudo -u apache bash -c "echo hello > /tmp/test_rename_src.txt; mv /tmp/test_rename_src.txt /tmp/test_rename_dst.txt; cat /tmp/test_rename_dst.txt" 2>&1', timeout=30)
print('Apache rename:', o.read().decode()[:200])

# Check config.tmp
i, o, e = c.exec_command('ls -la /Agent/data/config.tmp 2>/dev/null; echo ex=$?', timeout=30)
print('Config.tmp:', o.read().decode()[:200])

c.close()