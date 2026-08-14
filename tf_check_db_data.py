import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ('数据库连接测试', "mysql -uroot -proot -e 'show databases' 2>&1 | head -10"),
    ('ly库表列表', "mysql -uroot -proot ly -e 'show tables' 2>/dev/null"),
    ('t_feature 表结构', "mysql -uroot -proot ly -e 'desc t_feature' 2>/dev/null | head -5"),
    ('t_feature 实际查询', "mysql -uroot -proot ly -e 'select count(1) as cnt from t_feature' 2>/dev/null"),
    ('nfcapd 最新数据目录', "ls -la /data/flow/1/nfcapd.2026081409* 2>/dev/null; echo ---; ls -la /data/flow/1/ 2>/dev/null | tail -8"),
    ('nfdump 读最近的关闭文件', "nfdump -r /data/flow/1/nfcapd.202608140855 -c 5 2>/dev/null | head -10"),
    ('indexer 是否在处理', "ls -la /Agent/data/indexer_* 2>/dev/null; echo ---; stat /Agent/data/indexer_feature 2>/dev/null | grep Modify"),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:300]}')
c.close()