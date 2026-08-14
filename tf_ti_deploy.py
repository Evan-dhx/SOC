import paramiko
import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 1. 创建目录并上传
def put_dir(sftp, local, remote):
    if not os.path.isdir(local):
        sftp.put(local, remote)
        return
    try:
        sftp.stat(remote)
    except FileNotFoundError:
        sftp.mkdir(remote)
    for name in os.listdir(local):
        put_dir(sftp, os.path.join(local, name), f"{remote}/{name}")

sftp = client.open_sftp()
put_dir(sftp, r'd:\QorderProject\SOC\ti_server', '/opt/ti_server')
sftp.close()
print("ti_server 已上传到 /opt/ti_server")

cmds = [
    ("初始化 + systemd 部署", r"""
chmod +x /opt/ti_server/install.sh
/opt/ti_server/install.sh 8090 2>&1 | tail -12
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()