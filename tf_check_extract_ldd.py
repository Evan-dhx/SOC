import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("检查 extract_feature 链接", r"""
echo "=== 1. extract_feature 链接的库 ==="
ldd /Agent/cmd/extract_feature 2>&1 | grep -E "tensorflow|protobuf|common" 
echo ""
echo "=== 2. 直接运行 extract_feature（文本输入） ==="
echo 'devid: 1
starttime: 1786596300
endtime: 1786601400' | timeout 30 /Agent/cmd/extract_feature 2>&1 | head -20
echo "退出码: $?"
echo ""
echo "=== 3. extract_feature.cpp 源码入口 ==="
grep -n "int main\|http_post\|getenv\|stdin\|cin" /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp 2>/dev/null | head -15
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
