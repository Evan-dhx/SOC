import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check what type values the frontend sends to config endpoint
print("=== Frontend config API calls ===")
cmd = r"""
grep -rn "type.*device\|type.*agent\|type.*=.*'" /root/SOC/ly_vis/packages/std/src/service/ 2>/dev/null | head -20
echo "---"
grep -rn "'device'\|'agent'\|type:" /root/SOC/ly_vis/packages/std/src/store/ 2>/dev/null | head -20
echo "---"
# Check the config store
find /root/SOC/ly_vis/packages/std/src/ -name '*config*' -name '*.js' -o -name '*config*' -name '*.jsx' 2>/dev/null
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check config_class.cpp for type mapping
print("\n=== config_class type mapping ===")
cmd2 = r"""
grep -n 'type\|device\|agent\|createConfig' /root/SOC/ly_server_src/lib/config_class.cpp 2>/dev/null | head -30
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Check config.cpp for how it builds the .so path
print("\n=== config.cpp dlopen ===")
cmd3 = r"""
cat -n /root/SOC/ly_server_src/server/config.cpp
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Try different type values
print("\n=== Try different config types ===")
cmd4 = r"""
for t in device agent mo bwlist event user internalip internalsrv; do
    echo -n "type=$t: "
    curl -s http://localhost/d/config -d "auth_target=config&type=$t&op=get" 2>&1 | head -c 200
    echo ""
done
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
