import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    'cat /tmp/pusher_test.log 2>/dev/null; echo "---FILE SIZE---"; wc -c /tmp/pusher_test.log 2>/dev/null',
    'journalctl -u httpd -n 10 --no-pager 2>/dev/null || tail -20 /var/log/messages 2>/dev/null || echo "no logs"',
    'grep -r "config_pusher\|push" /var/log/messages 2>/dev/null | tail -10',
    'REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=GET /home/Agent/cmd/config_updater 2>/dev/null',
    'ls -la /Agent/data/',
]
for cmd in cmds:
    print(f'\n=== {cmd[:70]} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1000])
    if err: print(f'STDERR: {err[:500]}')
client.close()