import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find mo_req source", r"""
echo "=== 1. stAddWhere 定义位置 ==="
grep -rn "stAddWhere" /root/SOC/ly_analyser_src/ /root/SOC/ly_server_src/ 2>/dev/null | grep -v "\.o:" | grep -v Binary | head -5
echo ""
echo "=== 2. mo_req 相关文件 ==="
find /root/SOC -name "mo_req*" -type f 2>/dev/null | head -10
echo ""
echo "=== 3. libcommon 中是否有 mo 符号 ==="
nm -D /lib64/libcommon.so 2>/dev/null | grep -iE "stAddWhere|ParseMoReq" | head -5
echo ""
echo "=== 4. 旧 mo 二进制链接了什么 ==="
ldd /Server/www/d/mo 2>/dev/null | head -10
nm -D /Server/www/d/mo 2>/dev/null | grep "stAddWhere" | head -3
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
