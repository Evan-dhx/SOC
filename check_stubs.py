import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check all filter headers for boost dependency
print("=== Checking all filters for boost ===")
cmd = r"""grep -l 'boost' /root/SOC/ly_analyser_src/agent/flow/*.h /root/SOC/ly_analyser_src/agent/flow/*.cpp 2>/dev/null"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())

# Check what headers flow_indexer.cpp includes
print("\n=== flow_indexer.cpp includes ===")
cmd2 = r"""head -30 /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())

# Check the filter class declarations
print("\n=== AI filter class declarations ===")
cmd3 = r"""grep -A5 'class DgaFilter' /root/SOC/ly_analyser_src/agent/flow/dga_filter.h | head -10"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())

client.close()
