import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check db contents", r"""
echo "=== 1. db/20260813 内容 ==="
ls -la /Agent/data/db/20260813/
echo ""
echo "=== 2. 事件 db ==="
find /Agent/data -name "event*" -o -name "*.udb" 2>/dev/null | head -10
echo ""
echo "=== 3. /Agent/flow 目录状态 ==="
ls -la /Agent/flow/ 2>/dev/null
ls -la /Agent/flow/1/ 2>/dev/null | head -10
echo ""
echo "=== 4. config 中设备配置 ==="
mysql -e "SELECT id, moip, devid FROM server.t_mo;" 2>/dev/null | head -5
mysql -e "SHOW TABLES FROM server;" 2>/dev/null | grep -iE "agent|device|config" | head -10
"""),

    ("Migrate nfcapd to /Agent/flow/1", r"""
echo "=== 5. 迁移 nfcapd 到 /Agent/flow/1 ==="
pkill -x nfcapd 2>/dev/null
sleep 1
mkdir -p /Agent/flow/1
echo "--- 复制历史数据 ---"
cp -v /data/flow/nfcapd.* /Agent/flow/1/ 2>/dev/null | tail -3
echo ""
echo "--- 启动 nfcapd（正确目录） ---"
/Agent/bin/nfcapd -D -p 9995 -l /Agent/flow/1 -z -b 0.0.0.0
sleep 2
ss -tlnup | grep 9995
ps aux | grep "[n]fcapd" | grep -v bash | head -2
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
