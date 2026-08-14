import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # MySQL with correct password
    ('t_feature 记录数', "mysql -uroot -ppassword123 ly -e 'select count(1) from t_feature' 2>/dev/null"),
    ('t_event 记录数', "mysql -uroot -ppassword123 ly -e 'select count(1) from t_event' 2>/dev/null"),
    ('t_ti 记录数', "mysql -uroot -ppassword123 ly -e 'select count(1) from t_ti' 2>/dev/null"),
    ('最新 t_feature', "mysql -uroot -ppassword123 ly -e 'select * from t_feature order by id desc limit 3' 2>/dev/null"),
    # Latest nfcapd files
    ('nfcapd 文件列表', 'ls -la /data/flow/1/nfcapd.2026081409* 2>/dev/null; echo ---; ls -la /data/flow/1/nfcapd.current 2>/dev/null'),
    # Check nfdump
    ('nfdump test', 'nfdump -r /data/flow/1/nfcapd.202608140855 2>&1 | head -10'),
    # Restart indexer
    ('重启 indexer', 'pkill -x launch_indexer.sh 2>/dev/null; pkill -x indexer 2>/dev/null; pkill -x extractor 2>/dev/null; sleep 2; cd /Agent/bin; nohup bash launch_indexer.sh > /tmp/indexer.log 2>&1 &; sleep 5; ps -e | grep -E "indexer|extractor" | head -5'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=60)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:300]}')
c.close()