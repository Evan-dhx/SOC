import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Compile unqlite_db.cpp verbose", r"""
echo "=== Compile unqlite_db.cpp ==="
cd /root/SOC/ly_analyser_src/agent/data
g++ -c -Wall -fPIC -g -std=c++17 -DAGENT -O2 -I. -I../../common -I/usr/include -I/usr/local/include -o unqlite_db.o unqlite_db.cpp 2>&1 | tail -30
echo "Exit: $?"
ls -la unqlite_db.o 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:3000]}")

client.close()
