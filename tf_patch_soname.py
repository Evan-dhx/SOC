import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Patch SONAME to libprotobuf.so.19", r"""
echo "=== 检查 patchelf ==="
which patchelf || yum install -y patchelf 2>&1 | tail -3
echo ""
echo "=== 修改 SONAME ==="
cd /usr/local/lib
cp libprotobuf.so.19.0.0 libprotobuf.so.19.0.0.patched
patchelf --set-soname libprotobuf.so.19 libprotobuf.so.19.0.0.patched
echo "patchelf exit: $?"
mv -f libprotobuf.so.19.0.0.patched libprotobuf.so.19.0.0
ln -sf libprotobuf.so.19.0.0 libprotobuf.so.19
ldconfig
echo ""
echo "=== 验证 SONAME ==="
readelf -d /usr/local/lib/libprotobuf.so.19.0.0 | grep SONAME
echo ""
echo "=== 验证符号 ==="
nm -D /usr/local/lib/libprotobuf.so.19 | grep "CopyWithSourceCheck" | head -2
"""),

    ("Test extractor again", r"""
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
