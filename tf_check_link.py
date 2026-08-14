import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check TF libraries", r"""
echo "=== TF libraries ==="
ls -lh /usr/local/lib/libtensorflow* 2>/dev/null
echo ""
echo "=== ldconfig -p | grep tensorflow ==="
ldconfig -p | grep tensorflow
echo ""
echo "=== Check /usr/lib64 links ==="
ls -lh /usr/lib64/libtensorflow* 2>/dev/null
"""),

    ("Check protobuf library", r"""
echo "=== protobuf library ==="
ls -lh /usr/lib64/libprotobuf* 2>/dev/null
ls -lh /usr/lib/libprotobuf* 2>/dev/null
ls -lh /usr/local/lib/libprotobuf* 2>/dev/null
echo ""
ldconfig -p | grep protobuf
"""),

    ("Check boost regex", r"""
echo "=== boost regex ==="
ls -lh /usr/lib64/libboost_regex* 2>/dev/null
ls -lh /usr/lib/libboost_regex* 2>/dev/null
echo ""
ldconfig -p | grep boost_regex
"""),

    ("Check what symbols exist in libtensorflow_cc", r"""
echo "=== Check TF symbols in lib ==="
nm -D /usr/local/lib/libtensorflow_cc.so.2.12.0 2>/dev/null | grep -E "NewSession|ReadBinaryProto" | head -5
echo ""
echo "=== Check Env::Default ==="
nm -D /usr/local/lib/libtensorflow_cc.so.2.12.0 2>/dev/null | grep "Env" | head -5
"""),

    ("Check linker uses correct libs", r"""
echo "=== Test link with verbose ==="
cd /root/SOC/ly_analyser_src/agent/indexing
echo 'int main(){}' > /tmp/test_link.cpp
g++ /tmp/test_link.cpp -o /tmp/test_link -ltensorflow_cc -ltensorflow_framework -lprotobuf -lboost_regex -L/usr/local/lib -L/usr/lib64 2>&1 | head -10
echo "Exit: $?"
echo ""
echo "=== Check search paths ==="
g++ -print-search-dirs | grep libraries
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:500]}")

client.close()
