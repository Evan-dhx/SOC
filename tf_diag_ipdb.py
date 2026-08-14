import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("define.h + IP 库问题", r"""
echo "=== 1. define.h 路径定义 ==="
cat /root/SOC/ly_server_src/server/define.h
echo ""
echo "=== 2. locinfo ipip_file 从哪里来 ==="
grep -n "ipip_file\|ipip\." /root/SOC/ly_server_src/server/locinfo.cpp | head -10
echo ""
echo "=== 3. geoinfo ipdb_file 实际路径 ==="
readelf -p .rodata /Server/www/d/geoinfo 2>/dev/null | grep -i "data\|ip_data\|geo" | head -5
strings /Server/www/d/geoinfo 2>/dev/null | grep -i "data\|geo" | head -5
echo ""
echo "=== 4. locinfo 崩溃原因（strace 近似） ==="
gdb -batch -ex "run" -ex "bt" --args /Server/www/d/locinfo 2>&1 <<'EOF' | head -20
echo "locinfo" | timeout 10
EOF
echo ""
echo "=== 5. 检查 locinfo 是否用旧 protobuf 编译 ==="
nm -u /Server/www/d/locinfo 2>/dev/null | grep -c "protobuf" || echo "0 protobuf refs"
ls -la /Server/www/d/topn 2>/dev/null || echo "topn 不存在"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()