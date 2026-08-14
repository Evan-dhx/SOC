import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Fix indexing Makefile to use new flow_filter.a", r"""
echo "=== Fix indexing Makefile ==="
cd /root/SOC/ly_analyser_src/agent/indexing

# Change flow_filter_full.a to flow_filter.a (new ABI version)
sed -i 's|../flow/flow_filter_full.a|../flow/flow_filter.a|' Makefile

echo "New LIBS:"
grep "^LIBS=" Makefile
"""),

    ("Also update flow Makefile to remove old targets", r"""
echo "=== Check flow Makefile for cleanup ==="
# The old flow_filter_full.a was built manually with old ABI
# We should rename it to avoid confusion
cd /root/SOC/ly_analyser_src/agent/flow
mv flow_filter_full.a flow_filter_full.a.old_abi0 2>/dev/null
echo "Renamed flow_filter_full.a to flow_filter_full.a.old_abi0"
"""),

    ("Rebuild indexer", r"""
echo "=== Rebuild indexer ==="
cd /root/SOC/ly_analyser_src/agent/indexing
make clean
make 2>&1 | tail -50
echo ""
echo "Exit code: $?"
ls -lh indexer 2>/dev/null && echo "OK: indexer generated" || echo "FAIL: indexer not generated"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err and 'warning' not in err.lower():
        print(f"STDERR: {err}")
    
    if "FAIL:" in out:
        print(f"\nStep failed: {label}")
        break

client.close()
print("\nDone")
