import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("安装并测试 extract_feature", r"""
echo "=== 1. 安装新二进制 ==="
cp /root/SOC/ly_analyser_src/agent/handlers/extract_feature /Agent/cmd/extract_feature
chmod 755 /Agent/cmd/extract_feature
ls -la /Agent/cmd/extract_feature
echo ""
echo "=== 2. 命令行测试 ==="
echo 'devid: 1
starttime: 1786596300
endtime: 1786601400' | timeout 60 /Agent/cmd/extract_feature 2>&1 | head -c 1500
echo ""
echo "退出码: $?"
echo ""
echo "=== 3. HTTP 测试（10081） ==="
curl -s -X POST "http://127.0.0.1:10081/extract_feature" -d "devid: 1
starttime: 1786596300
endtime: 1786601400" --max-time 60 2>&1 | head -c 1500
echo ""
echo "=== 4. web feature 接口 ==="
curl -s "http://127.0.0.1/d/feature?action=get&devid=1&starttime=1786596300&endtime=1786601400" --max-time 60 2>&1 | head -c 2000
echo ""
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
