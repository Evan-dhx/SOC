import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Check what the frontend login component sends
    ("login component source", r"""
grep -rn 'auth_pass\|auth_user\|auth_target\|login' /root/SOC/ly_vis/packages/std/src/ 2>/dev/null | grep -i 'login\|auth' | head -20
"""),
    
    # 2. Check the login page component
    ("login page", r"""
find /root/SOC/ly_vis/packages/std/src/ -name '*login*' -o -name '*Login*' 2>/dev/null
"""),
    
    # 3. Check the request utility that makes API calls
    ("request util", r"""
grep -rn 'baseUrl\|/d/\|auth_target\|auth_pass\|auth_user' /root/SOC/ly_vis/packages/std/src/ 2>/dev/null | head -20
"""),
    
    # 4. Check app-config
    ("app config", r"""
cat /Server/www/ui/app-config/config.js
"""),
    
    # 5. Check what the frontend sends for the overview page
    ("overview api calls", r"""
# The overview page likely calls config endpoint to get device list
# Let's check what happens when we call config
curl -s http://localhost/d/config 2>&1 | head -5
echo "---"
# Check with POST
curl -s http://localhost/d/config -d "auth_target=config" 2>&1 | head -5
echo "---"
# Check error log for recent errors
tail -10 /var/log/httpd/ly_error_log
"""),
    
    # 6. Check the request flow - what does the frontend request on page load
    ("check request flow", r"""
# The frontend code has a request utility. Let's find it.
grep -rn 'requestCallBack\|requestErrCallBack\|responseCallBack' /root/SOC/ly_vis/packages/std/src/ 2>/dev/null | head -10
echo "==="
# Find the main request function
grep -rn 'fetch\|axios\|XMLHttpRequest\|\.post\|\.get' /root/SOC/ly_vis/packages/std/src/utils/ 2>/dev/null | head -20
"""),
    
    # 7. Check the error message source
    ("error message source", r"""
grep -rn '客户端错误\|请检查地址' /root/SOC/ly_vis/packages/ 2>/dev/null | head -10
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
