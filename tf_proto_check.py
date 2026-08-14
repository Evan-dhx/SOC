import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("服务器 proto 文件核对", r"""
echo "=== 1. 服务器 ly_server common proto 列表 ==="
ls /root/SOC/ly_server_src/common/*.proto 2>/dev/null
echo ""
echo "=== 2. config_agent.proto 是否存在 ==="
ls -la /root/SOC/ly_server_src/common/config_agent.proto 2>/dev/null || echo "不存在"
echo ""
echo "=== 3. config.proto 的 package 和 Device ==="
grep -n "package\|message Device" /root/SOC/ly_server_src/common/config.proto 2>/dev/null | head -5
echo ""
echo "=== 4. config_agent.h include ==="
grep -n "include\|namespace" /root/SOC/ly_server_src/lib/config_agent.h 2>/dev/null | head -10
echo ""
echo "=== 5. config_class.cpp namespace ==="
grep -n "namespace\|include" /root/SOC/ly_server_src/lib/config_class.cpp 2>/dev/null | head -10
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()