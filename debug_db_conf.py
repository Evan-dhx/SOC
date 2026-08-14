import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Verify file exists and is readable
    ("file check", r"""
ls -la /etc/my.cnf.d/gl.server.cnf
echo "---content---"
cat /etc/my.cnf.d/gl.server.cnf
echo "---hex---"
xxd /etc/my.cnf.d/gl.server.cnf | head -5
echo "---readable by apache?---"
su -s /bin/bash apache -c "cat /etc/my.cnf.d/gl.server.cnf" 2>&1
"""),
    
    # Check if there's a Windows line ending issue
    ("line endings", r"""
file /etc/my.cnf.d/gl.server.cnf
od -c /etc/my.cnf.d/gl.server.cnf | head -5
"""),
    
    # Check if the binary can find the file (strace)
    ("strace auth", r"""
timeout 5 strace -e openat su -s /bin/bash apache -c "/Server/www/d/auth" 2>&1 | grep -i 'my.cnf\|gl.server\|passwd\|No such' | head -10
"""),
    
    # Alternative: check if cppdb reads from standard mysql config
    ("mysql default config", r"""
ls -la /etc/my.cnf /etc/my.cnf.d/ 2>/dev/null
echo "---"
cat /etc/my.cnf 2>/dev/null
echo "---"
ls /etc/my.cnf.d/ 2>/dev/null
"""),
    
    # Try a different approach: put the config in standard location
    ("standard location", r"""
# cppdb mysql backend reads from standard MySQL config files
# Let's add our group to /etc/my.cnf.d/client.cnf or create a standard one
cat > /etc/my.cnf.d/gl.server.cnf << 'EOF'
[gl.server]
user=root
password=password123
database=server
EOF
chmod 644 /etc/my.cnf.d/gl.server.cnf
echo "New config:"
cat /etc/my.cnf.d/gl.server.cnf
"""),
    
    # Test again
    ("test again", r"""
su -s /bin/bash apache -c "/Server/www/d/auth" 2>&1 | head -5
echo "---"
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost/d/auth
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
