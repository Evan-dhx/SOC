import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Verify new protoc", r"""
echo "=== Verify new protoc ==="
/root/tensorflow/bazel-bin/external/com_google_protobuf/protoc --version
"""),

    ("Backup old pb files and regenerate with protoc 3.21", r"""
echo "=== Regenerate all .pb.h and .pb.cc files ==="

PROTOC=/root/tensorflow/bazel-bin/external/com_google_protobuf/protoc
PROTO_INC=/usr/local/include

# Backup old generated files
mkdir -p /root/SOC/ly_analyser_src/common/pb_backup
cp /root/SOC/ly_analyser_src/common/*.pb.h /root/SOC/ly_analyser_src/common/pb_backup/ 2>/dev/null
cp /root/SOC/ly_analyser_src/common/*.pb.cc /root/SOC/ly_analyser_src/common/pb_backup/ 2>/dev/null

# Regenerate common proto files
cd /root/SOC/ly_analyser_src/common
for f in *.proto; do
    echo "Regenerating $f..."
    $PROTOC --cpp_out=. --proto_path=. "$f" 2>&1
done

echo ""
echo "=== Regenerate agent proto files ==="
cd /root/SOC/ly_analyser_src/agent/data
for f in *.proto; do
    echo "Regenerating $f..."
    $PROTOC --cpp_out=. --proto_path=. --proto_path=../../common "$f" 2>&1
done

cd /root/SOC/ly_analyser_src/agent/handlers
for f in *.proto; do
    echo "Regenerating $f..."
    $PROTOC --cpp_out=. --proto_path=. --proto_path=../../common "$f" 2>&1
done

# Also regenerate baseline
cd /root/SOC/ly_analyser_src/common/baseline
for f in *.proto; do
    echo "Regenerating $f..."
    $PROTOC --cpp_out=. --proto_path=. --proto_path=.. "$f" 2>&1
done

echo ""
echo "OK: All proto files regenerated"
"""),

    ("Verify regenerated files", r"""
echo "=== Verify regenerated files ==="
head -5 /root/SOC/ly_analyser_src/common/event.pb.h | grep "protobuf version"
echo ""
ls -la /root/SOC/ly_analyser_src/common/*.pb.h | wc -l
echo "pb.h files in common"
ls -la /root/SOC/ly_analyser_src/common/*.pb.cc | wc -l
echo "pb.cc files in common"
"""),

    ("Retry compile flow_filter.a", r"""
echo "=== Retry compile flow_filter.a ==="
cd /root/SOC/ly_analyser_src/agent/flow
make clean
make flow_filter.a 2>&1 | tail -80
echo ""
echo "Exit code: $?"
ls -lh flow_filter.a 2>/dev/null && echo "OK: flow_filter.a generated" || echo "FAIL: flow_filter.a not generated"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
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
