import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("编译结果确认", r"""
cd /root/SOC/ly_analyser_src/agent/handlers
echo "=== 1. 二进制时间戳 ==="
ls -la actl fsd config_updater extractor extract_event extract_event_feature extract_feature extract_pcap flow_scan output_unqlite 2>/dev/null | awk '{print $NF, $6, $7, $8}'
echo ""
echo "=== 2. 错误检查 ==="
grep -c "error" /tmp/rebuild_all.log 2>/dev/null || echo 0
tail -2 /tmp/rebuild_all.log
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:500]}")

client.close()