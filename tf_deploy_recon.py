import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("服务器编译环境侦察", r"""
echo "=== 1. 源码副本结构 ==="
ls /root/SOC/ 2>/dev/null
echo ""
echo "=== 2. ly_server 编译方式 ==="
ls /root/SOC/ly_server_src/server/*.cpp 2>/dev/null | head -3
grep -m3 "config_pusher\|config_agent" /root/SOC/ly_server_src/server/Makefile 2>/dev/null | head -5
echo ""
echo "=== 3. protoc 版本 ==="
protoc --version 2>&1
which protoc
echo ""
echo "=== 4. agent 编译 ==="
ls /root/SOC/ly_analyser_src/agent/handlers/ 2>/dev/null | head -8
echo ""
echo "=== 5. 已部署的 config/actl/fsd 二进制 ==="
ls -la /Agent/bin/ 2>/dev/null | grep -E "config|actl|fsd|indexer" 
echo ""
echo "=== 6. 当前 agent 配置（dev 部分） ==="
head -30 /Agent/data/config 2>/dev/null
echo ""
echo "=== 7. probe.conf ==="
cat /Agent/etc/probe.conf 2>/dev/null | head -20
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()