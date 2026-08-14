import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check ly_vis structure
    "echo '=== ly_vis local structure ==='",
    "ls -la /root/SOC/ly_vis/ 2>/dev/null",
    
    "echo '=== ly_vis package.json ==='",
    "cat /root/SOC/ly_vis/package.json 2>/dev/null",
    
    "echo '=== ly_vis lerna.json ==='",
    "cat /root/SOC/ly_vis/lerna.json 2>/dev/null",
    
    "echo '=== ly_vis packages ==='",
    "ls -la /root/SOC/ly_vis/packages/ 2>/dev/null",
    
    "echo '=== Check if node/yarn available ==='",
    "node --version 2>/dev/null || echo 'node not installed'",
    "yarn --version 2>/dev/null || echo 'yarn not installed'",
    "npm --version 2>/dev/null || echo 'npm not installed'",
    
    "echo '=== Check Server/www/ui ==='",
    "ls -la /Server/www/ui/ 2>/dev/null",
]

for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out)
    if err and 'warning' not in err.lower():
        print(f"STDERR: {err}")
    print()

client.close()
