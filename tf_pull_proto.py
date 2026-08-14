import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sftp = client.open_sftp()
sftp.get('/root/SOC/ly_server_src/lib/config_agent.proto', r'd:\QorderProject\SOC\ly_server\src\lib\config_agent.proto')
sftp.close()
print("已拉取 config_agent.proto")

cmds = [
    ("config_agent.proto Device 定义", r"""
grep -n -A30 "^message Device" /root/SOC/ly_server_src/lib/config_agent.proto | head -40
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:500]}")

client.close()