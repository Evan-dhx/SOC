import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sftp = client.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ti_server\server.py', '/opt/ti_server/server.py')
sftp.close()
print("server.py 已更新")

cmds = [
    ("重新部署", r"""
cd /opt/ti_server
TI_DB_PASS=password123 ./install.sh 8090 8091 2>&1 | tail -14
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()