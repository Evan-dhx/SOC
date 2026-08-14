import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Fix C++17 and macro conflict", r"""
echo "=== Fix Makefile: upgrade to C++17 ==="
cd /root/SOC/ly_analyser_src/agent/flow

# Upgrade from c++14 to c++17 (needed for std::optional in TF 2.12)
sed -i 's/-std=c++14/-std=c++17/' Makefile

echo "New CXXFLAGS:"
grep "^CXXFLAGS=" Makefile
"""),

    ("Check nffile.h macro conflict", r"""
echo "=== Check nffile.h v4 macro ==="
grep -n "define v4\|define v6" /root/SOC/ly_analyser_src/agent/dump/nffile.h | head -5
echo ""
echo "=== Check what includes nffile.h in dga_filter chain ==="
grep -n "nffile\|nfdump" /root/SOC/ly_analyser_src/agent/flow/dga_filter.h /root/SOC/ly_analyser_src/agent/flow/dga_filter.cpp 2>/dev/null | head -10
echo ""
echo "=== Check flow_filter.cpp include chain ==="
grep -n "nffile\|nfdump\|dump/" /root/SOC/ly_analyser_src/agent/flow/flow_filter.cpp 2>/dev/null | head -10
echo ""
echo "=== Check tsdb.h include chain ==="
grep -n "nffile\|nfdump\|dump/" /root/SOC/ly_analyser_src/agent/data/tsdb.h 2>/dev/null | head -10
"""),

    ("Fix macro conflict in dga_filter.cpp", r"""
echo "=== Fix macro conflict ==="
# The issue: nffile.h defines #define v4 ip_union._v4
# This conflicts with absl/strings/numbers.h which uses v4 as a variable name
# Solution: undef v4/v6 before including TF headers, then redefine after

# Check if dga_filter.cpp includes nffile.h directly or indirectly
grep -n "#include" /root/SOC/ly_analyser_src/agent/flow/dga_filter.cpp | head -10
echo ""
grep -n "#include" /root/SOC/ly_analyser_src/agent/flow/dga_filter.h | head -10
"""),

    ("Add undef workaround in dga_filter.h", r"""
echo "=== Patch dga_filter.h to handle macro conflict ==="
cd /root/SOC/ly_analyser_src/agent/flow

# Backup
cp dga_filter.h dga_filter.h.backup

# The TF headers are included in dga_filter.h
# We need to save and undef conflicting macros before TF includes, then restore after
# First check what the current includes look like
head -25 dga_filter.h
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)

client.close()
