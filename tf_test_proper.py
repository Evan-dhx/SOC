import paramiko, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Test actl directly with a CtlReq TEXT FILE (no shell escaping issues)
i, o, e = c.exec_command(r"python3 -c "
open('/tmp/ctl.txt','w').write('node: NODE_PROBE\nsrv: SRV_ALL\nop: STATUS\nid: \"1\"\n')
" && curl -s -o /dev/null -w 'HTTP:%{http_code}' -X POST -d @/tmp/ctl.txt http://127.0.0.1:10081/actl", timeout=30)
print('actl test:', o.read().decode()[:200])

# Run actual config_pusher
i, o, e = c.exec_command('/Server/bin/config_pusher 2>&1', timeout=120)
print('Push:', o.read().decode()[:500])

time.sleep(5)
i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null | head -3', timeout=30)
print('tsensor.conf:', o.read().decode()[:200])

c.close()