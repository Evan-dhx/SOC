import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Start fsd via a separate script to avoid bash syntax issues
stdin, stdout, stderr = client.exec_command("cat > /tmp/start_fsd.sh << 'SCRIPT'\n#!/bin/bash\nnohup /home/Agent/bin/fsd > /dev/null 2>&1 &\nsleep 3\npgrep -x fsd\necho fsd_started=$?\nSCRIPT\nchmod +x /tmp/start_fsd.sh\n/tmp/start_fsd.sh", timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err: print(f'STDERR: {err[:500]}')

# Check fsd and nftls
for label, cmd in [
    ('processes', 'ps -e | grep -E "fsd|nftls|probe|fcapd" | head -10'),
    ('log', 'tail -10 /Agent/data/log'),
    ('nftls server', 'cat /Agent/etc/nftls.psk; echo; ss -tlnp | grep 199'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()