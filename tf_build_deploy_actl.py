import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Sync modified actl.cpp
sftp = c.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ly_analyser\src\agent\handlers\actl.cpp',
         '/root/SOC/ly_analyser_src/agent/handlers/actl.cpp')
sftp.close()
print('Uploaded actl.cpp')

# Rebuild actl
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/handlers && rm -f actl.o && make actl 2>&1 | tail -10', timeout=120)
print('Compile:', o.read().decode()[:500])

# Deploy
i, o, e = c.exec_command('cp /root/SOC/ly_analyser_src/agent/handlers/actl /Agent/cmd/; ls -la /Agent/cmd/actl', timeout=30)
print('Deploy:', o.read().decode()[:200])

# Test with proper CtlReq
i, o, e = c.exec_command("""
printf 'node: NODE_PROBE
srv: SRV_ALL
op: RESTART
id: "1"
' > /tmp/ctl_req.txt && curl -s -X POST -d @/tmp/ctl_req.txt http://127.0.0.1:10081/actl 2>&1
""", timeout=30)
print('actl test:', o.read().decode()[:500])

c.close()
print('\nDone')