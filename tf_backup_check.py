import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("服务器原版源码排查", r"""
echo "=== 1. handlers 目录完整列表 ==="
ls /root/SOC/ly_analyser_src/agent/handlers/ | head -40
echo ""
echo "=== 2. oldabi 相关 ==="
ls /root/SOC/ly_analyser_src/agent/handlers/*oldabi* 2>/dev/null
ls /root/SOC/ly_analyser_src/ | head -10
echo ""
echo "=== 3. 其他备份目录 ==="
find /root/SOC/ly_analyser_src -name "*.bak*" -o -name "*old*" 2>/dev/null | grep -vE "\.o$|\.a$" | head -10
echo ""
echo "=== 4. 部署的 actl 二进制反查源码线索 ==="
ls -la /home/Agent/cmd/actl 2>/dev/null
strings /home/Agent/cmd/actl 2>/dev/null | grep -c "trim"
echo ""
echo "=== 5. 工作区 handlers 列表（actl.cpp 是否有 strings.h） ==="
echo "(本地)"; grep -n "strings.h" "d:\QorderProject\SOC\ly_analyser\src\agent\handlers\actl.cpp" 2>/dev/null || echo "本地无"
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