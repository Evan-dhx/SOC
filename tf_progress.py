import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重编进度检查", r"""
echo "=== 1. 编译进度 ==="
tail -5 /tmp/rebuild_all.log 2>/dev/null
echo ""
echo "=== 2. 是否还在编译 ==="
pgrep -f "make all" >/dev/null && echo "编译中..." || echo "编译结束"
echo ""
echo "=== 3. 二进制时间戳 ==="
ls -la actl fsd config_updater extractor extract_event extract_event_feature extract_feature extract_pcap flow_scan output_unqlite 2>/dev/null | awk '{print $NF, $6, $7, $8}'
echo ""
echo "=== 4. 错误检查 ==="
grep -c "error" /tmp/rebuild_all.log 2>/dev/null || echo 0
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