import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ('MySQL 配置', 'cat /etc/my.cnf.d/gl.server.cnf 2>/dev/null; echo ===; grep -rn "user.*root\|password\|database" /etc/my.cnf* 2>/dev/null | head -10'),
    ('ly_server DB 配置', 'cat /root/SOC/ly_server_src/common/config.ini 2>/dev/null; echo ===; cat /Server/config.ini 2>/dev/null; echo ===; find /Server -name "*.ini" -exec cat {} \\; 2>/dev/null'),
    ('ly 库连接尝试', "mysql -uadmin -padmin ly -e 'show tables' 2>&1 | head -20"),
    ('ly 库备选密码', "mysql -uroot -pPP@ssw0rd ly -e 'show tables' 2>&1 | head -20"),
    ('indexer 启动参数', 'ps -ef | grep indexer | grep -v grep'),
    ('launch_indexer', 'cat /Agent/bin/launch_indexer.sh 2>/dev/null'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:300]}')
c.close()