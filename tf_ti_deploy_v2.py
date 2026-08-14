import paramiko
import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

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
# 删除旧 SQLite 库（已迁移 MySQL）
try:
    sftp.remove('/opt/ti_server/ti.db')
    sftp.remove('/opt/ti_server/ti.db-wal')
    sftp.remove('/opt/ti_server/ti.db-shm')
except FileNotFoundError:
    pass
sftp.close()
print("ti_server v2 已上传")

cmds = [
    ("部署 v2（MySQL + 双端口）", r"""
cd /opt/ti_server
chmod +x install.sh
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