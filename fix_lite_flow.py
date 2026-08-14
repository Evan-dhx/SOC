import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Create a minimal flow_filter without AI filters (they need boost_regex + TF)
print("=== Creating minimal flow_filter for indexing ===")
cmd = r"""
cd /root/SOC/ly_analyser_src/agent/flow
# Create flow_filter_lite.a without AI/TensorFlow-dependent objects
ar t flow_filter.a | grep -v 'dga_filter\|dnstun_ai_filter\|mining_filter\|threat_filter' > /tmp/lite_objects.txt
cat /tmp/lite_objects.txt
# Extract needed objects and create lite archive
rm -f /tmp/lite_objs/*.o 2>/dev/null
mkdir -p /tmp/lite_objs
cd /tmp/lite_objs
ar x /root/SOC/ly_analyser_src/agent/flow/flow_filter.a
# Remove AI-dependent objects
rm -f dga_filter.o dnstun_ai_filter.o mining_filter.o threat_filter.o
# Create lite archive
ar rcs /root/SOC/ly_analyser_src/agent/flow/flow_filter_lite.a *.o
echo "Created flow_filter_lite.a"
ls -la /root/SOC/ly_analyser_src/agent/flow/flow_filter_lite.a
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print(stdout.read().decode())
print(stderr.read().decode())

# Update indexing Makefile to use flow_filter_lite.a
print("\n=== Updating indexing Makefile ===")
cmd2 = r"""cd /root/SOC/ly_analyser_src/agent/indexing
sed -i 's|../flow/flow_filter.a|../flow/flow_filter_lite.a|' Makefile
echo 'Updated to use flow_filter_lite.a'
grep 'LIBS=' Makefile"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Rebuild indexing
print("\n=== Rebuilding indexing ===")
cmd3 = r"""cd /root/SOC/ly_analyser_src/agent/indexing && make clean 2>&1 | tail -1 && make 2>&1 | tail -20"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("=== STDOUT ===")
print(out)
if err.strip():
    print("=== STDERR ===")
    print(err)

client.close()
