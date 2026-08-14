import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Fix symlink and verify", r"""
echo "=== 修复 libprotobuf.so.19 链接 ==="
cd /usr/local/lib
rm -f libprotobuf.so.19
ln -s libprotobuf.so.19.0.0 libprotobuf.so.19
ls -la /usr/local/lib/libprotobuf.so*
echo ""
echo "=== 验证符号 ==="
nm -D /usr/local/lib/libprotobuf.so.19 | grep "CopyWithSourceCheck" | head -2
echo ""
echo "=== 验证版本 ==="
strings /usr/local/lib/libprotobuf.so.19 | grep -E "^3\.21\.9" | head -3
ldconfig
ldconfig -p | grep "libprotobuf.so.19"
"""),

    ("Test extractor after fix", r"""
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
