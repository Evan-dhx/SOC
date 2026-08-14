import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check config.dev content
i, o, e = c.exec_command('cat /Agent/data/config.dev 2>/dev/null', timeout=30)
print('config.dev:', o.read().decode()[:1000])

# Check if actl can parse it
i, o, e = c.exec_command(r"printf 'node: NODE_PROBE\nsrv: SRV_ALL\nop: STATUS\nid: \"1\"\n' | curl -s -w '\nHTTP:%{http_code}\n' -X POST -d @- http://127.0.0.1:10081/actl 2>&1", timeout=30)
print('actl STATUS:', o.read().decode()[:500])

# Check apache error for actl
i, o, e = c.exec_command('tail -3 /var/log/httpd/ly_error_log 2>/dev/null', timeout=30)
print('Apache error:', o.read().decode()[:300])

c.close()