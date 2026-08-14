import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Compile fb.o and rebuild", r"""
echo "=== 1. 编译 fb.o ==="
cd /root/tsensor
gcc -DHAVE_CONFIG_H -I. -I. -I/usr/include/mysql -I/usr/include/mysql/mysql -I/usr/local/include -I/opt/local/include -g -O2 -pipe -c fb.c -o fb.o
echo "fb.o: $?"
ls -la fb.o
echo ""
echo "=== 2. make 重新构建 ==="
make 2>&1 | tail -10
echo "Make exit: $?"
"""),

    ("Install and restart", r"""
echo "=== 3. make install ==="
cd /root/tsensor
make install 2>&1 | tail -10
echo ""
echo "=== 4. 验证 ==="
ls -la /usr/local/lib/liblyprobe-1.0.0.so /usr/local/bin/tsensor
echo ""
echo "=== 5. 重启 tsensor ==="
systemctl restart tsensor
sleep 3
systemctl status tsensor 2>&1 | head -6
echo ""
ps aux | grep "[t]sensor" | head -1 | cut -c1-100
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
