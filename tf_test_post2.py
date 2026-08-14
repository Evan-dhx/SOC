import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('restore config', "echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; echo restored; wc -c /Agent/data/config"),
    ('curl POST test', """curl -s -X POST -d 'controller { host: "127.0.0.1" port: "10081" } dev { id: 1 name: "test" psk: "abc123" }' http://127.0.0.1:10081/config_updater 2>&1; echo; echo CURL_EXIT=$?"""),
    ('config after curl', 'echo === config ===; cat /Agent/data/config; echo; wc -c /Agent/data/config'),
    ('run production pusher', '/home/Server/bin/config_pusher > /tmp/pusher2.log 2>&1; echo PUSHER_EXIT=$?'),
    ('config after pusher', 'echo === config ===; cat /Agent/data/config; echo; wc -c /Agent/data/config'),
    ('pusher log', 'cat /tmp/pusher2.log; echo; wc -c /tmp/pusher2.log'),
    ('error log', 'tail -5 /Agent/data/log'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
    time.sleep(0.3)
client.close()