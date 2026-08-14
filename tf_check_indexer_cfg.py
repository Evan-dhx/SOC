import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check indexer config for DB info
    ('indexer 源码DB配置', 'grep -rn "database\|host.*127\|ly_server\|mysql" /root/SOC/ly_analyser_src/agent/indexing/*.cpp 2>/dev/null | head -10'),
    ('indexer 配置文件', 'find /Agent -name "*.ini" -o -name "*.conf" -o -name "*.cfg" 2>/dev/null | xargs grep -l "mysql\|database" 2>/dev/null'),
    ('check indexer exit log', 'cat /tmp/idx.log 2>/dev/null | grep -iE "error|fail|warn|exception|mysql" | head -10'),
    ('全量 indexer log', 'cat /tmp/idx.log 2>/dev/null | tail -20'),
    ('check indexer_feature', 'stat /Agent/data/indexer_feature 2>/dev/null'),
    ('check /Agent/data files date', 'ls -la /Agent/data/indexer_* /Agent/data/log 2>/dev/null'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')
c.close()