import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check indexer can load (ldd + quick run)", r"""
echo "=== 1. indexer 动态库完整性 ==="
ldd /Agent/bin/indexer 2>&1 | grep -E "not found|tensorflow|common" 
echo ""
echo "=== 2. indexer --help 测试 ==="
cd /tmp
timeout 5 /Agent/bin/indexer --help 2>&1 | head -20
echo "Exit: $?"
echo ""
echo "=== 3. indexer -v 测试 ==="
timeout 5 /Agent/bin/indexer -v 2>&1 | head -10
echo "Exit: $?"
"""),

    ("Check AI model files exist", r"""
echo "=== 4. AI 模型文件检查 ==="
echo "--- /Agent/data 目录 ---"
ls -lh /Agent/data/ 2>/dev/null | head -20
echo ""
echo "--- /Agent/cmd 目录 ---"
ls -lh /Agent/cmd/ 2>/dev/null | head -20
echo ""
echo "--- 查找 .pb 模型文件 ---"
find /Agent -name "*.pb" -type f 2>/dev/null | head -10
find /root/SOC -name "*.pb" -type f 2>/dev/null | grep -v "pb.h\|pb.cc" | head -10
"""),

    ("Check config for AI filter enable", r"""
echo "=== 5. 配置文件检查 ==="
echo "--- /Agent 配置 ---"
find /Agent -name "*.ini" -o -name "*.conf" -o -name "*.cfg" 2>/dev/null | head -10
echo ""
echo "--- 检查 ly_agent 配置 ---"
cat /etc/cron.d/ly_agent 2>/dev/null
echo ""
echo "--- 查找 ai 相关配置 ---"
grep -rn -i "ai_filter\|dga\|dnstun\|mining\|threat" /Agent/*.ini /Agent/**/*.ini 2>/dev/null | head -10
"""),

    ("Check running processes", r"""
echo "=== 6. 运行中的 agent 进程 ==="
ps aux | grep -E "indexer|agent|analyser" | grep -v grep
echo ""
echo "=== 7. systemd 服务 ==="
systemctl list-units --type=service --state=running 2>/dev/null | grep -iE "agent|index|ly" | head -10
"""),

    ("Check logs for errors", r"""
echo "=== 8. 日志检查 ==="
echo "--- /var/log 下 agent 相关 ---"
ls -lh /var/log/*agent* /var/log/*index* /var/log/ly* 2>/dev/null | head -10
echo ""
echo "--- 最近的 agent 日志尾部 ---"
find /var/log -name "*agent*" -o -name "*index*" 2>/dev/null | head -5 | while read f; do
    echo ">>> $f"
    tail -20 "$f" 2>/dev/null
done
"""),

    ("Check AI filter symbols in indexer", r"""
echo "=== 9. indexer 中的 AI 过滤器符号 ==="
nm /Agent/bin/indexer 2>/dev/null | grep -iE "DgaFilter|DnstunAI|MiningFilter|ThreatFilter|CreateSession" | head -20
echo ""
echo "=== 10. 模型加载路径检查（源码） ==="
grep -rn "ReadBinaryProto\|\.pb" /root/SOC/ly_analyser_src/agent/flow/dga_filter.cpp /root/SOC/ly_analyser_src/agent/flow/dnstun_ai_filter.cpp 2>/dev/null | head -10
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err and 'warning' not in err.lower():
        print(f"STDERR: {err[:1500]}")

client.close()
print("\nDone")
