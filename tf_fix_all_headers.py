import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check bazel protobuf version", r"""
echo "=== Bazel protobuf version ==="
cat /root/tensorflow/bazel-tensorflow/external/com_google_protobuf/src/google/protobuf/stubs/common.h 2>/dev/null | grep "PROTOBUF_VERSION" | head -3
echo ""
echo "=== System protobuf version ==="
rpm -q protobuf-devel 2>/dev/null || pkg-config --modversion protobuf 2>/dev/null || echo "unknown"
protoc --version 2>/dev/null || echo "protoc not found"
"""),

    ("Copy ALL bazel-generated headers", r"""
echo "=== Copy ALL generated headers ==="
# Remove old partial copy
rm -rf /usr/local/include/tensorflow

# Copy the entire bazel-bin/tensorflow which contains ALL generated .pb.h files
# This includes tensorflow/core/framework/*.pb.h, tensorflow/tsl/protobuf/*.pb.h, etc.
cd /root/tensorflow/bazel-bin
find tensorflow -name "*.pb.h" -type f 2>/dev/null | wc -l
echo "generated .pb.h files found"

# Copy all generated headers preserving directory structure
cd /root/tensorflow/bazel-bin
find tensorflow -name "*.pb.h" -type f -exec install -D {} /usr/local/include/{} \;
echo "OK: All generated headers installed"

# Verify key files
ls /usr/local/include/tensorflow/core/framework/types.pb.h && echo "OK: types.pb.h"
ls /usr/local/include/tensorflow/tsl/protobuf/error_codes.pb.h 2>/dev/null && echo "OK: error_codes.pb.h" || echo "Checking tsl path..."
find /usr/local/include/tensorflow/tsl -name "*.pb.h" 2>/dev/null | head -5
"""),

    ("Also copy bazel protobuf headers to override system", r"""
echo "=== Install Bazel protobuf headers ==="
# We need the protobuf headers from Bazel to match the generated .pb.h files
# Copy them to override the system protobuf
cp -r /root/tensorflow/bazel-tensorflow/external/com_google_protobuf/src/google /usr/local/include/
echo "OK: Bazel protobuf headers installed"
ls /usr/local/include/google/protobuf/stubs/common.h && echo "OK: protobuf stubs"
"""),

    ("Update Makefile - remove conflicting paths", r"""
echo "=== Update Makefile ==="
cd /root/SOC/ly_analyser_src/agent/flow

# The include path needs:
# - /usr/local/include for tensorflow/core/framework/*.pb.h (generated) and google/protobuf (bazel version)
# - /usr/local/include/tf for TF source headers
# - /usr/local/include/tf/third_party/eigen3 for Eigen
# - /usr/local/include/tf/nsync_public for nsync
sed -i 's|^INCS=.*|INCS=-I. -I/usr/include -I/usr/local/include -I/usr/local/include/tf -I/usr/local/include/tf/tensorflow -I/usr/local/include/tf/third_party -I/usr/local/include/tf/third_party/eigen3 -I/usr/local/include/tf/tensorflow/core/protobuf -I/usr/local/include/tf/nsync_public|' Makefile

echo "New INCS:"
grep "^INCS=" Makefile
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
