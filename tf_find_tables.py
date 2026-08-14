import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for db in ['server', 'ly_agent', 'ly_server']:
    i, o, e = c.exec_command(f'mysql -uroot -ppassword123 {db} -e "SHOW TABLES" 2>&1', timeout=30)
    print(f'\n[ {db} tables ]')
    print(o.read().decode()[:800])

# Also check previous indexer data files
i, o, e = c.exec_command('ls -la /Agent/data/indexer_* 2>/dev/null', timeout=30)
print('\n[ indexer data files ]')
print(o.read().decode()[:500])

# Restart indexer the simplest way
i, o, e = c.exec_command('cd /Agent/bin && setsid bash launch_indexer.sh > /tmp/idx.log 2>&1 &', timeout=30)
print('\n[ launch indexer ]')
time.sleep(8)
i, o, e = c.exec_command('ps -e | grep -E "indexer|extract" | head -3', timeout=30)
print(o.read().decode()[:200])
i, o, e = c.exec_command('tail -5 /tmp/idx.log 2>/dev/null', timeout=30)
print(o.read().decode()[:500])

c.close()