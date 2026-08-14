import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

i, o, e = c.exec_command('mysql -uroot -ppassword123 -e "SHOW DATABASES" 2>&1', timeout=30)
print('Databases:', o.read().decode()[:500])
print('STDERR:', e.read().decode()[:300])

i, o, e = c.exec_command('mysql -uroot -ppassword123 ly_server -e "SELECT count(1) as cnt FROM t_feature" 2>&1', timeout=30)
print('t_feature:', o.read().decode()[:300])
print('ERR:', e.read().decode()[:300])

i, o, e = c.exec_command('mysql -uroot -ppassword123 ly_server -e "SELECT count(1) as cnt FROM t_ti" 2>&1', timeout=30)
print('t_ti:', o.read().decode()[:300])
print('ERR:', e.read().decode()[:300])

i, o, e = c.exec_command('ls -la /Agent/flow/1/nfcapd.current 2>/dev/null', timeout=30)
print('current:', o.read().decode()[:200])

i, o, e = c.exec_command('ps -e | grep indexer', timeout=30)
print('indexer proc:', o.read().decode()[:200])

c.close()