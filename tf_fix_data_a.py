import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Fix dbctx.pb.o name and repackage data.a", r"""
echo "=== Fix data.a ==="
cd /root/SOC/ly_analyser_src/agent/data

# Rename wrong object file name
mv dbctx.pb.cc.o dbctx.pb.o 2>/dev/null

# Repackage
ar rcs data.a unqlite_db.o dbctx.o tsdb.o unqlite.o web_cache.o dbctx.pb.o
echo "OK: data.a rebuilt:"
ls -lh data.a
"""),

    ("Rebuild indexer", r"""
echo "=== Rebuild indexer ==="
cd /root/SOC/ly_analyser_src/agent/indexing
make clean
make 2>&1 | tail -30
echo ""
echo "Exit code: $?"
ls -lh indexer 2>/dev/null && echo "OK: indexer generated" || echo "FAIL: indexer not generated"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err and 'warning' not in err.lower():
        print(f"STDERR: {err[:2000]}")
    
    if "FAIL:" in out:
        print(f"\nStep failed: {label}")
        break

client.close()
print("\nDone")
