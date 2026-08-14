import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check libprotobuf.so.19 version", r"""
echo "=== libprotobuf.so.19 version ==="
strings /usr/local/lib/libprotobuf.so.19.0.0 2>/dev/null | grep -E "^3\.[0-9]+\.[0-9]+|libprotobuf" | head -5
echo ""
echo "=== Bazel protobuf version header ==="
grep "GOOGLE_PROTOBUF_VERSION" /root/tensorflow/bazel-tensorflow/external/com_google_protobuf/src/google/protobuf/stubs/common.h 2>/dev/null | head -2
echo ""
echo "=== soname ==="
readelf -d /usr/local/lib/libprotobuf.so.19.0.0 2>/dev/null | grep SONAME
echo ""
echo "=== Check if there is a newer protobuf so anywhere ==="
find /root/tensorflow /root/.cache/bazel -name "libprotobuf*.so*" -o -name "libprotobuf*.a" 2>/dev/null | head -10
"""),

    ("Check TF lib protobuf symbols", r"""
echo "=== Does libtensorflow_cc export protobuf symbols? ==="
nm -D /usr/local/lib/libtensorflow_cc.so.2.12.0 2>/dev/null | grep -cE " _ZN6google8protobuf" 
echo "protobuf symbols exported"
echo ""
nm -D /usr/local/lib/libtensorflow_cc.so.2.12.0 2>/dev/null | grep -E "MessageLite|down_cast" | head -5
"""),

    ("Check indexer protobuf symbol refs", r"""
echo "=== indexer protobuf undefined symbols ==="
nm -D /Agent/bin/indexer 2>/dev/null | grep " U _ZN6google8protobuf" | head -10
echo ""
echo "=== indexer protobuf symbol count ==="
nm -D /Agent/bin/indexer 2>/dev/null | grep -c "google8protobuf"
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
