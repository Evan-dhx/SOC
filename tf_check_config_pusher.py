import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check config_pusher", r"""
echo "=== 1. config_pusher 是否存在 ==="
ls -la /Server/bin/config_pusher 2>/dev/null
echo ""
echo "=== 2. config_pusher.log ==="
tail -20 /data/log/config_pusher.log 2>/dev/null
echo ""
echo "=== 3. extractor read_config 实现 ==="
grep -n -A20 "read_config" /root/SOC/ly_analyser_src/agent/handlers/extractor.cpp | head -40
echo ""
echo "=== 4. /Agent/data 下所有文件 ==="
find /Agent/data -type f 2>/dev/null | head -20
echo ""
echo "=== 5. /Agent/etc ==="
ls -la /Agent/etc/ 2>/dev/null
"""),

    ("Check extractor config path", r"""
echo "=== 6. config 读取路径（common 库） ==="
grep -rn "AGENT_CFG_FILE\|read_config\|ReadConfig" /root/SOC/ly_analyser_src/common/config.cpp /root/SOC/ly_analyser_src/common/config.h 2>/dev/null | head -15
echo ""
echo "=== 7. config_pusher 源码 ==="
grep -rn "AGENT_CFG_FILE\|/Agent/data/config\|WriteConfig\|SaveConfig" /root/SOC/ly_analyser_src/agent/ 2>/dev/null | grep -v "\.o:" | head -10
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
