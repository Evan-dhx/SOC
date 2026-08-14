import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Replace libprotobuf.so.19 with 3.21.9", r"""
echo "=== 替换 libprotobuf.so.19 ==="
cd /tmp/protobuf_build
echo "--- 找到旧库位置 ---"
ls -la /usr/local/lib/libprotobuf.so* 2>/dev/null
echo ""
echo "--- 备份并覆盖 ---"
cp /usr/local/lib/libprotobuf.so.19.0.0 /usr/local/lib/libprotobuf.so.19.0.0.bak.old 2>/dev/null
cp libprotobuf.so.3.21.9.0 /usr/local/lib/libprotobuf.so.19.0.0
ln -sf libprotobuf.so.19.0.0 /usr/local/lib/libprotobuf.so.19
ldconfig
echo ""
echo "--- 验证 ---"
ldconfig -p | grep "libprotobuf.so.19"
ls -la /usr/local/lib/libprotobuf.so.19*
echo ""
echo "--- 检查符号 ---"
nm -D /usr/local/lib/libprotobuf.so.19 | grep "CopyWithSourceCheck" | head -2
echo ""
echo "--- 检查版本字符串 ---"
strings /usr/local/lib/libprotobuf.so.19 | grep -E "^3\.21\.9" | head -3
"""),

    ("Test extractor now", r"""
echo "=== 测试 extractor ==="
cd /Agent/bin
now=$(date +"%s")
aligned=$[$now-$now%300-300]
timeout 30 sudo -u apache ./extractor -v 1 -t $aligned -i ./indexer 2>&1 | head -40
echo "Exit: $?"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
