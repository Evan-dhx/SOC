import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config_pusher 崩溃分析", r"""
echo "=== 1. pusher 输出日志 ==="
cat /tmp/pusher.log 2>/dev/null | head -10
echo ""
echo "=== 2. core 文件 ==="
ls -la /root/core* /core* 2>/dev/null | head -3
echo ""
echo "=== 3. 用 gdb 复现崩溃（strace 或直接跑） ==="
cd /home/Server/bin
timeout 10 ./config_pusher d 2>&1 | head -20
echo "exit=$?"
echo ""
echo "=== 4. config_updater 是否在运行（pusher 需要 POST 到 10081） ==="
ss -tlnp 2>/dev/null | grep 10081
ps aux | grep config_updater | grep -v grep | head -2
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()