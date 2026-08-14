import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("common 目录核对", r"""
echo "=== 1. ly_analyser_src/common 文件（strings/config 相关） ==="
ls /root/SOC/ly_analyser_src/common/ | grep -E "strings|config|\.h$" | head -20
echo ""
echo "=== 2. 工作区应有 strings.h，服务器对比 ==="
ls -la /root/SOC/ly_analyser_src/common/strings.h 2>/dev/null || echo "strings.h 缺失"
echo ""
echo "=== 3. Makefile INCS 路径 ==="
grep -m3 "INCS" /root/SOC/ly_analyser_src/agent/handlers/Makefile
echo ""
echo "=== 4. 上次编译时间（actl.o 时间戳） ==="
ls -la /root/SOC/ly_analyser_src/agent/handlers/*.o 2>/dev/null | head -5
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