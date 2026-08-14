import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check nfreplay usage", r"""
echo "=== nfreplay help ==="
/Agent/bin/nfreplay -h 2>&1 | head -20
echo ""
echo "=== nfdump help（如何生成回放文件） ==="
/Agent/bin/nfdump -h 2>&1 | head -15
"""),

    ("Loopback replay test", r"""
echo "=== 回放现有小文件测试 ==="
echo "--- 先看文件内容 ---"
/Agent/bin/nfdump -r /data/flow/nfcapd.current 2>&1 | head -10
echo ""
echo "--- 回放到本地 9995 ---"
timeout 15 /Agent/bin/nfreplay -p 9995 -l 127.0.0.1 /data/flow/nfcapd.current 2>&1 | head -10
echo "Replay exit: $?"
echo ""
echo "--- 检查文件是否增长 ---"
ls -la /data/flow/
stat -c "%s bytes %y" /data/flow/nfcapd.current
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
