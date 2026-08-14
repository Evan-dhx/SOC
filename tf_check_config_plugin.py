import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config 插件检查", r"""
echo "=== 1. /Server/lib 下插件 ==="
ls -la /Server/lib/ 2>/dev/null | head -30
echo ""
echo "=== 2. config.cpp 完整（前 90 行） ==="
sed -n '1,90p' /root/SOC/ly_server_src/server/config.cpp
echo ""
echo "=== 3. lib 目录编译产物 ==="
ls /root/SOC/ly_server_src/lib/*.so 2>/dev/null
echo ""
echo "=== 4. 各插件 create 函数 ==="
grep -rn "createConfigInstance\|extern \"C\"" /root/SOC/ly_server_src/lib/config_event.cpp | head -5
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
