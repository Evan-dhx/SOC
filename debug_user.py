import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check t_user structure
    ("t_user structure", r"""
mysql -u root -p'password123' server -e "DESCRIBE t_user;" 2>&1
"""),

    # Check t_event_ignore structure
    ("t_event_ignore structure", r"""
mysql -u root -p'password123' server -e "DESCRIBE t_event_ignore;" 2>&1
"""),

    # Test user query directly
    ("test user query", r"""
mysql -u root -p'password123' server -e "SELECT \`id\`, \`name\`, \`lasttime\`, \`lastip\`, \`level\`, \`createtime\`, \`comment\`, \`disabled\`, \`creator\`, \`lockedtime\`, \`resource\` FROM \`t_user\` WHERE 1;" 2>&1
"""),

    # Check what config_user.so actually queries
    ("config_user SELECT", r"""
grep -n 'SELECT.*t_user' /root/SOC/ly_server_src/lib/config_user.cpp
"""),

    # Try the user endpoint with verbose curl
    ("verbose user test", r"""
curl -sv -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1 | tail -15
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
