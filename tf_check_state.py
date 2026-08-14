import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('进程状态', 'ps -e | grep -E "tsensor|nftls|fcapd|fsd|indexer" | head -10'),
    ('TLS状态文件', 'cat /Agent/etc/nftls.status 2>/dev/null'),
    ('TLS端口', 'ss -tlnp | grep 19996; ss -uln | grep -E "999[56]"'),
    ('nfcapd数据', 'ls -la /data/flow/1/ 2>/dev/null | tail -5'),
    ('配置', 'grep -E "psk:|port:" /Agent/data/config'),
    ('indexer处理进度', 'cat /Agent/data/indexer_process 2>/dev/null | head -5'),
    ('agent日志', 'tail -10 /Agent/data/log'),
]:
    print(f'\n=== {label} ===')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:1000])
    if err: print(f'ERR: {err[:300]}')
c.close()