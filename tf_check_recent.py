import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check only the most recent actl errors
i, o, e = c.exec_command('tail -20 /var/log/httpd/ly_error_log 2>/dev/null | grep -i "actl\|probe.*running\|config\.Config"', timeout=30)
print('Recent actl:', o.read().decode()[:500])

# Run ACTL STATUS directly and capture output
i, o, e = c.exec_command(r"tmpf=/tmp/actl_test_$$; printf 'node: NODE_PROBE\nsrv: SRV_ALL\nop: STATUS\nid: \"1\"\n' > $tmpf; curl -s -o /dev/null -w 'HTTP:%{http_code}' -X POST -d @$tmpf http://127.0.0.1:10081/actl; echo; rm -f $tmpf", timeout=30)
print('actl STATUS HTTP:', o.read().decode()[:100])

c.close()