import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check tables in server db
i, o, e = c.exec_command("mysql -uroot -ppassword123 server -e 'SHOW TABLES LIKE \"%feature%\"; SHOW TABLES LIKE \"%ti%\"; SHOW TABLES LIKE \"%event%\"' 2>&1", timeout=30)
print('[ server DB tables with feature/ti/event ]')
print(o.read().decode()[:800])

# Check counts
i, o, e = c.exec_command("mysql -uroot -ppassword123 server -e 'SELECT count(1) as cnt FROM t_feature' 2>&1", timeout=30)
print('[ t_feature count ]')
print(o.read().decode()[:300])

i, o, e = c.exec_command("mysql -uroot -ppassword123 server -e 'SELECT count(1) as cnt FROM t_ti' 2>&1", timeout=30)
print('[ t_ti count ]')
print(o.read().decode()[:300])

i, o, e = c.exec_command("mysql -uroot -ppassword123 server -e 'SELECT count(1) as cnt FROM t_event' 2>&1", timeout=30)
print('[ t_event count ]')
print(o.read().decode()[:300])

# Check indexer log
i, o, e = c.exec_command('tail -5 /tmp/idx.log 2>/dev/null', timeout=30)
print('[ indexer log ]')
print(o.read().decode()[:500])

# Check processes
i, o, e = c.exec_command('ps -e | grep -E "indexer|extract" | head -3', timeout=30)
print('[ processes ]')
print(o.read().decode()[:200])

c.close()