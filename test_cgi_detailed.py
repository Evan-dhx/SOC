import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Create a simple test CGI to verify CGI works
    ("test cgi basic", r"""
cat > /Server/www/d/test.cgi << 'EOF'
#!/bin/bash
echo "Content-Type: text/plain"
echo ""
echo "CGI works!"
EOF
chmod +x /Server/www/d/test.cgi
curl -s http://localhost/d/test.cgi 2>&1
"""),
    
    # 2. Run auth with POST data (simulating login)
    ("auth with POST", r"""
echo -n "auth_target=login&user=admin&pass=admin" | \
REQUEST_METHOD=POST SCRIPT_NAME=/d/auth REMOTE_ADDR=127.0.0.1 \
CONTENT_TYPE=application/x-www-form-urlencoded CONTENT_LENGTH=37 \
/Server/www/d/auth 2>&1
echo ""
echo "Exit: $?"
"""),
    
    # 3. Run auth with full CGI env including POST
    ("auth POST full", r"""
printf "auth_target=login&user=admin&pass=admin" | \
env REQUEST_METHOD=POST SCRIPT_NAME=/d/auth REMOTE_ADDR=127.0.0.1 \
CONTENT_TYPE=application/x-www-form-urlencoded CONTENT_LENGTH=37 \
/Server/www/d/auth 2>/tmp/auth_stderr
echo "STDOUT exit: $?"
echo "STDERR:"
cat /tmp/auth_stderr
"""),
    
    # 4. Check if the issue is the HTTPContentHeader output
    ("check header output", r"""
# The C++ code does: cout << header; cout << "[{\"code\": " << code << "}]"<<endl;
# Let's see what HTTPContentHeader outputs
# It should output "Content-Type: application/javascript; charset=UTF-8\n\n"
# Maybe the issue is the header doesn't include the blank line

# Let's check by looking at cgicc source
grep -n 'HTTPContentHeader\|operator<<' /usr/include/cgicc/HTTPContentHeader.h 2>/dev/null | head -10
echo "---"
grep -rn 'operator<<.*HTTPContentHeader' /usr/include/cgicc/ 2>/dev/null | head -5
"""),
    
    # 5. Try curl with POST to auth
    ("curl POST auth", r"""
curl -sv http://localhost/d/auth -d "auth_target=login&user=admin&pass=admin" 2>&1 | head -30
"""),
    
    # 6. Check if there's a different CGI error now
    ("check all errors", r"""
tail -20 /var/log/httpd/ly_error_log | grep -v '19:0[0-5]'
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
