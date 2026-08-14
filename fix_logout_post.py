import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Fix logout to handle POST properly
    ("fix logout POST", r"""
cat > /Server/www/d/logout << 'SCRIPT'
#!/bin/bash
echo "Content-Type: application/javascript; charset=UTF-8"
echo ""
echo '[{"code":200}]'
SCRIPT
chmod +x /Server/www/d/logout

# Verify
echo "=== File ==="
cat /Server/www/d/logout
echo ""
echo "=== GET test ==="
curl -s -o /dev/null -w "GET: %{http_code}\n" http://localhost/d/logout
echo "=== POST test ==="
curl -s -o /dev/null -w "POST: %{http_code}\n" -X POST http://localhost/d/logout
echo "=== POST with data ==="
curl -s -X POST http://localhost/d/logout -d "auth_target=logout" 2>&1
echo ""
"""),

    # Check error log
    ("check errors", "tail -3 /var/log/httpd/ly_error_log"),

    # Now verify everything with browser-like requests
    ("browser simulation", r"""
> /var/log/httpd/ly_error_log

# Step 1: Login
echo "1. Login"
RESP=$(curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin")
echo "   Response: $RESP"

# Step 2: Config agent (what overview page loads)
echo "2. Config agent"
curl -s -b /tmp/cookies http://localhost/d/config -d "auth_target=config&type=agent&op=get" 2>&1 | head -c 200
echo ""

# Step 3: Config device
echo "3. Config device"
curl -s -b /tmp/cookies http://localhost/d/config -d "auth_target=config&type=device&op=get" 2>&1 | head -c 200
echo ""

# Step 4: MO
echo "4. MO"
curl -s -b /tmp/cookies http://localhost/d/mo -d "auth_target=mo&op=get" 2>&1 | head -c 200
echo ""

# Step 5: Logout
echo "5. Logout"
curl -s -o /dev/null -w "   HTTP: %{http_code}\n" -X POST http://localhost/d/logout

# Check errors
echo ""
echo "6. Error log:"
cat /var/log/httpd/ly_error_log
echo "(end)"
"""),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
