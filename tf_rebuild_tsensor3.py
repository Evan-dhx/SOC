import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Fix version.o and full build", r"""
echo "=== 1. 检查 version.c ==="
ls -la /root/tsensor/version.c /root/tsensor/.libs/version.o 2>&1
echo ""
echo "=== 2. 编译 version.o ==="
cd /root/tsensor
gcc -DHAVE_CONFIG_H -I. -I. -I/usr/include/mysql -I/usr/include/mysql/mysql -I/usr/local/include -I/opt/local/include -g -O2 -pipe -c version.c -o version.o
echo "version.o: $?"
echo ""
echo "=== 3. make（完整） ==="
make 2>&1 | tail -8
echo "Make exit: $?"
"""),

    ("Install all", r"""
echo "=== 4. make install ==="
cd /root/tsensor
make install 2>&1 | tail -12
echo ""
echo "=== 5. 验证安装时间 ==="
ls -la /usr/local/lib/liblyprobe-1.0.0.so /usr/local/bin/tsensor
echo ""
echo "=== 6. 检查 .so 中的新常量 ==="
strings /usr/local/lib/liblyprobe-1.0.0.so | grep -E "^8192$|flowBuffer" | head -3
echo ""
echo "=== 7. 重启 tsensor ==="
systemctl restart tsensor
sleep 3
systemctl status tsensor 2>&1 | head -6
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
