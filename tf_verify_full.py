import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ('DB ly_server 表列表', 'mysql -uroot -ppassword123 ly_server -e "show tables" 2>/dev/null'),
    ('DB ly_agent 表列表', 'mysql -uroot -ppassword123 ly_agent -e "show tables" 2>/dev/null'),
    ('t_feature 记录数', 'mysql -uroot -ppassword123 ly_server -e "select count(1) as cnt from t_feature" 2>/dev/null'),
    ('最新 3 条 feature', 'mysql -uroot -ppassword123 ly_server -e "select id, timestamp, sip, dip, dport, bytes from t_feature order by id desc limit 3" 2>/dev/null'),
    ('t_ti 记录数', 'mysql -uroot -ppassword123 ly_server -e "select count(1) as cnt from t_ti" 2>/dev/null'),
    ('最新 3 条 TI', 'mysql -uroot -ppassword123 ly_server -e "select id, timestamp, threat_type, threat_detail from t_ti order by id desc limit 3" 2>/dev/null'),
    ('t_event 记录数', 'mysql -uroot -ppassword123 ly_server -e "select count(1) as cnt from t_event" 2>/dev/null'),
    ('indexer 处理进度', 'cat /Agent/data/indexer_process 2>/dev/null | grep -E "^#|enable" | head -20'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')

# Wait for indexer to process more data
print('\n等待 60 秒让 indexer 处理更多数据...')
time.sleep(60)

for label, cmd in [
    ('索引特征文件', 'cat /Agent/data/indexer_feature 2>/dev/null | tail -5'),
    ('t_feature 最新', 'mysql -uroot -ppassword123 ly_server -e "select count(1) as cnt, from_unixtime(min(timestamp)) as start, from_unixtime(max(timestamp)) as end from t_feature" 2>/dev/null'),
    ('t_ti 最新', 'mysql -uroot -ppassword123 ly_server -e "select count(1) as cnt, from_unixtime(min(timestamp)) as start, from_unixtime(max(timestamp)) as end from t_ti" 2>/dev/null'),
    ('indexer log 最近', 'tail -5 /tmp/indexer.log 2>/dev/null'),
]:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')
c.close()