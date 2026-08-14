import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check protobuf version on the server
i, o, e = c.exec_command("ldd /Server/bin/config_pusher | grep proto; echo ---; head -10 /var/log/messages 2>/dev/null | grep config_pusher", timeout=30)
print('Protobuf:', o.read().decode()[:300])

# Test config_updater directly
i, o, e = c.exec_command("curl -s -w '\nHTTP_CODE:%{http_code}' -X POST -d 'dev { id: 1 name: \"test\" }' http://127.0.0.1:10081/config_updater 2>&1", timeout=30)
print('Direct config_updater test:', o.read().decode()[:500])

# Check result
i, o, e = c.exec_command('grep -c "dev {" /Agent/data/config 2>/dev/null; echo; head -3 /Agent/data/config', timeout=30)
print('After direct test:', o.read().decode()[:200])

c.close()