import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("服务器 common.h 检查 extern C", r"""
echo "=== 1. 服务器 common.h extern C 检查 ==="
grep -n "extern \"C\"\|#include" /root/SOC/ly_analyser_src/common/common.h | head -20
echo ""
echo "=== 2. 工作区 common.h 对比 ==="
echo "(本地文件)"; grep -n "extern \"C\"\|#include" /dev/null 2>/dev/null
echo ""
echo "=== 3. fsd.cpp 的 include 顺序 ==="
head -15 /root/SOC/ly_analyser_src/agent/handlers/fsd.cpp
echo ""
echo "=== 4. 服务器是否本来就有 strings.h 被删（git 检查） ==="
cd /root/SOC && git log --oneline -3 2>/dev/null; git status --short 2>/dev/null | head -5
ls -la /root/SOC/ly_analyser_src/common/strings.h
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:500]}")

client.close()