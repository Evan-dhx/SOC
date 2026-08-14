import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('verify checksums', 'md5sum /root/SOC/ly_analyser_src/agent/handlers/fsd.cpp /root/SOC/ly_analyser_src/agent/handlers/actl.cpp'),
    ('compile handlers', 'cd /root/SOC/ly_analyser_src/agent && make handlers 2>&1 | tail -25'),
    ('check binaries', 'ls -la /root/SOC/ly_analyser_src/agent/build/handlers/fsd /root/SOC/ly_analyser_src/agent/build/handlers/actl 2>/dev/null; echo "---"; file /root/SOC/ly_analyser_src/agent/build/handlers/fsd 2>/dev/null'),
    ('deploy', 'pkill -x fsd 2>/dev/null; sleep 1; cp /root/SOC/ly_analyser_src/agent/build/handlers/fsd /home/Agent/bin/ 2>/dev/null; cp /root/SOC/ly_analyser_src/agent/build/handlers/actl /home/Agent/cmd/ 2>/dev/null; ls -la /home/Agent/bin/fsd /home/Agent/cmd/actl'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:2000])
    if err: print(f'STDERR: {err[:500]}')
    if label == 'deploy':
        stdin2, stdout2, stderr2 = client.exec_command('/home/Agent/bin/fsd > /dev/null 2>&1 &; sleep 3; ps aux | grep fsd | grep -v grep', timeout=30)
        out2 = stdout2.read().decode('utf-8', errors='replace')
        if out2: print(f'fsd started: {out2[:200]}')
client.close()