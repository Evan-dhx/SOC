import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Check current TF library ABI
    ("check TF ABI", r"""
echo "=== TensorFlow library ==="
ls -la /usr/local/lib/libtensorflow* 2>/dev/null
echo "---"
# Check if TF was compiled with old ABI
strings /usr/local/lib/libtensorflow_cc.so.2 2>/dev/null | grep -i 'abi\|cxx11\|GLIBCXX' | head -5
echo "---"
# Check TF version
python3 -c "import tensorflow as tf; print(tf.__version__)" 2>/dev/null || echo "TF Python not available"
echo "---"
file /usr/local/lib/libtensorflow_cc.so.2 2>/dev/null
"""),

    # 2. Check which AI filter files need recompilation
    ("check AI filters", r"""
echo "=== AI filter source files ==="
ls -la /root/SOC/ly_analyser_src/agent/flow/dga_filter.* /root/SOC/ly_analyser_src/agent/flow/threat_filter.* /root/SOC/ly_analyser_src/agent/flow/dnstun_ai_filter.* /root/SOC/ly_analyser_src/agent/flow/mining_filter.* 2>/dev/null
echo "---"
echo "=== Current flow_filter.a ==="
ls -la /root/SOC/ly_analyser_src/agent/flow/flow_filter*.a 2>/dev/null
echo "---"
echo "=== Current flow_filter_noai.a ==="
ls -la /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a 2>/dev/null
"""),

    # 3. Check the flow/Makefile
    ("check Makefile", r"""
cat /root/SOC/ly_analyser_src/agent/flow/Makefile
"""),

    # 4. Recompile AI filters with old ABI
    ("recompile AI filters", r"""
cd /root/SOC/ly_analyser_src/agent/flow

# Compile AI filter objects with old ABI flag
echo "=== Compiling AI filters with ABI=0 ==="
g++ -c -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++11 -fPIC \
    -I/usr/local/include \
    -I/usr/local/include/tf \
    -I.. \
    dga_filter.cpp -o dga_filter_abi0.o 2>&1
echo "dga_filter: $?"

g++ -c -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++11 -fPIC \
    -I/usr/local/include \
    -I/usr/local/include/tf \
    -I.. \
    threat_filter.cpp -o threat_filter_abi0.o 2>&1
echo "threat_filter: $?"

g++ -c -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++11 -fPIC \
    -I/usr/local/include \
    -I/usr/local/include/tf \
    -I.. \
    dnstun_ai_filter.cpp -o dnstun_ai_filter_abi0.o 2>&1
echo "dnstun_ai_filter: $?"

g++ -c -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++11 -fPIC \
    -I/usr/local/include \
    -I/usr/local/include/tf \
    -I.. \
    mining_filter.cpp -o mining_filter_abi0.o 2>&1
echo "mining_filter: $?"

echo "---"
ls -la *_abi0.o 2>/dev/null
"""),

    # 5. Create new flow_filter.a with AI filters included
    ("create full flow_filter", r"""
cd /root/SOC/ly_analyser_src/agent/flow

# Extract non-AI objects from flow_filter_noai.a
mkdir -p /tmp/flow_objs
cd /tmp/flow_objs
rm -rf *
ar x /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a 2>/dev/null
echo "Extracted non-AI objects:"
ls *.o 2>/dev/null | wc -l

# Add AI filter objects
cp /root/SOC/ly_analyser_src/agent/flow/dga_filter_abi0.o .
cp /root/SOC/ly_analyser_src/agent/flow/threat_filter_abi0.o .
cp /root/SOC/ly_analyser_src/agent/flow/dnstun_ai_filter_abi0.o .
cp /root/SOC/ly_analyser_src/agent/flow/mining_filter_abi0.o .

echo "Total objects:"
ls *.o | wc -l

# Create new flow_filter.a
ar rcs /root/SOC/ly_analyser_src/agent/flow/flow_filter_full.a *.o
echo "Created flow_filter_full.a"
ls -la /root/SOC/ly_analyser_src/agent/flow/flow_filter_full.a
"""),

    # 6. Rebuild indexer with full flow_filter (including AI)
    ("rebuild indexer", r"""
cd /root/SOC/ly_analyser_src/agent/indexing

# Update Makefile to use flow_filter_full.a and add TF libs
cp Makefile Makefile.noai

# Replace flow_filter_noai.a with flow_filter_full.a and add TF libs
sed -i 's|flow_filter_noai.a|flow_filter_full.a|' Makefile

# Check if TF libs are already in LDLIBS
grep -n 'tensorflow\|TF_LIB' Makefile | head -5
echo "---"

# Add TF libs if not present
if ! grep -q 'tensorflow_cc' Makefile; then
    sed -i 's|-lboost_regex|-lboost_regex -ltensorflow_cc -ltensorflow_framework|' Makefile
    echo "Added TF libs to Makefile"
fi

# Add ENABLE_AI define
if ! grep -q 'ENABLE_AI' Makefile; then
    sed -i 's|CXXFLAGS=|CXXFLAGS+=-DENABLE_AI |' Makefile 2>/dev/null
    # Or add to the compile command
    sed -i '1s|^|CXXFLAGS += -DENABLE_AI\n|' Makefile
    echo "Added ENABLE_AI define"
fi

echo "=== Updated Makefile ==="
cat Makefile
"""),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
