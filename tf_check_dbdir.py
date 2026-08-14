import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ('20260814 目录内容', 'ls -la /Agent/data/db/20260814/ 2>/dev/null'),
    ('20260813 目录内容', 'ls -la /Agent/data/db/20260813/ 2>/dev/null | head -20'),
    ('找 db 文件', 'find /Agent/data/db -name "*.db" -o -name "*.sqlite" 2>/dev/null'),
    ('每种数据文件', 'file /Agent/data/db/20260813/* 2>/dev/null | head -10'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')
c.close()