import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

items = [
    ('restore', "echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; wc -c /Agent/data/config"),
    ('curl POST', "curl -s -X POST -H 'Content-Type: text/plain' -d 'controller { host: \"127.0.0.1\" port: \"10081\" } dev { id: 1 name: \"test\" psk: \"abc123\" }' http://127.0.0.1:10081/config_updater 2>&1; echo; echo CURL_EXIT=$?"),
    ('config after curl', 'echo === config ===; cat /Agent/data/config; echo; wc -c /Agent/data/config'),
    ('restore2', "echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; wc -c /Agent/data/config"),
    ('pusher', '/home/Server/bin/config_pusher > /tmp/pusher_test.log 2>&1; echo EXIT=$?'),
    ('config after pusher', 'echo === pusher ===; grep -E \"psk:|port:|name:\" /Agent/data/config | head -5; wc -c /Agent/data/config'),
    ('pusher log', 'cat /tmp/pusher_test.log | head -5'),
]
for label, cmd in items:
    print(f'\n[{label}]')
    i, o, e = c.exec_command(cmd, timeout=60)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:600])
    if err: print(f'ERR: {err[:200]}')
c.close()