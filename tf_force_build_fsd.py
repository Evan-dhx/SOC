import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('force recompile fsd+actl', 'cd /root/SOC/ly_analyser_src/agent/handlers; rm -f fsd.o actl.o fsd actl; make fsd actl 2>&1 | tail -20'),
    ('check compiled', 'ls -la fsd actl; file fsd; echo "---"; file actl'),
    ('deploy', 'pkill -x fsd 2>/dev/null; sleep 1; cp fsd /home/Agent/bin/; cp actl /home/Agent/cmd/; ls -la /home/Agent/bin/fsd /home/Agent/cmd/actl'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:2000])
    if err: print(f'STDERR: {err[:500]}')
client.close()