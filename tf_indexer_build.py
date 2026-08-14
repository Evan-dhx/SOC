import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重编 indexer + 部署全部", r"""
echo "=== 1. 重编 indexer ==="
cd /root/SOC/ly_analyser_src/agent/indexing
rm -f indexer *.o 2>/dev/null
make > /tmp/indexer.log 2>&1; echo "exit=$?"
ls -la indexer 2>/dev/null | awk '{print $NF, $6, $7, $8}'
grep -c "error" /tmp/indexer.log 2>/dev/null || echo 0
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=1800)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1200]}")

client.close()