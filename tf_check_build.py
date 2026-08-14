import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check server-side build capability
items = [
    ('ly_vis source on server', 'ls -la /root/SOC/ly_vis_src 2>/dev/null || echo "not found"'),
    ('node/node_modules', 'node --version 2>/dev/null; npm --version 2>/dev/null'),
    ('Server www ui build', 'ls -la /Server/www/ui/ | head -5; echo "---"; head -1 /Server/www/ui/index.html 2>/dev/null'),
    ('packages std source', 'ls /root/SOC/ly_vis_src/packages 2>/dev/null || echo "no src"'),
]
for label, cmd in items:
    print(f'\n[{label}]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:500])
    if err: print(f'ERR: {err[:200]}')
c.close()