import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find generated protobuf headers", r"""
echo "=== Find types.pb.h ==="
find /root/tensorflow/bazel-bin/tensorflow/core/framework -name "types.pb.h" 2>/dev/null
find /root/tensorflow/bazel-out -name "types.pb.h" -path "*/tensorflow/*" 2>/dev/null | head -5
"""),

    ("Check bazel-bin structure", r"""
echo "=== bazel-bin tensorflow/core/framework ==="
ls /root/tensorflow/bazel-bin/tensorflow/core/framework/*.pb.h 2>/dev/null | head -10
echo ""
echo "=== bazel-bin tensorflow/core/protobuf ==="
ls /root/tensorflow/bazel-bin/tensorflow/core/protobuf/*.pb.h 2>/dev/null | head -5
"""),

    ("Copy generated headers to include dir", r"""
echo "=== Copy generated protobuf headers ==="
# Copy bazel-generated protobuf headers to the TF include directory
# These need to be at tensorflow/core/framework/types.pb.h relative to include path
mkdir -p /usr/local/include/tf_gen
cp -r /root/tensorflow/bazel-bin/tensorflow /usr/local/include/tf_gen/
echo "OK: Generated headers copied"
ls /usr/local/include/tf_gen/tensorflow/core/framework/types.pb.h 2>/dev/null && echo "OK: types.pb.h exists" || echo "types.pb.h not found"
"""),

    ("Update Makefile with generated headers path", r"""
echo "=== Update Makefile ==="
cd /root/SOC/ly_analyser_src/agent/flow

# Add generated headers path
sed -i 's|^INCS=.*|INCS=-I. -I/usr/include -I/usr/local/include -I/usr/local/include/tf -I/usr/local/include/tf/tensorflow -I/usr/local/include/tf/third_party -I/usr/local/include/tf/third_party/eigen3 -I/usr/local/include/tf/tensorflow/core/protobuf -I/usr/local/include/tf/nsync_public -I/usr/local/include|' Makefile

# Actually, we need -I/usr/local/include so that tf_gen/tensorflow/... resolves
# But the include is "tensorflow/core/framework/types.pb.h"
# So we need the file at <some_include_path>/tensorflow/core/framework/types.pb.h
# Let's symlink it instead
ln -sf /usr/local/include/tf_gen/tensorflow /usr/local/include/tensorflow_gen 2>/dev/null

# Better approach: put generated headers where they can be found as tensorflow/core/framework/types.pb.h
mkdir -p /usr/local/include/tensorflow/core/framework
cp /root/tensorflow/bazel-bin/tensorflow/core/framework/*.pb.h /usr/local/include/tensorflow/core/framework/ 2>/dev/null
mkdir -p /usr/local/include/tensorflow/core/protobuf
cp /root/tensorflow/bazel-bin/tensorflow/core/protobuf/*.pb.h /usr/local/include/tensorflow/core/protobuf/ 2>/dev/null

echo "New INCS:"
grep "^INCS=" Makefile
echo ""
echo "Verify:"
ls /usr/local/include/tensorflow/core/framework/types.pb.h 2>/dev/null && echo "OK: types.pb.h" || echo "FAIL"
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
