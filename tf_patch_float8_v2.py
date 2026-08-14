import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Patch float8.h with correct insertion", r"""
echo "=== Patch float8.h ==="

cat > /tmp/patch_float8.py << 'PYEOF'
filepath = '/usr/local/include/tf/tensorflow/tsl/platform/float8.h'

with open(filepath, 'r') as f:
    lines = f.readlines()

# Find the last ConvertImpl specialization line (around line 789)
# Look for the closing brace of the last ConvertImpl before float8_base methods
insert_after = None
for i, line in enumerate(lines):
    # Find "struct ConvertImpl<float8_e5m2, Eigen::half, kSaturate, kTruncate>"
    if 'ConvertImpl<float8_e5m2, Eigen::half, kSaturate' in line:
        # Find the closing brace of this struct (next line with just "};")
        for j in range(i+1, min(i+10, len(lines))):
            if lines[j].strip() == '};':
                insert_after = j
                break
        break

if insert_after is None:
    # Fallback: find the last ConvertImpl closing brace before line 800
    for i in range(790, 700, -1):
        if lines[i].strip() == '};' and 'ConvertImpl' in ''.join(lines[max(0,i-10):i]):
            insert_after = i
            break

if insert_after is None:
    print("ERROR: Could not find insertion point!")
    exit(1)

print(f"Inserting after line {insert_after + 1}: {lines[insert_after].strip()}")

patch_lines = [
    '\n',
    '// === PATCH: Additional ConvertImpl specializations for GCC 11 ===\n',
    '\n',
    '// float8_e4m3fn <-> float\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<float8_e4m3fn, float, kSaturate, kTruncate> {\n',
    '  static float run(float8_e4m3fn from) { return from.to_float(); }\n',
    '};\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<float, float8_e4m3fn, kSaturate, kTruncate> {\n',
    '  static float8_e4m3fn run(float from) { return float8_e4m3fn(from); }\n',
    '};\n',
    '\n',
    '// float8_e4m3fn <-> double\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<float8_e4m3fn, double, kSaturate, kTruncate> {\n',
    '  static double run(float8_e4m3fn from) { return static_cast<double>(from.to_float()); }\n',
    '};\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<double, float8_e4m3fn, kSaturate, kTruncate> {\n',
    '  static float8_e4m3fn run(double from) { return float8_e4m3fn(static_cast<float>(from)); }\n',
    '};\n',
    '\n',
    '// float8_e4m3fn <-> Eigen::half\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<float8_e4m3fn, Eigen::half, kSaturate, kTruncate> {\n',
    '  static Eigen::half run(float8_e4m3fn from) { return Eigen::half(from.to_float()); }\n',
    '};\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<Eigen::half, float8_e4m3fn, kSaturate, kTruncate> {\n',
    '  static float8_e4m3fn run(Eigen::half from) { return float8_e4m3fn(static_cast<float>(from)); }\n',
    '};\n',
    '\n',
    '// float8_e4m3fn <-> Eigen::bfloat16\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<float8_e4m3fn, Eigen::bfloat16, kSaturate, kTruncate> {\n',
    '  static Eigen::bfloat16 run(float8_e4m3fn from) { return Eigen::bfloat16(from.to_float()); }\n',
    '};\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<Eigen::bfloat16, float8_e4m3fn, kSaturate, kTruncate> {\n',
    '  static float8_e4m3fn run(Eigen::bfloat16 from) { return float8_e4m3fn(static_cast<float>(from)); }\n',
    '};\n',
    '\n',
    '// float8_e5m2 <-> float\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<float8_e5m2, float, kSaturate, kTruncate> {\n',
    '  static float run(float8_e5m2 from) { return from.to_float(); }\n',
    '};\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<float, float8_e5m2, kSaturate, kTruncate> {\n',
    '  static float8_e5m2 run(float from) { return float8_e5m2(from); }\n',
    '};\n',
    '\n',
    '// float8_e5m2 <-> double\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<float8_e5m2, double, kSaturate, kTruncate> {\n',
    '  static double run(float8_e5m2 from) { return static_cast<double>(from.to_float()); }\n',
    '};\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<double, float8_e5m2, kSaturate, kTruncate> {\n',
    '  static float8_e5m2 run(double from) { return float8_e5m2(static_cast<float>(from)); }\n',
    '};\n',
    '\n',
    '// float8_e5m2 <-> Eigen::bfloat16\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<float8_e5m2, Eigen::bfloat16, kSaturate, kTruncate> {\n',
    '  static Eigen::bfloat16 run(float8_e5m2 from) { return Eigen::bfloat16(from.to_float()); }\n',
    '};\n',
    'template <bool kSaturate, bool kTruncate>\n',
    'struct ConvertImpl<Eigen::bfloat16, float8_e5m2, kSaturate, kTruncate> {\n',
    '  static float8_e5m2 run(Eigen::bfloat16 from) { return float8_e5m2(static_cast<float>(from)); }\n',
    '};\n',
    '\n',
    '// === END PATCH ===\n',
]

# Insert the patch
new_lines = lines[:insert_after+1] + patch_lines + lines[insert_after+1:]

with open(filepath, 'w') as f:
    f.writelines(new_lines)

print(f"Patch applied: {len(patch_lines)} lines inserted after line {insert_after + 1}")
PYEOF

python3 /tmp/patch_float8.py
"""),

    ("Verify patch", r"""
echo "=== Verify ==="
grep -c "PATCH" /usr/local/include/tf/tensorflow/tsl/platform/float8.h
echo "PATCH markers found"
grep "ConvertImpl<float8_e4m3fn, float" /usr/local/include/tf/tensorflow/tsl/platform/float8.h | head -3
"""),

    ("Retry compile", r"""
echo "=== Retry compile ==="
cd /root/SOC/ly_analyser_src/agent/flow
make clean
make flow_filter.a 2>&1 | tail -40
echo ""
ls -lh flow_filter.a 2>/dev/null && echo "OK: flow_filter.a generated" || echo "FAIL: flow_filter.a not generated"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if "FAIL:" in out:
        print(f"\nStep failed: {label}")
        break

client.close()
print("\nDone")
