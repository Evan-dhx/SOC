import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Find the "客户端错误" message source
print("=== Search for error message ===")
cmd = r"""
grep -rn '客户端错误\|请检查地址' /root/SOC/ly_vis/packages/ 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Read the request-config module
print("\n=== request-config ===")
cmd2 = r"""
find /root/SOC/ly_vis/packages/components/ -name 'request-config*' -o -name 'methods-auth*' 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Read the request error callback
print("\n=== request-config source ===")
cmd3 = r"""
find /root/SOC/ly_vis/packages/components/ -path '*/request-config*' -name '*.js' -o -path '*/request-config*' -name '*.jsx' 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
files = stdout.read().decode('utf-8', errors='replace').strip()
print(files)
if files:
    for f in files.split('\n'):
        if f.strip():
            print(f"\n--- {f.strip()} ---")
            cmd4 = f"cat -n '{f.strip()}' 2>/dev/null"
            stdin, stdout, stderr = client.exec_command(cmd4, timeout=15)
            print(stdout.read().decode('utf-8', errors='replace'))

# Read methods-auth
print("\n=== methods-auth ===")
cmd5 = r"""
find /root/SOC/ly_vis/packages/components/ -path '*methods-auth*' -name '*.js' 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=15)
files2 = stdout.read().decode('utf-8', errors='replace').strip()
print(files2)
if files2:
    for f in files2.split('\n'):
        if f.strip():
            print(f"\n--- {f.strip()} ---")
            cmd6 = f"cat -n '{f.strip()}' 2>/dev/null"
            stdin, stdout, stderr = client.exec_command(cmd6, timeout=15)
            print(stdout.read().decode('utf-8', errors='replace'))

client.close()
