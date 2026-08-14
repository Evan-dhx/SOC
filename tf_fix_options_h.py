import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find all generated options.h", r"""
echo "=== Find generated options.h in bazel-bin ==="
find /root/tensorflow/bazel-bin -name "options.h" -path "*/registration/*" 2>/dev/null
echo ""
echo "=== Find in bazel-out ==="
find /root/tensorflow/bazel-out -name "options.h" -path "*/registration/*" 2>/dev/null | head -5
echo ""
echo "=== Find ALL generated .h in bazel-bin tensorflow/core/framework ==="
find /root/tensorflow/bazel-bin/tensorflow/core/framework -name "*.h" 2>/dev/null | head -20
"""),

    ("Copy ALL bazel-generated headers comprehensively", r"""
echo "=== Copy ALL generated headers from bazel-bin ==="
cd /root/tensorflow/bazel-bin

# Count all generated headers
TOTAL=$(find tensorflow -name "*.h" -type f 2>/dev/null | wc -l)
echo "Total generated headers in bazel-bin: $TOTAL"

# Copy ALL of them preserving directory structure
find tensorflow -name "*.h" -type f -exec install -D {} /usr/local/include/{} \;

echo "OK: All generated headers installed"

# Verify
ls /usr/local/include/tensorflow/core/framework/registration/options.h 2>/dev/null && echo "OK: options.h exists" || echo "FAIL: options.h still missing"
"""),

    ("Also copy from bazel execroot if needed", r"""
echo "=== Check execroot for additional generated headers ==="
EXECROOT=/root/.cache/bazel/_bazel_root/efb88f6336d9c4a18216fb94287b8d97/execroot/org_tensorflow/bazel-out/k8-opt/bin
find $EXECROOT/tensorflow/core/framework/registration -name "*.h" 2>/dev/null
echo ""
# Copy if found
if [ -f "$EXECROOT/tensorflow/core/framework/registration/options.h" ]; then
    cp $EXECROOT/tensorflow/core/framework/registration/options.h /usr/local/include/tensorflow/core/framework/registration/
    echo "OK: options.h copied from execroot"
fi

# Final verify
ls /usr/local/include/tensorflow/core/framework/registration/options.h 2>/dev/null && echo "OK: options.h confirmed" || echo "Still missing"
"""),

    ("Retry compile", r"""
echo "=== Retry compile flow_filter.a ==="
cd /root/SOC/ly_analyser_src/agent/flow
make clean
make flow_filter.a 2>&1 | tail -40
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
