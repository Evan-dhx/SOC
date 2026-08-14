import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Test actl with a proper restart request
i, o, e = c.exec_command(r"""printf 'node: NODE_PROBE
srv: SRV_ALL
op: RESTART
id: "1"
' > /tmp/actl_req.txt && curl -s -w '\nHTTP:%{http_code}\n' -X POST -d @/tmp/actl_req.txt http://127.0.0.1:10081/actl 2>&1""", timeout=30)
print('actl test:', o.read().decode()[:500])

# Also check apache error log for details
i, o, e = c.exec_command('tail -5 /var/log/httpd/ly_error_log 2>/dev/null', timeout=30)
print('Apache error:', o.read().decode()[:500])

c.close()