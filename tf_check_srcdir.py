import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('check src dir', 'ls -la /root/SOC/ly_analyser_src/ 2>/dev/null; echo "---"; ls /root/SOC/ly_analyser_src/handlers/ 2>/dev/null || echo "no handlers dir"'),
    ('find fsd location', 'find /root/SOC -name "fsd.cpp" 2>/dev/null; find /root/SOC -name "Makefile" -path "*/handlers/*" 2>/dev/null'),
    ('check build dir', 'ls /root/SOC/ly_analyser_src/build/ 2>/dev/null'),
    ('ls whole src', 'ls /root/SOC/ly_analyser_src/ 2>/dev/null'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()