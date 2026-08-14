import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Check what's in libcommon.so
    ("check libcommon", r"""
echo "=== libcommon symbols ==="
nm -D /lib64/libcommon.so 2>/dev/null | grep -E 'ipnum_to_ipstr|valid_ip' | head -10
echo "---"
# Check if libcommon was compiled with new ABI
nm -D /lib64/libcommon.so 2>/dev/null | grep 'ipnum_to_ipstr' | head -5
"""),

    # 2. The issue is ABI mismatch - libcommon uses new ABI symbols
    # but dnstun_ai_filter_abi0.o expects old ABI symbols
    # Solution: compile libcommon's ip.cpp with old ABI too
    ("check ip.cpp", r"""
echo "=== ip.cpp functions ==="
grep -n 'ipnum_to_ipstr\|valid_ip' /root/SOC/ly_analyser_src/common/ip.cpp | head -10
echo "---"
grep -n 'ipnum_to_ipstr\|valid_ip' /root/SOC/ly_analyser_src/common/ip.h | head -10
"""),

    # 3. Recompile ip.cpp with old ABI and add to flow_filter_full.a
    ("recompile ip with ABI0", r"""
cd /root/SOC/ly_analyser_src/common

# Recompile ip.cpp with old ABI
g++ -c -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++11 -fPIC \
    -I. -I/usr/include \
    ip.cpp -o ip_abi0.o 2>&1
echo "ip.cpp compile: $?"

# Also recompile other common files that AI filters might need
for f in datetime.cpp file.cpp; do
    if [ -f "$f" ]; then
        g++ -c -D_GLIBCXX_USE_CXX11_ABI=0 -std=c++11 -fPIC \
            -I. -I/usr/include \
            $f -o ${f%.cpp}_abi0.o 2>&1
        echo "$f compile: $?"
    fi
done

ls -la *_abi0.o 2>/dev/null
"""),

    # 4. Rebuild flow_filter_full.a with ip_abi0.o included
    ("rebuild with ip", r"""
cd /root/SOC/ly_analyser_src/agent/flow

# Rebuild flow_filter_full.a
mkdir -p /tmp/flow_objs3
cd /tmp/flow_objs3
rm -rf *

# Extract non-AI objects
ar x /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a 2>/dev/null

# Add all AI filter objects
cp /root/SOC/ly_analyser_src/agent/flow/dga_filter_abi0.o .
cp /root/SOC/ly_analyser_src/agent/flow/threat_filter_abi0.o .
cp /root/SOC/ly_analyser_src/agent/flow/dnstun_ai_filter_abi0.o .
cp /root/SOC/ly_analyser_src/agent/flow/mining_filter_abi0.o .

# Add ip_abi0.o from common
cp /root/SOC/ly_analyser_src/common/ip_abi0.o . 2>/dev/null && echo "Added ip_abi0.o"

echo "Total objects: $(ls *.o | wc -l)"

ar rcs /root/SOC/ly_analyser_src/agent/flow/flow_filter_full.a *.o
echo "Created: $(stat -c%s /root/SOC/ly_analyser_src/agent/flow/flow_filter_full.a) bytes"
"""),

    # 5. Rebuild indexer
    ("rebuild indexer", r"""
cd /root/SOC/ly_analyser_src/agent/indexing
make clean 2>/dev/null
make 2>&1 | tail -15
echo "Build exit: ${PIPESTATUS[0]}"
"""),

    # 6. If still failing, try linking ip_abi0.o directly
    ("direct link fix", r"""
cd /root/SOC/ly_analyser_src/agent/indexing

# If make failed, try adding ip_abi0.o directly to the link
if [ ! -f indexer ]; then
    echo "=== Direct link with ip_abi0.o ==="
    g++ -DENABLE_AI -Wall -fPIC -g -std=c++14 -DAGENT -O2 \
        -I. -I/usr/include -I/usr/local/include \
        -I/usr/local/include/tf/ -I/usr/local/include/tf/bazel-genfiles \
        -I/usr/local/include/tf/tensorflow -I/usr/local/include/tf/tensorflow/third-party \
        -I/usr/local/include/tf/tensorflow/contrib/makefile/downloads/eigen \
        -I/usr/local/include/tf/tensorflow/contrib/makefile/downloads/absl \
        -I/usr/local/include/tf/tensorflow/contrib/makefile/gen/protobuf/include \
        -I/usr/local/include/tf/tensorflow/contrib/makefile/gen/proto \
        -I../../common \
        -o indexer indexer.o flow_indexer.o cache_generator.o \
        -L/usr/lib64 -L/usr/lib -L/usr/local/lib -L. -L../../common -L../flow \
        -Wl,--start-group \
        ../dump/libnfdump.a ../flow/flow_filter_full.a ../model/model.a ../data/data.a ../config/config.a \
        /root/SOC/ly_analyser_src/common/ip_abi0.o \
        -Wl,--whole-archive -lprotobuf -Wl,--no-whole-archive \
        -lcommon -lboost_regex -ltensorflow_cc -ltensorflow_framework \
        -lcppdb -lcgicc -lcurl -lpthread \
        -Wl,--end-group 2>&1 | tail -10
    echo "Direct link exit: $?"
fi

ls -la indexer 2>/dev/null
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
