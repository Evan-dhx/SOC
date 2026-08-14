import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("部署状态检查", r"""
echo "=== 1. 服务状态 ==="
systemctl status ti-server --no-pager 2>&1 | head -8
echo ""
echo "=== 2. 端口监听 ==="
ss -tlnp 2>/dev/null | grep 8090 || echo "8090 未监听"
echo ""
echo "=== 3. 数据库与文件 ==="
ls -la /opt/ti_server/
echo ""
echo "=== 4. 服务日志 ==="
journalctl -u ti-server --no-pager -n 8 2>/dev/null | tail -8
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()