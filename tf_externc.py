import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("extern C 源头排查", r"""
echo "=== 1. config.h extern C ==="
grep -n "extern \"C\"" /root/SOC/ly_analyser_src/common/config.h 2>/dev/null | head -5
echo ""
echo "=== 2. CMyINI.h extern C ==="
grep -n "extern \"C\"" /root/SOC/ly_analyser_src/common/CMyINI.h 2>/dev/null | head -5
echo ""
echo "=== 3. cached_config.h extern C ==="
grep -n "extern \"C\"" /root/SOC/ly_analyser_src/agent/config/cached_config.h 2>/dev/null | head -5
echo ""
echo "=== 4. log.h extern C ==="
grep -n "extern \"C\"" /root/SOC/ly_analyser_src/common/log.h 2>/dev/null | head -5
echo ""
echo "=== 5. strings.cpp 是否存在旧版本引用（fsd 链接需要） ==="
ls -la /root/SOC/ly_analyser_src/common/strings.cpp 2>/dev/null
echo ""
echo "=== 6. 尝试单独编译 fsd.o 看第一个 extern C 错误位置 ==="
cd /root/SOC/ly_analyser_src/agent/handlers
rm -f fsd.o
make fsd 2>&1 | grep -B3 "extern \"C\" linkage started" | head -10
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()