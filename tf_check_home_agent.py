import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check /home/Agent old deployment", r"""
echo "=== 1. /home/Agent 结构 ==="
ls -la /home/Agent/ 2>/dev/null
echo ""
echo "=== 2. /home/Agent/bin ==="
ls /home/Agent/bin/ 2>/dev/null | head -15
echo ""
echo "=== 3. /home/Agent/cmd ==="
ls /home/Agent/cmd/ 2>/dev/null | head -15
echo ""
echo "=== 4. 10081 相关 systemd 服务 ==="
grep -rn "10081" /etc/systemd/system/ 2>/dev/null | head -5
echo ""
echo "=== 5. 所有 systemd 服务列表 ==="
systemctl list-unit-files --type=service 2>/dev/null | grep -iE "agent|http|apache|config|ly" | head -10
echo ""
echo "=== 6. httpd 其他实例 ==="
ps aux | grep "[h]ttpd" | awk '{print $11, $12, $13}' | head -5
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
