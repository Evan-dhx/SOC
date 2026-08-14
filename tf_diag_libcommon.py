import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("libcommon 对比 + mo 源码", r"""
echo "=== 1. libcommon.so 版本对比 ==="
md5sum /lib64/libcommon.so /Agent/lib/libcommon.so 2>/dev/null
ls -la /lib64/libcommon.so /Agent/lib/libcommon.so 2>/dev/null
echo ""
echo "=== 2. /Agent/lib/libcommon.so 是否导出 CtlReq 默认 id ==="
nm -D /Agent/lib/libcommon.so 2>/dev/null | grep "give_permission" | head -3
nm -D /lib64/libcommon.so 2>/dev/null | grep "give_permission" | head -3
echo ""
echo "=== 3. mo.cpp 460-510 行 ==="
sed -n '460,510p' /root/SOC/ly_server_src/server/mo.cpp
echo ""
echo "=== 4. mo.cpp 中 process/main ==="
grep -n "static void process\|int main\|action\|GetDevs" /root/SOC/ly_server_src/server/mo.cpp | head -15
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
