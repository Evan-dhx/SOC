import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重编 config_updater + 全部 handlers EXE", r"""
cd /root/SOC/ly_analyser_src/agent/handlers
echo "=== 1. make all（全部 CMD/BIN EXE） ==="
make all > /tmp/all.log 2>&1; echo "exit=$?"
grep -cE "error" /tmp/all.log || echo 0
ls -la config_updater extractor extract_event extract_feature flow_scan extract_pcap output_unqlite extract_event_feature 2>/dev/null | awk '{print $NF, $6, $7, $8}'
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=1800)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()