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
sftp.close()
print("已上传")

cmds = [
    ("建表 + 重启", r"""
cd /opt/ti_server
echo "=== 1. 初始化（建 t_client 表，幂等） ==="
TI_DB_PASS=password123 python3 server.py --init 2>&1 | head -3
echo ""
echo "=== 2. 重启 ==="
systemctl restart ti-server
sleep 3
systemctl is-active ti-server
echo ""
echo "=== 3. 默认客户端（兼容旧 key） ==="
mysql -uroot -ppassword123 ti_server -e "SELECT id,name,order_no,enabled,allowed_ips,update_window FROM t_client;" 2>/dev/null
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