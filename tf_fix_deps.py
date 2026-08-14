import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Install absl headers", r"""
echo "=== Install Abseil headers ==="
cp -r /root/tensorflow/bazel-tensorflow/external/com_google_absl/absl /usr/local/include/tf/
echo "OK: absl headers installed"
ls /usr/local/include/tf/absl/strings/string_view.h && echo "OK: string_view.h exists"
"""),

    ("Install nsync headers", r"""
echo "=== Install nsync headers ==="
cp -r /root/tensorflow/bazel-tensorflow/external/nsync/public /usr/local/include/tf/nsync_public
echo "OK: nsync headers installed"
ls /usr/local/include/tf/nsync_public/nsync.h 2>/dev/null && echo "OK: nsync.h exists" || echo "nsync.h not found, checking structure..."
ls /usr/local/include/tf/nsync_public/ | head -5
"""),

    ("Install protobuf headers", r"""
echo "=== Install protobuf headers ==="
# protobuf headers are needed for tensorflow includes
mkdir -p /usr/local/include/tf/protobuf
cp -r /root/tensorflow/bazel-tensorflow/external/com_google_protobuf/src/google /usr/local/include/tf/protobuf/
echo "OK: protobuf headers installed"
ls /usr/local/include/tf/protobuf/google/protobuf/ | head -5
"""),

    ("Update flow Makefile with new include paths", r"""
echo "=== Update flow Makefile ==="
cd /root/SOC/ly_analyser_src/agent/flow

# Add absl, nsync, protobuf include paths
sed -i 's|^INCS=.*|INCS=-I. -I/usr/include -I/usr/local/include -I/usr/local/include/tf -I/usr/local/include/tf/tensorflow -I/usr/local/include/tf/third_party -I/usr/local/include/tf/tensorflow/core/protobuf -I/usr/local/include/tf -I/usr/local/include/tf/nsync_public|' Makefile

echo "New INCS:"
grep "^INCS=" Makefile
"""),

    ("Retry compile flow_filter.a", r"""
echo "=== Retry compile flow_filter.a ==="
cd /root/SOC/ly_analyser_src/agent/flow
make clean
make flow_filter.a 2>&1 | tail -60
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
