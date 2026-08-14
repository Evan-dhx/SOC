import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check symbols in libcommon.a
print("=== Checking ipnum_to_ipstr in libcommon.a ===")
cmd = r"""nm /usr/lib64/libcommon.so 2>/dev/null | grep 'ipnum_to_ipstr' | head -5"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check in the local common lib
print("\n=== Checking in ly_analyser common ===")
cmd2 = r"""nm /root/SOC/ly_analyser_src/common/libcommon.so 2>/dev/null | grep 'ipnum_to_ipstr' | head -5"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check what ABI the common lib was compiled with
print("\n=== Checking common lib ABI ===")
cmd3 = r"""nm /root/SOC/ly_analyser_src/common/libcommon.so 2>/dev/null | grep 'trim' | head -5"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Check what the flow module expects
print("\n=== Checking flow expected symbols ===")
cmd4 = r"""nm /root/SOC/ly_analyser_src/agent/flow/flow_filter.a 2>/dev/null | grep 'ipnum_to_ipstr' | grep ' U ' | head -5"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
