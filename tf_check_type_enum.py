import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("feature.proto Type 枚举 + 参数解析", r"""
echo "=== 1. feature.proto Type 枚举 ==="
grep -n -A30 "enum Type\|enum FeatureType" /root/SOC/ly_analyser_src/common/feature.proto | head -40
echo ""
echo "=== 2. feature_req.cpp CGI 解析完整（260-330 行） ==="
sed -n '260,330p' /root/SOC/ly_analyser_src/common/feature_req.cpp
echo ""
echo "=== 3. feature_req.cpp 中 type 处理 ==="
grep -n "type\|Type" /root/SOC/ly_analyser_src/common/feature_req.cpp | head -20
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
