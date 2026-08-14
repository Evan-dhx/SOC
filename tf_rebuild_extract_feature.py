import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重新编译 extract_feature", r"""
echo "=== 1. 备份旧二进制 ==="
cp /Agent/cmd/extract_feature /Agent/cmd/extract_feature.bak_old
echo "备份完成"
cd /root/SOC/ly_analyser_src/agent/handlers
echo ""
echo "=== 2. 删除旧对象文件并编译 ==="
rm -f extract_feature.o extract_feature
make extract_feature 2>&1 | tail -20
echo ""
echo "=== 3. 检查产物 ==="
ls -la extract_feature 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
