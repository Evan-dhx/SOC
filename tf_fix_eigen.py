import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Replace Eigen headers with actual content from Bazel cache", r"""
echo "=== Replace Eigen headers ==="

# Remove the wrapper eigen3 directory (it only has stub files)
rm -rf /usr/local/include/tf/third_party/eigen3

# Copy actual Eigen headers from Bazel external cache
cp -r /root/tensorflow/bazel-tensorflow/external/eigen_archive /usr/local/include/tf/third_party/eigen3

echo "Eigen headers copied from Bazel cache"
"""),

    ("Verify Eigen headers", r"""
echo "=== Verify Eigen structure ==="
ls /usr/local/include/tf/third_party/eigen3/unsupported/Eigen/CXX11/Tensor && echo "OK: Tensor header exists"
ls /usr/local/include/tf/third_party/eigen3/unsupported/Eigen/CXX11/src/ | head -5 && echo "OK: src directory exists"
ls /usr/local/include/tf/third_party/eigen3/Eigen/ | head -5 && echo "OK: Eigen core exists"
"""),

    ("Check if wrapper Tensor file is now real", r"""
echo "=== Check Tensor header content ==="
head -5 /usr/local/include/tf/third_party/eigen3/unsupported/Eigen/CXX11/Tensor
"""),

    ("Retry compiling flow_filter.a", r"""
echo "=== Retry compile flow_filter.a ==="
cd /root/SOC/ly_analyser_src/agent/flow
make clean
make flow_filter.a 2>&1 | tail -50
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
    if err:
        print(f"STDERR: {err}")
    
    if "FAIL:" in out:
        print(f"\nStep failed: {label}")
        break

client.close()
print("\nDone")
