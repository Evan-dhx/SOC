import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check ALL fill/0 patterns in arena_impl.h", r"""
echo "=== Check for any remaining fill with 0 ==="
grep -n "fill" /usr/local/include/google/protobuf/arena_impl.h
echo ""
echo "=== Check ALL fill calls in protobuf headers ==="
grep -rn "std::fill" /usr/local/include/google/protobuf/*.h | grep -v backup | head -10
"""),

    ("Rebuild data module with -fpermissive", r"""
echo "=== Rebuild data module with -fpermissive ==="
cd /root/SOC/ly_analyser_src/agent/data

# Remove old objects
rm -f unqlite_db.o dbctx.o tsdb.o unqlite.o web_cache.o dbctx.pb.o data.a

# Compile all with -fpermissive
for f in unqlite_db.cpp dbctx.cpp tsdb.cpp unqlite.cpp web_cache.cpp dbctx.pb.cc; do
    echo "Compiling $f..."
    g++ -c -Wall -fPIC -g -std=c++17 -fpermissive -DAGENT -O2 -I. -I../../common -I/usr/include -I/usr/local/include -o ${f%.cpp}.o $f 2>&1 | grep -E "error:" | head -5
done

# Check all objects exist
ls -la *.o 2>/dev/null | head -10
echo ""

# Package
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
