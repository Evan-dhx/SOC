import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ('pusher 日志', 'cat /tmp/pusher_prod.log 2>/dev/null | head -20'),
    ('手动 curl POST', "curl -s -X POST -d 'dev { id: 1 name: \"test-dev\" psk: \"abc123\" }' http://127.0.0.1:10081/config_updater 2>&1 | head -10"),
    ('curl 后查看配置', "grep -A10 '^dev {' /Agent/data/config 2>/dev/null; echo '---'; head -30 /Agent/data/config 2>/dev/null"),
    ('MySQL t_device tls_psk', "mysql -uroot -proot ly -e 'select id,name,tls_psk,tls_status from t_device' 2>/dev/null"),
    ('pusher SQL 核对', "mysql -uroot -proot ly -e 'select t1.id, t1.name, t1.ip, t1.tls_psk, t2.id, t2.ip from t_device t1 join t_agent t2 on t1.agentid=t2.id' 2>/dev/null"),
]
for label, cmd in cmds:
    print(f'\n[{label}]')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out[:500])
    if err: print(f'STDERR: {err[:500]}')
client.close()