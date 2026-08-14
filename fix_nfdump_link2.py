import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=== Checking nfdump.c FlowFilters reference ===")
cmd = r"""
grep -n 'FlowFilter\|flow_filter' /root/SOC/ly_analyser_src/nfdump/bin/nfdump.c | head -10
echo ""
echo "=== Check what headers it includes ==="
grep -n '#include.*flow\|#include.*filter' /root/SOC/ly_analyser_src/nfdump/bin/nfdump.c
echo ""
echo "=== Check flow_filter library ==="
nm /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a 2>/dev/null | grep 'FlowFilters' | head -5
echo ""
echo "=== Check nfdump LDADD ==="
grep 'LDADD\|am_nfdump\|nfdump_LDADD\|nfdump_DEPENDENCIES' /root/SOC/ly_analyser_src/nfdump/bin/Makefile | head -10
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode())

# Fix: add flow_filter_noai.a and common back
print("\n=== Fixing nfdump link with flow_filter_noai.a ===")
cmd2 = r"""
cd /root/SOC/ly_analyser_src/nfdump/bin

# Add back flow_filter_noai.a and common as direct .a file references
# Replace the nfdump link line to include the static libraries directly
FLOW_FILTER=/root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a
COMMON_LIB=/root/SOC/ly_analyser_src/common/libcommon.so

# Modify the nfdump target link command
# The link line is in the Makefile as nfdump_LINK
# Let's just override with LDFLAGS
sed -i "s|LIBS =  -lresolv|LIBS = ${FLOW_FILTER} -lcommon -lboost_regex -lcppdb -lcurl -lresolv -lpthread|" Makefile

# Also need include path for flow_filter headers
sed -i 's|nfdump_CFLAGS =|nfdump_CFLAGS = -I/root/SOC/ly_analyser_src/agent -I/root/SOC/ly_analyser_src/common|' Makefile

echo "Updated LIBS:"
grep '^LIBS' Makefile

echo ""
echo "=== Rebuilding ==="
cd /root/SOC/ly_analyser_src/nfdump
make 2>&1 | tail -20
echo ""
echo "=== Install ==="
make install 2>&1 | tail -10
echo ""
echo "=== Check nfdump ==="
ls -la /Agent/bin/ 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=300)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
