import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check config file content around line 19
i, o, e = c.exec_command("sed -n '15,25p' /Agent/data/config", timeout=30)
print('Config lines 15-25:', o.read().decode()[:500])

# Check if CachedConfig::Create works via actl in debug
i, o, e = c.exec_command(r"printf 'node: NODE_PROBE\nsrv: SRV_ALL\nop: STATUS\nid: \"1\"\n' > /tmp/actl_req2.txt && curl -s -w '\nHTTP:%{http_code}\n' -X POST -d @/tmp/actl_req2.txt http://127.0.0.1:10081/actl 2>&1", timeout=30)
print('actl STATUS:', o.read().decode()[:500])

c.close()