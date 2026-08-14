import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Fix logout - check why it returns 404
    ("fix logout", r"""
# Check current logout file
echo "=== logout file ==="
ls -la /Server/www/d/logout
cat /Server/www/d/logout
echo ""
echo "=== file type ==="
file /Server/www/d/logout
echo ""
echo "=== test directly ==="
/Server/www/d/logout 2>&1
echo ""
echo "=== test via curl ==="
curl -sv http://localhost/d/logout 2>&1 | tail -15
"""),
    
    # 2. The issue might be that Apache CGI requires specific setup
    # Let's check if the ScriptAlias covers all files
    ("check cgi setup", r"""
echo "=== Apache config ==="
cat /etc/httpd/conf.d/ly_server.conf
echo ""
echo "=== Test with POST ==="
curl -sv -X POST http://localhost/d/logout 2>&1 | tail -15
"""),
    
    # 3. The logout might need to be handled by the auth script
    # Let's make logout a copy of auth
    ("logout as auth copy", r"""
# Copy auth to logout - auth handles logout via auth_target parameter
cp /Server/www/d/auth /Server/www/d/logout
chmod +x /Server/www/d/logout
echo "logout replaced with auth binary"
ls -la /Server/www/d/logout
echo ""
curl -sv -X POST http://localhost/d/logout 2>&1 | tail -10
"""),
    
    # 4. Fix config returning empty - the frontend sends type=device
    # but config_device.so doesn't exist. Frontend actually sends type=agent
    # Let's check what the browser actually requests
    ("check config types", r"""
# The frontend config-agent.js sends type='agent'
# Let's verify agent config works
echo "=== agent config ==="
curl -s http://localhost/d/config -d "auth_target=config&type=agent&op=get" 2>&1
echo ""
echo "=== device config (fails) ==="
curl -s http://localhost/d/config -d "auth_target=config&type=device&op=get" 2>&1
echo ""
# The issue: frontend might send type=device somewhere
# Let's search the built JS for what types are sent
grep -o "type:'[a-z]*'" /Server/www/ui/static/js/main.bff3bffb.chunk.js 2>/dev/null | sort -u
echo "---"
grep -o 'type:"[a-z]*"' /Server/www/ui/static/js/main.bff3bffb.chunk.js 2>/dev/null | sort -u
"""),
    
    # 5. Create config_device.so as a symlink to config_agent.so
    ("create device so", r"""
# The frontend may send type=device. Create config_device.so
# First check if config_agent.so handles device data
ln -sf /Server/lib/config_agent.so /Server/lib/config_device.so
echo "Created symlink: config_device.so -> config_agent.so"
ls -la /Server/lib/config_device.so
echo ""
# Test
curl -s http://localhost/d/config -d "auth_target=config&type=device&op=get" 2>&1 | head -c 300
echo ""
"""),
    
    # 6. Also check what other .so files might be needed
    ("check all needed sos", r"""
# Find all type values used in frontend
grep -oP "type:\s*['\"](\w+)['\"]" /Server/www/ui/static/js/main.bff3bffb.chunk.js 2>/dev/null | sort -u
echo "==="
# Check which .so files exist vs which are needed
echo "Existing .so files:"
ls /Server/lib/config_*.so 2>/dev/null
"""),
    
    # 7. Final comprehensive test
    ("final test", r"""
> /var/log/httpd/ly_error_log

echo "=== Login ==="
curl -s -D /tmp/h http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin"
echo ""
COOKIE=$(grep 'Set-Cookie' /tmp/h | sed 's/.*SESSION_ID=\([^;]*\).*/\1/')
echo "Session: $COOKIE"

echo ""
echo "=== Config agent (with session) ==="
curl -s -b "SESSION_ID=$COOKIE" http://localhost/d/config -d "auth_target=config&type=agent&op=get" 2>&1 | head -c 300
echo ""

echo ""
echo "=== Config device (with session) ==="
curl -s -b "SESSION_ID=$COOKIE" http://localhost/d/config -d "auth_target=config&type=device&op=get" 2>&1 | head -c 300
echo ""

echo ""
echo "=== Logout ==="
curl -s -o /dev/null -w "HTTP: %{http_code}\n" -X POST http://localhost/d/logout
echo ""
echo "=== Error log ==="
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
