import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check what symbols the new-ABI flow objects need from common
print("=== Checking new-ABI flow symbols from common ===")
cmd = r"""nm /root/SOC/ly_analyser_src/agent/flow/flow_filter.a 2>/dev/null | grep ' U ' | grep -v 'boost\|tensorflow\|google\|proto\|std::\|__\|typeinfo\|vtable\|operator\|non-virtual\|virtual' | sort -u | head -30"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())

# Check if old-ABI common has the new-ABI symbols needed
print("\n=== Checking old-ABI common for new-ABI symbols ===")
cmd2 = r"""
echo "--- ipnum_to_ipstr ---"
nm /root/SOC/ly_analyser_src/common_oldabi/libcommon_oldabi.a 2>/dev/null | grep 'ipnum_to_ipstr' | grep -v ' U '
echo "--- trim ---"
nm /root/SOC/ly_analyser_src/common_oldabi/libcommon_oldabi.a 2>/dev/null | grep 'trim' | grep -v ' U ' | head -5
echo "--- proto_to_string ---"
nm /root/SOC/ly_analyser_src/common_oldabi/libcommon_oldabi.a 2>/dev/null | grep 'proto_to_string' | grep -v ' U '
echo "--- format_timestamp ---"
nm /root/SOC/ly_analyser_src/common_oldabi/libcommon_oldabi.a 2>/dev/null | grep 'format_timestamp' | grep -v ' U '
echo "--- sha256 ---"
nm /root/SOC/ly_analyser_src/common_oldabi/libcommon_oldabi.a 2>/dev/null | grep 'sha256' | grep -v ' U ' | head -3
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())

# Check what the new-ABI flow objects expect
print("\n=== What new-ABI flow expects ===")
cmd3 = r"""
echo "--- ipnum_to_ipstr ---"
nm /root/SOC/ly_analyser_src/agent/flow/flow_filter.a 2>/dev/null | grep 'ipnum_to_ipstr' | grep ' U ' | head -3
echo "--- trim ---"
nm /root/SOC/ly_analyser_src/agent/flow/flow_filter.a 2>/dev/null | grep 'trim' | grep ' U ' | head -3
echo "--- format_timestamp ---"
nm /root/SOC/ly_analyser_src/agent/flow/flow_filter.a 2>/dev/null | grep 'format_timestamp' | grep ' U ' | head -3
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())

client.close()
