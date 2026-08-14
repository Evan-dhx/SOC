import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("部署包 + 文档检查", r"""
echo "=== 1. dependence 目录内容 ==="
ls -la /root/SOC/ly_server_src/dependence/ 2>/dev/null
ls -la /root/SOC/ly_analyser_src/dependence/ 2>/dev/null
echo ""
echo "=== 2. db.server 包内容 ==="
tar tzf /root/SOC/ly_server_src/dependence/db.server.v1.1.231123.tar.gz 2>/dev/null | head -30
echo ""
echo "=== 3. /tmp/recreate_event_config.sql 内容（之前创建的） ==="
head -30 /tmp/recreate_event_config.sql 2>/dev/null
echo ""
echo "=== 4. /tmp/create_all_tables.sql 内容开头 ==="
head -40 /tmp/create_all_tables.sql 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
