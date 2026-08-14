import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Find Eigen header location
    ("find eigen", r"""
echo "=== Find Eigen ==="
find /usr/local/include/tf -name 'Tensor' -path '*/Eigen/*' 2>/dev/null | head -5
echo "---"
find /usr/local/include -name 'Tensor' -path '*/Eigen/*' 2>/dev/null | head -5
echo "---"
# Check the include path used by the original Makefile
grep -i 'eigen' /root/SOC/ly_analyser_src/agent/flow/Makefile | head -5
"""),

    # 2. Recompile with correct Eigen path
    ("recompile with eigen path", r"""
cd /root/SOC/ly_analyser_src/agent/flow

# Get the correct include paths from the flow Makefile
EIGEN_INC="-I/usr/local/include/tf/tensorflow/contrib/makefile/downloads/eigen"
ABSL_INC="-I/usr/local/include/tf/tensorflow/contrib/makefile/downloads/absl"
PROTO_INC="-I/usr/local/include/tf/tensorflow/contrib/makefile/gen/protobuf/include"
TF_BASE="-I/usr/local/include/tf"
TF_GENFILES="-I/usr/local/include/tf/bazel-genfiles"
TF_TENSORFLOW="-I/usr/local/include/tf/tensorflow"
TF_THIRD="-I/usr/local/include/tf/tensorflow/third-party"
TF_PROTO="-I/usr/local/include/tf/tensorflow/contrib/makefile/gen/proto"

COMMON_INCS="$TF_BASE $TF_GENFILES $TF_TENSORFLOW $TF_THIRD $EIGEN_INC $ABSL_INC $PROTO_INC $TF_PROTO -I/usr/local/include -I.."

echo "=== Compiling dga_filter with ABI=0 ==="
g++ -c -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++11 -fPIC \
    $COMMON_INCS \
    dga_filter.cpp -o dga_filter_abi0.o 2>&1
echo "dga_filter exit: $?"

echo ""
echo "=== Compiling dnstun_ai_filter with ABI=0 ==="
g++ -c -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++11 -fPIC \
    $COMMON_INCS \
    dnstun_ai_filter.cpp -o dnstun_ai_filter_abi0.o 2>&1
echo "dnstun_ai_filter exit: $?"

echo ""
echo "=== Check results ==="
ls -la *_abi0.o 2>/dev/null
"""),

    # 3. Rebuild flow_filter_full.a with all 4 AI filters
    ("rebuild full filter", r"""
cd /root/SOC/ly_analyser_src/agent/flow

# Check if we have all 4 AI filter objects
echo "=== AI filter objects ==="
for f in dga_filter_abi0.o threat_filter_abi0.o dnstun_ai_filter_abi0.o mining_filter_abi0.o; do
    if [ -f "$f" ]; then
        echo "$f: EXISTS ($(stat -c%s $f) bytes)"
    else
        echo "$f: MISSING"
    fi
done

# Rebuild flow_filter_full.a
mkdir -p /tmp/flow_objs2
cd /tmp/flow_objs2
rm -rf *
ar x /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a 2>/dev/null

# Copy available AI filter objects
for f in /root/SOC/ly_analyser_src/agent/flow/*_abi0.o; do
    if [ -f "$f" ]; then
        cp "$f" .
        echo "Added: $(basename $f)"
    fi
done

echo "Total objects: $(ls *.o | wc -l)"

ar rcs /root/SOC/ly_analyser_src/agent/flow/flow_filter_full.a *.o
echo "Created flow_filter_full.a: $(stat -c%s /root/SOC/ly_analyser_src/agent/flow/flow_filter_full.a) bytes"
"""),

    # 4. Try to build indexer
    ("build indexer", r"""
cd /root/SOC/ly_analyser_src/agent/indexing

# Check if all AI filter objects are available
echo "=== Check AI filters in flow_filter_full.a ==="
ar t ../flow/flow_filter_full.a | grep -E 'dga|threat|dnstun|mining'

echo ""
echo "=== Building indexer ==="
make clean 2>/dev/null
make 2>&1 | tail -20
echo "Build exit: ${PIPESTATUS[0]}"
"""),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
