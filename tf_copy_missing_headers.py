import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check and copy missing TF headers", r"""
echo "=== Check missing registration headers ==="
ls /root/tensorflow/tensorflow/core/framework/registration/ 2>/dev/null
echo ""
# Check if it was missed during copy
ls /usr/local/include/tf/tensorflow/core/framework/registration/ 2>/dev/null || echo "registration dir missing in installed headers"

# Re-copy the entire tensorflow source tree to ensure completeness
echo "=== Re-copy TF source headers ==="
cp -rn /root/tensorflow/tensorflow/core/framework/registration /usr/local/include/tf/tensorflow/core/framework/ 2>/dev/null
echo "OK: registration headers copied"
ls /usr/local/include/tf/tensorflow/core/framework/registration/ 2>/dev/null

# Also check for any other missing directories by doing a fresh full copy
echo ""
echo "=== Ensure all TF headers are present ==="
# Use rsync-like approach: copy only missing files
cd /root/tensorflow
find tensorflow -name "*.h" -type f | while read f; do
    if [ ! -f "/usr/local/include/tf/$f" ]; then
        mkdir -p "/usr/local/include/tf/$(dirname $f)"
        cp "$f" "/usr/local/include/tf/$f"
    fi
done
echo "OK: All missing TF headers copied"
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
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
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
