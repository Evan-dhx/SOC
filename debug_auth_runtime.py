import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Run auth binary directly with CGI env
    ("run auth with env", r"""
REQUEST_METHOD=POST SCRIPT_NAME=/d/auth REMOTE_ADDR=127.0.0.1 CONTENT_TYPE=application/x-www-form-urlencoded CONTENT_LENGTH=0 /Server/www/d/auth 2>&1
"""),
    
    # Also try with GET
    ("run auth GET", r"""
REQUEST_METHOD=GET SCRIPT_NAME=/d/auth REMOTE_ADDR=127.0.0.1 QUERY_STRING=auth_target=auth /Server/www/d/auth 2>&1
"""),
    
    # Check if the binary has ABI issues with libcommon.so
    ("check libcommon", r"""
ldd /Server/www/d/auth | grep common
echo "---"
ls -la /lib64/libcommon.so
echo "---"
file /lib64/libcommon.so
"""),
    
    # Check if the issue is the auth.cpp api_set variable
    ("check api_set", r"""
grep -n 'api_set' /root/SOC/ly_server_src/server/auth.cpp | head -10
"""),
    
    # Try running with strace-like approach using LD_DEBUG
    ("ld debug", r"""
LD_DEBUG=libs REQUEST_METHOD=GET SCRIPT_NAME=/d/auth REMOTE_ADDR=127.0.0.1 /Server/www/d/auth 2>&1 | grep -i 'error\|fail\|cannot' | head -10
"""),
    
    # Check if the binary crashes with a core dump
    ("ulimit core", r"""
ulimit -c unlimited
REQUEST_METHOD=GET SCRIPT_NAME=/d/auth REMOTE_ADDR=127.0.0.1 /Server/www/d/auth 2>&1
echo "Exit code: $?"
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
