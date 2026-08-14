import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ('本地DB文件', 'ls -la /Agent/data/db/ 2>/dev/null; echo ---; ls -la /Agent/data/eventdb/ 2>/dev/null'),
    ('DB文件大小', 'du -sh /Agent/data/db/ 2>/dev/null; du -sh /Agent/data/eventdb/ 2>/dev/null'),
    ('SQLite 表检查', 'sqlite3 /Agent/data/db/feature.db ".tables" 2>/dev/null; echo ---; sqlite3 /Agent/data/eventdb/event.db ".tables" 2>/dev/null'),
    ('feature记录数', 'sqlite3 /Agent/data/db/feature.db "SELECT count(1) FROM feature;" 2>/dev/null'),
    ('最新 feature', 'sqlite3 /Agent/data/db/feature.db "SELECT timestamp, sip, dip, dport, bytes FROM feature ORDER BY rowid DESC LIMIT 3;" 2>/dev/null'),
    ('检查 event', 'sqlite3 /Agent/data/eventdb/event.db "SELECT count(1) FROM event;" 2>/dev/null'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')
c.close()