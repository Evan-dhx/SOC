import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Foreground nfcapd test", r"""
echo "=== 前台运行 nfcapd 3 秒（看错误） ==="
cd /data/flow
timeout 3 /Agent/bin/nfcapd -p 9995 -l /data/flow -z -b 0.0.0.0 2>&1
echo "Exit: $?"
echo ""
echo "=== 换参数测试（不带 -z -b） ==="
timeout 3 /Agent/bin/nfcapd -p 9995 -l /data/flow 2>&1
echo "Exit: $?"
echo ""
echo "=== 文件系统检查 ==="
ls -ld /data/flow
df -h /data | tail -1
touch /data/flow/test_write && echo "write OK" && rm /data/flow/test_write
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
