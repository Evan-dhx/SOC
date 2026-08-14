import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

items = [
    # Current fsd process
    ('fsd 进程', 'ps -e | grep fsd; ls -la /home/Agent/bin/fsd; md5sum /home/Agent/bin/fsd'),
    # Compiled fsd binary
    ('已编译的 fsd', 'ls -la /root/SOC/ly_analyser_src/agent/handlers/fsd 2>/dev/null; md5sum /root/SOC/ly_analyser_src/agent/handlers/fsd 2>/dev/null'),
    # nftls process
    ('nftls 进程', 'ps -e | grep nftls | head -5'),
    # Config file
    ('配置文件', 'grep -E "psk:|port:|name:" /Agent/data/config | head -5'),
    # nftls.psk
    ('PSK 文件', 'cat /Agent/etc/nftls.psk 2>/dev/null; echo; ls -la /Agent/etc/nftls.psk 2>/dev/null'),
    # Recent fsd log
    ('fsd 日志', 'tail -8 /Agent/data/log'),
]

for label, cmd in items:
    print(f'\n[{label}]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:500])
    if err: print(f'ERR: {err[:200]}')
c.close()