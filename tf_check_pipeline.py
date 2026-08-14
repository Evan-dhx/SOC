import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check port 9995 listener", r"""
echo "=== 1. 9995 端口监听状态 ==="
ss -tlnup | grep -E "9995|:9[0-9]{3}" 
echo ""
echo "=== 2. 所有 agent 相关进程 ==="
ps aux | grep -E "indexer|flow_scan|actl|extract|output" | grep -v grep | head -20
echo ""
echo "=== 3. indexer 是否在运行 ==="
pidof indexer && echo "indexer RUNNING" || echo "indexer NOT RUNNING"
echo ""
echo "=== 4. 9995 是谁的端口（全端口列表） ==="
ss -tlnp 2>/dev/null | head -30
"""),

    ("Check web service and DB", r"""
echo "=== 5. web 服务进程 ==="
ps aux | grep -iE "nginx|httpd|apache|node|python.*server|ly_server|ly_vis" | grep -v grep | head -10
echo ""
echo "=== 6. 数据库进程 ==="
ps aux | grep -iE "mysql|mariadb|unqlite|cppdb" | grep -v grep | head -5
echo ""
echo "=== 7. ly_server 是否部署 ==="
ls -la /Agent/bin/ 2>/dev/null | head -20
echo ""
echo "=== 8. web 端口 ==="
ss -tlnp 2>/dev/null | grep -E ":80 |:8080|:443|:9999|:9000" | head -10
"""),

    ("Check data flow pipeline config", r"""
echo "=== 9. 查找流量采集配置 ==="
find /Agent -name "*.ini" -type f 2>/dev/null | head -10
find /Agent -name "*.conf" -type f 2>/dev/null | head -10
echo ""
echo "=== 10. flow_scan 相关 ==="
ls -la /Agent/cmd/flow_scan
echo ""
echo "=== 11. 9995 相关配置 ==="
grep -rn "9995" /Agent/ 2>/dev/null | head -10
grep -rn "9995" /root/SOC/ly_analyser_src/ 2>/dev/null | grep -v "\.o:" | head -10
"""),

    ("Check log for recent activity", r"""
echo "=== 12. /Agent 下的日志 ==="
find /Agent -name "*.log" -type f 2>/dev/null | head -10
echo ""
echo "=== 13. 检查 agent 日志 ==="
ls -la /Agent/log/ 2>/dev/null | head -20
echo ""
echo "=== 14. 最近日志尾部 ==="
for f in /Agent/log/*.log; do
    [ -f "$f" ] && echo ">>> $f" && tail -15 "$f"
done
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
