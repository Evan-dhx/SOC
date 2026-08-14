import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("前台验证脚本可运行", r"""
echo "=== 1. 脚本语法检查 ==="
python3 -m py_compile /tmp/sim_ti_server.py && echo "语法 OK" || echo "语法错误"
echo ""
echo "=== 2. 前台运行 3 秒（看输出） ==="
timeout 3 python3 /tmp/sim_ti_server.py 2>&1 | head -5
echo "退出码: $?"
echo ""
echo "=== 3. 文件内容检查 ==="
head -5 /tmp/sim_ti_server.py
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