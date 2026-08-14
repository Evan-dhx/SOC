import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ('indexer_process', 'cat /Agent/data/indexer_process 2>/dev/null | head -15'),
    ('indexer_feature', 'cat /Agent/data/indexer_feature 2>/dev/null | tail -10'),
    ('indexer_cache', 'cat /Agent/data/indexer_cache 2>/dev/null | tail -10'),
    ('t_feature count', "mysql -uroot -proot ly -e 'select count(*) from t_feature' 2>/dev/null"),
    ('t_event count', "mysql -uroot -proot ly -e 'select count(*) from t_event' 2>/dev/null"),
    ('t_ti count last 24h', "mysql -uroot -proot ly -e 'select count(*) from t_ti where timestamp > unix_timestamp(date_sub(now(), interval 1 day))' 2>/dev/null"),
    ('t_ti total count', "mysql -uroot -proot ly -e 'select count(*) from t_ti' 2>/dev/null"),
    ('nfdump sample', 'nfdump -M /data/flow/1 -R /data/flow/1/nfcapd.202608140900 -c 3 2>/dev/null | head -10'),
    ('agent data files', 'ls -la /Agent/data/ | grep -v total | tail -10'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:600])
    if err: print(f'ERR: {err[:200]}')
c.close()