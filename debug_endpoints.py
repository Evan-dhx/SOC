import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check what user endpoint actually returns
    ("user response", r"""
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null
echo "User response (hex):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1 | od -c | head -5
echo ""
echo "User response (raw):"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1
echo ""
"""),

    # Check config_user.cpp GET handler
    ("config_user GET", r"""
grep -n -A30 'case GET' /root/SOC/ly_server_src/lib/config_user.cpp | head -40
"""),

    # Check what columns the GET query reads
    ("user GET columns", r"""
sed -n '310,400p' /root/SOC/ly_server_src/lib/config_user.cpp
"""),

    # Check bwlist GET handler
    ("bwlist GET", r"""
grep -n -A30 'case GET\|Get()' /root/SOC/ly_server_src/lib/config_bwlist.cpp | head -50
"""),

    # Check event_ignore GET - maybe the issue is FROM_UNIXTIME in WHERE clause
    ("event_ignore GET detail", r"""
sed -n '1104,1170p' /root/SOC/ly_server_src/lib/config_event.cpp
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
