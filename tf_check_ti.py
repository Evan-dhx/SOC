import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check ti_server process
    ('ti_server 进程', 'ps -e | grep -E "ti_|python" | head -5'),
    # Check TI data files
    ('TI 数据文件', 'ls -la /Agent/data/ti_dns /Agent/data/mining_domain /Agent/data/mining_ip /Agent/data/sus_threat 2>/dev/null'),
    ('sus_threat 时间', 'stat /Agent/data/sus_threat 2>/dev/null | grep Modify'),
    ('ti_dns 时间', 'stat /Agent/data/ti_dns 2>/dev/null | grep Modify'),
    ('mining_domain 时间', 'stat /Agent/data/mining_domain 2>/dev/null | grep Modify'),
    # Check cron or systemd for TI update
    ('cron TI 任务', 'crontab -l 2>/dev/null | grep -iE "ti_|threat|update" | head -5'),
    ('systemd TI 服务', 'systemctl list-units --type=service --state=running 2>/dev/null | grep -iE "ti_|threat" | head -5'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')
c.close()