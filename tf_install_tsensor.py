import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Build tsensor binary only", r"""
echo "=== 1. 构建 lyprobe（tsensor）==="
cd /root/tsensor
make lyprobe 2>&1 | tail -8
echo "Make lyprobe exit: $?"
echo ""
echo "=== 2. 检查产物 ==="
ls -la lyprobe .libs/lyprobe 2>/dev/null
"""),

    ("Install tsensor and restart", r"""
echo "=== 3. 安装新 tsensor ==="
cd /root/tsensor
cp /usr/local/bin/tsensor /usr/local/bin/tsensor.bak_old_114
cp .libs/lyprobe /usr/local/bin/tsensor 2>/dev/null || cp lyprobe /usr/local/bin/tsensor
chmod +x /usr/local/bin/tsensor
ls -la /usr/local/bin/tsensor
echo ""
echo "=== 4. 重启服务 ==="
systemctl restart tsensor
sleep 5
systemctl status tsensor 2>&1 | head -6
echo ""
echo "=== 5. 等待 30 秒确认稳定 ==="
sleep 30
systemctl is-active tsensor
ps aux | grep "[t]sensor" | grep -v bash | head -1 | cut -c1-80
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
