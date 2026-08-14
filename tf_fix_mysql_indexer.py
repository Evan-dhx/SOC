import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ('MySQL 连接测试', "mysql -uroot -ppassword123 -e 'SELECT 1 as test'"),
    ('ly 数据库存在', "mysql -uroot -ppassword123 -e 'SHOW DATABASES' | grep ly"),
    ('mysql 版本', "mysql -uroot -ppassword123 -e 'SELECT version()'"),
    ('nftls 状态', 'cat /Agent/etc/nftls.status 2>/dev/null'),
    ('tf 数据文件', 'ls -la /data/flow/1/nfcapd.2026081409* 2>/dev/null'),
    ('indexer 当前进程', 'ps -e | grep -E "indexer|extract" | head -5'),
    ('启动 indexer (用setsid)', 'setsid bash /Agent/bin/launch_indexer.sh > /tmp/indexer.log 2>&1 &'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')

# Wait and check indexer
import time
time.sleep(5)
for label, cmd in [
    ('indexer 进程', 'ps -e | grep -E "indexer|extract" | head -5'),
    ('indexer log', 'cat /tmp/indexer.log 2>/dev/null | head -15'),
]:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')
c.close()