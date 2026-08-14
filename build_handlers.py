import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check if handlers reference AI filters
print("=== Check handlers for AI filter references ===")
cmd = "grep -l 'dga_filter\\|threat_filter\\|dnstun_ai_filter\\|mining_filter\\|DgaFilter\\|ThreatFilter\\|DnstunAIFilter\\|MiningFilter\\|tensorflow' /root/SOC/ly_analyser_src/agent/handlers/*.cpp /root/SOC/ly_analyser_src/agent/handlers/*.h 2>/dev/null"
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
out = stdout.read().decode()
print(out if out.strip() else "No AI/TF references found in handlers")

# Fix handlers Makefile and build
print("\n=== Fixing handlers Makefile and building ===")
cmd2 = r"""
cd /root/SOC/ly_analyser_src/agent/handlers

# Replace flow_filter.a with flow_filter_noai.a
sed -i 's|flow_filter.a|flow_filter_noai.a|g' Makefile

# Remove TensorFlow library links
sed -i 's|-ltensorflow_cc -ltensorflow_framework||g' Makefile

# Add cppdb and curl to LDLIBS (may be needed)
sed -i 's|-lboost_regex -lpthread|-lboost_regex -lcppdb -lcurl -lpthread|' Makefile

echo "=== Updated Makefile ==="
grep -E 'LIBS=|LDLIBS=' Makefile

echo ""
echo "=== Building handlers ==="
make clean 2>/dev/null
make 2>&1 | tail -50
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=180)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print(f"STDERR: {err}")

client.close()
