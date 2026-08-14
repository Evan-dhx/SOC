import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Search for .slice().sort() or .sort() in the frontend source
print("=== Search for sort in source ===")
cmd = r"""
grep -rn '\.sort\|\.slice' /root/SOC/ly_vis/packages/std/src/ 2>/dev/null | grep -v 'node_modules' | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Search in components package too
print("\n=== Search in components ===")
cmd2 = r"""
grep -rn '\.sort\|\.slice' /root/SOC/ly_vis/packages/components/src/ 2>/dev/null | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Search for the specific pattern t.slice().sort()
print("\n=== Search for slice().sort() pattern ===")
cmd3 = r"""
grep -rn 'slice.*sort\|\.sort(' /root/SOC/ly_vis/packages/std/src/ 2>/dev/null | head -20
echo "---"
grep -rn 'slice.*sort\|\.sort(' /root/SOC/ly_vis/packages/components/src/ 2>/dev/null | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check the overview/om page component
print("\n=== Overview page component ===")
cmd4 = r"""
find /root/SOC/ly_vis/packages/std/src/ -path '*overview*' -o -path '*om*' 2>/dev/null | grep -v node_modules | head -20
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
