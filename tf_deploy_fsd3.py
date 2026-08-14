import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('find compiled binary', 'ls -la /root/SOC/ly_analyser_src/agent/handlers/fsd /root/SOC/ly_analyser_src/agent/handlers/actl 2>&1'),
    ('kill old fsd + deploy', 'pkill -x fsd 2>/dev/null; sleep 1; cp /root/SOC/ly_analyser_src/agent/handlers/fsd /home/Agent/bin/ 2>/dev/null; cp /root/SOC/ly_analyser_src/agent/handlers/actl /home/Agent/cmd/ 2>/dev/null; ls -la /home/Agent/bin/fsd /home/Agent/cmd/actl'),
    ('start fsd', '/home/Agent/bin/fsd > /dev/null 2>&1 &; sleep 3; pgrep -x fsd'),
    ('check processes', 'ps aux | grep -E "fsd|nftls" | grep -v grep | head -10'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()