import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check current state of flow_indexer files
    "echo '=== flow_indexer.h AI lines ==='",
    "grep -n 'dga_\\|threat_\\|dnstun_ai_\\|mining_\\|DgaFilter\\|ThreatFilter\\|DnstunAIFilter\\|MiningFilter' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.h",
    
    "echo '=== flow_indexer.cpp AI lines ==='",
    "grep -n 'dga_\\|threat_\\|dnstun_ai_\\|mining_\\|DgaFilter\\|ThreatFilter\\|DnstunAIFilter\\|MiningFilter' /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp",
    
    "echo '=== flow_indexer.h includes ==='",
    "head -35 /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.h",
    
    "echo '=== flow_indexer.cpp head ==='",
    "head -25 /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp",
    
    "echo '=== Current Makefile ==='",
    "cat /root/SOC/ly_analyser_src/agent/indexing/Makefile",
    
    "echo '=== Check .orig backups ==='",
    "ls -la /root/SOC/ly_analyser_src/agent/indexing/*.orig 2>/dev/null",
    
    "echo '=== Check flow_filter files ==='",
    "ls -la /root/SOC/ly_analyser_src/agent/flow/*.a 2>/dev/null",
    
    "echo '=== Check which flow objects use boost::regex ==='",
    "nm /root/SOC/ly_analyser_src/agent/flow/*.o 2>/dev/null | grep -i 'boost.*regex' | head -20",
    
    "echo '=== Check handlers dir ==='",
    "ls /root/SOC/ly_analyser_src/agent/handlers/ 2>/dev/null",
    
    "echo '=== Check agent Makefile ==='",
    "cat /root/SOC/ly_analyser_src/agent/Makefile",
]

for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out)
    if err and 'warning' not in err.lower():
        print(f"STDERR: {err}")
    print()

client.close()
