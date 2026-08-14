import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ('ti_server 服务详情', 'systemctl status ti-server 2>&1 | head -15'),
    ('ti_server 路径', 'which python3; ls -la /usr/local/bin/ti_server /usr/bin/ti_server /root/ti_server/server.py 2>/dev/null; find / -name "server.py" -path "*ti*" 2>/dev/null | head -5'),
    ('ti_server 启动参数', "ps -ef | grep python | grep -v grep"),
    ('cron 任务', 'crontab -l 2>/dev/null; echo ---; cat /etc/crontab 2>/dev/null; echo ---; ls /etc/cron.d/ 2>/dev/null'),
    ('TI 更新方式', 'cat /root/ti_server/README.md 2>/dev/null | head -20'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:1000])
    if err: print(f'ERR: {err[:200]}')
c.close()