import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Clear old error log for clean test
    ("clear log", "> /var/log/httpd/ly_error_log"),
    
    # Full browser flow test
    ("full flow test", r"""
# 1. Login
echo "=== Login ==="
RESP=$(curl -s -D /tmp/headers http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" 2>/dev/null)
echo "Response: $RESP"
COOKIE=$(grep 'Set-Cookie' /tmp/headers | sed 's/.*SESSION_ID=\([^;]*\).*/\1/')
echo "Session: $COOKIE"

# 2. Access config with session
echo ""
echo "=== Config ==="
curl -s -b "SESSION_ID=$COOKIE" http://localhost/d/config 2>&1 | head -3

# 3. Access event with session
echo ""
echo "=== Event ==="
curl -s -b "SESSION_ID=$COOKIE" http://localhost/d/event 2>&1 | head -3

# 4. Access bwlist with session
echo ""
echo "=== BWList ==="
curl -s -b "SESSION_ID=$COOKIE" http://localhost/d/bwlist 2>&1 | head -3

# 5. Access mo with session
echo ""
echo "=== MO ==="
curl -s -b "SESSION_ID=$COOKIE" http://localhost/d/mo 2>&1 | head -3

# 6. Access internalip with session
echo ""
echo "=== InternalIP ==="
curl -s -b "SESSION_ID=$COOKIE" http://localhost/d/internalip 2>&1 | head -3
"""),
    
    # Check for any new errors
    ("check new errors", r"""
echo "=== Error log (should be empty or minimal) ==="
cat /var/log/httpd/ly_error_log
echo "=== End ==="
"""),
    
    # Summary
    ("summary", r"""
echo "============================================"
echo "  DEPLOYMENT STATUS"
echo "============================================"
echo ""
echo "Server: 10.10.102.220 (AlmaLinux 9)"
echo ""
echo "Services:"
for svc in httpd mariadb crond firewalld; do
  echo "  $svc: $(systemctl is-active $svc)"
done
echo ""
echo "Frontend: http://10.10.102.220/ui/"
echo "  Status: $(curl -s -o /dev/null -w '%{http_code}' http://localhost/ui/)"
echo ""
echo "API Endpoints:"
for ep in auth config event bwlist mo internalip; do
  code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost/d/$ep)
  echo "  /d/$ep: $code"
done
echo ""
echo "Database: $(mysql -u root -p'password123' server -e 'SELECT COUNT(*) AS tables FROM information_schema.tables WHERE table_schema="server";' 2>/dev/null | tail -1) tables"
echo ""
echo "Login: admin / admin"
echo "============================================"
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
