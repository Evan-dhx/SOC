import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("protoc 修复 + tsensor 启动来源", r"""
echo "=== 1. protoc 库冲突排查 ==="
ldd /usr/local/bin/protoc 2>/dev/null | grep proto
ls -la /usr/local/lib/libproto* 2>/dev/null
find / -name "libprotobuf.so*" -not -path "*/proc/*" 2>/dev/null | head -8
echo ""
echo "=== 2. 尝试不同环境跑 protoc ==="
LD_LIBRARY_PATH=/usr/local/lib protoc --version 2>&1 | head -2
echo ""
echo "=== 3. tsensor 启动来源 ==="
systemctl list-units --all 2>/dev/null | grep -iE "tsensor|lyprobe|probe"
cat /etc/systemd/system/tsensor.service 2>/dev/null || cat /etc/systemd/system/lyprobe.service 2>/dev/null
echo ""
echo "=== 4. actl 部署位置 ==="
find / -name "actl" -type f -not -path "*/proc/*" 2>/dev/null | head -3
find / -name "config_agent.so" -o -name "config_agent*" -not -path "*/proc/*" 2>/dev/null | grep -v SOC | head -3
echo ""
echo "=== 5. fsd 启动方式 ==="
ps aux | grep -E "fsd|config_updater" | grep -v grep
systemctl list-units --all 2>/dev/null | grep -iE "fsd|agent"
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