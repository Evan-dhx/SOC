import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Test login with correct parameter names
    ("test login correct", r"""
curl -sv http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" 2>&1 | grep -E 'HTTP|Set-Cookie|code|\['
"""),
    
    # Check what the frontend sends
    ("frontend auth call", r"""
grep -rn 'auth_pass\|auth_user\|auth_target' /Server/www/ui/static/js/main.bff3bffb.chunk.js 2>/dev/null | head -5
echo "---"
# Also check in the non-minified source if available
grep -rn 'auth_pass\|auth_user' /root/SOC/ly_vis/packages/ 2>/dev/null | head -10
"""),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
