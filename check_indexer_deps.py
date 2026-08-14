import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check what flow_indexer.cpp needs from AI filters
print("=== Checking flow_indexer.cpp AI filter references ===")
cmd = r"""grep -n 'DgaFilter\|DnstunAIFilter\|MiningFilter\|ThreatFilter' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp | head -30"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())

# Check which filters are used
print("\n=== Filter includes in flow_indexer.cpp ===")
cmd2 = r"""grep '#include.*filter' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())

# Check if dns_filter uses boost regex
print("\n=== dns_filter boost usage ===")
cmd3 = r"""grep -n 'boost' /root/SOC/ly_analyser_src/agent/flow/dns_filter.h /root/SOC/ly_analyser_src/agent/flow/dns_filter.cpp 2>/dev/null | head -10"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())

client.close()
