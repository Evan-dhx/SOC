import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

items = [
    ('check ScriptAlias path', 'ls -la /Agent/cmd/config_updater; ls -la /home/Agent/cmd/config_updater; md5sum /Agent/cmd/config_updater /home/Agent/cmd/config_updater 2>/dev/null'),
    ('httpd error log', 'tail -10 /var/log/httpd/error_log 2>/dev/null; echo ---; tail -10 /etc/httpd/logs/error_log 2>/dev/null'),
    ('httpd version', 'httpd -v 2>/dev/null; apachectl -v 2>/dev/null'),
    ('config file before curl', "echo 'controller { host: \"127.0.0.1\" port: \"10081\" }' > /Agent/data/config; wc -c /Agent/data/config"),
    ('curl with -v', "curl -v -X POST -H 'Content-Type: text/plain' -d 'dev { id: 1 name: \"test\" psk: \"abc123\" }' http://127.0.0.1:10081/config_updater 2>&1 | head -20"),
    ('config after curl verbose', 'echo === after curl ===; ls -la /Agent/data/config; wc -c /Agent/data/config'),
]
for label, cmd in items:
    print(f'\n[{label}]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:800])
    if err: print(f'ERR: {err[:200]}')
c.close()