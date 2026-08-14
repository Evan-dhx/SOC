import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find protobuf 3.21.9 library in bazel", r"""
echo "=== Find protobuf lib in bazel-bin ==="
find /root/tensorflow/bazel-bin/external/com_google_protobuf -name "*.so*" -o -name "*.a" 2>/dev/null | head -10
echo ""
echo "=== Find in execroot ==="
find /root/.cache/bazel/_bazel_root/efb88f6336d9c4a18216fb94287b8d97/execroot/org_tensorflow/bazel-out/k8-opt/bin/external/com_google_protobuf -maxdepth 1 -name "*.so*" -o -name "*.a" 2>/dev/null | head -10
"""),

    ("Check protobuf version of existing lib", r"""
echo "=== Check current libprotobuf version ==="
strings /usr/local/lib/libprotobuf.so.19.0.0 2>/dev/null | grep -m1 "libprotobuf"
strings /usr/local/lib/libprotobuf.so.19.0.0 2>/dev/null | grep -m2 "3\.\|GOOGLE_PROTOBUF_VERSION" | head -5
echo ""
echo "=== Check soname ==="
readelf -d /usr/local/lib/libprotobuf.so.19.0.0 2>/dev/null | grep SONAME
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)

client.close()
