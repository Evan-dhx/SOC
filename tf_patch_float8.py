import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Patch float8.h - add missing ConvertImpl specializations", r"""
echo "=== Patch float8.h ==="

F8=/usr/local/include/tf/tensorflow/tsl/platform/float8.h
cp $F8 ${F8}.backup

# Find the line with the last ConvertImpl specialization (before the closing of the namespace)
# We need to add missing specializations before the float8_base class methods that use them

# The error is at lines 796 and 802 which call ConvertImpl::run()
# The missing specializations are for float8_e4m3fn conversions

# Add missing ConvertImpl specializations after the existing ones (before line 794 area)
# We'll insert them right before the "template <class Derived>" line of float8_base

cat >> /tmp/float8_patch.py << 'PYEOF'
import re

with open('/usr/local/include/tf/tensorflow/tsl/platform/float8.h', 'r') as f:
    content = f.read()

# Add missing specializations before the float8_base class definition's ConvertFrom/ConvertTo
# Find the line "template <class Derived>" that defines float8_base
# and insert our specializations before it

patch = '''
// === PATCHED: Additional ConvertImpl specializations for GCC 11 compatibility ===
// float8_e4m3fn <-> float
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<float8_e4m3fn, float, kSaturate, kTruncate> {
  static float run(float8_e4m3fn from) { return static_cast<float>(from); }
};
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<float, float8_e4m3fn, kSaturate, kTruncate> {
  static float8_e4m3fn run(float from) { return static_cast<float8_e4m3fn>(from); }
};

// float8_e4m3fn <-> double
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<float8_e4m3fn, double, kSaturate, kTruncate> {
  static double run(float8_e4m3fn from) { return static_cast<double>(from); }
};
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<double, float8_e4m3fn, kSaturate, kTruncate> {
  static float8_e4m3fn run(double from) { return static_cast<float8_e4m3fn>(from); }
};

// float8_e4m3fn <-> Eigen::half
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<float8_e4m3fn, Eigen::half, kSaturate, kTruncate> {
  static Eigen::half run(float8_e4m3fn from) { return Eigen::half(static_cast<float>(from)); }
};
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<Eigen::half, float8_e4m3fn, kSaturate, kTruncate> {
  static float8_e4m3fn run(Eigen::half from) { return static_cast<float8_e4m3fn>(static_cast<float>(from)); }
};

// float8_e4m3fn <-> Eigen::bfloat16
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<float8_e4m3fn, Eigen::bfloat16, kSaturate, kTruncate> {
  static Eigen::bfloat16 run(float8_e4m3fn from) { return Eigen::bfloat16(static_cast<float>(from)); }
};
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<Eigen::bfloat16, float8_e4m3fn, kSaturate, kTruncate> {
  static float8_e4m3fn run(Eigen::bfloat16 from) { return static_cast<float8_e4m3fn>(static_cast<float>(from)); }
};

// float8_e5m2 <-> float
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<float8_e5m2, float, kSaturate, kTruncate> {
  static float run(float8_e5m2 from) { return static_cast<float>(from); }
};
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<float, float8_e5m2, kSaturate, kTruncate> {
  static float8_e5m2 run(float from) { return static_cast<float8_e5m2>(from); }
};

// float8_e5m2 <-> double
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<float8_e5m2, double, kSaturate, kTruncate> {
  static double run(float8_e5m2 from) { return static_cast<double>(from); }
};
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<double, float8_e5m2, kSaturate, kTruncate> {
  static float8_e5m2 run(double from) { return static_cast<float8_e5m2>(from); }
};

// float8_e5m2 <-> Eigen::bfloat16
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<float8_e5m2, Eigen::bfloat16, kSaturate, kTruncate> {
  static Eigen::bfloat16 run(float8_e5m2 from) { return Eigen::bfloat16(static_cast<float>(from)); }
};
template <bool kSaturate, bool kTruncate>
struct ConvertImpl<Eigen::bfloat16, float8_e5m2, kSaturate, kTruncate> {
  static float8_e5m2 run(Eigen::bfloat16 from) { return static_cast<float8_e5m2>(static_cast<float>(from)); }
};
// === END PATCH ===

'''

# Insert before the float8_base class's ConvertFrom method
# Find "static Derived ConvertFrom" and insert before its containing class
marker = '  static Derived ConvertFrom(const From& from) {'
if marker in content:
    # Find the line with "template <bool kSaturate" before the first ConvertImpl that's a generic catch-all
    # Actually, let's insert right before the float8_base class methods
    # The float8_base class has ConvertFrom at around line 796
    # Let's insert our patch before "template <class Derived>\nclass float8_base"
    
    # Find the class float8_base definition
    class_marker = 'class float8_base {'
    if class_marker in content:
        content = content.replace(class_marker, patch + class_marker)
        print("Patch inserted before float8_base class")
    else:
        # Try alternative marker
        class_marker2 = 'class float8_base'
        if class_marker2 in content:
            content = content.replace(class_marker2, patch + class_marker2, 1)
            print("Patch inserted before float8_base class (alt marker)")
        else:
            print("Could not find insertion point!")
else:
    print("Could not find ConvertFrom marker!")

with open('/usr/local/include/tf/tensorflow/tsl/platform/float8.h', 'w') as f:
    f.write(content)

print("float8.h patched successfully")
PYEOF

python3 /tmp/float8_patch.py
"""),

    ("Verify patch", r"""
echo "=== Verify float8.h patch ==="
grep -c "PATCHED" /usr/local/include/tf/tensorflow/tsl/platform/float8.h
echo "patch markers found"
grep "ConvertImpl<float8_e4m3fn, float" /usr/local/include/tf/tensorflow/tsl/platform/float8.h | head -3
"""),

    ("Retry compile", r"""
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
