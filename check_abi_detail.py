import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check what TF symbols are actually used by the code
print("=== Checking TF symbols used in flow module ===")
cmd = r"""nm /root/SOC/ly_analyser_src/agent/flow/flow_filter.a 2>/dev/null | grep 'tensorflow' | grep ' U ' | head -20"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())

# Check if any TF symbols involve std::string
print("\n=== TF symbols with string ===")
cmd2 = r"""nm /root/SOC/ly_analyser_src/agent/flow/flow_filter.a 2>/dev/null | grep 'tensorflow' | grep ' U ' | grep -i 'string\|cxx11' | head -20"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())

# Check cgicc symbols in libcommon.so
print("\n=== cgicc symbols needed by libcommon.so ===")
cmd3 = r"""nm -D /root/SOC/ly_analyser_src/common/libcommon.so 2>/dev/null | grep 'cgicc\|cppdb' | grep ' U ' | head -10"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())

# Check system cgicc ABI
print("\n=== cgicc library symbols ===")
cmd4 = r"""nm -D /usr/lib64/libcgicc.so 2>/dev/null | grep 'operator()' | head -5"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=30)
print(stdout.read().decode())

client.close()
