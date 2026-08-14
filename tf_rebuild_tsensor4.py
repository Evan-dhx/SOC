import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Fix base64.o and complete build", r"""
echo "=== 1. 编译 base64.o ==="
cd /root/tsensor
gcc -DHAVE_CONFIG_H -I. -I. -I/usr/include/mysql -I/usr/include/mysql/mysql -I/usr/local/include -I/opt/local/include -g -O2 -pipe -c base64.c -o base64.o
echo "base64.o: $?"
echo ""
echo "=== 2. make 完整构建 ==="
make 2>&1 | tail -6
echo "Make exit: $?"
"""),

    ("Install and verify", r"""
echo "=== 3. make install ==="
cd /root/tsensor
make install 2>&1 | tail -8
echo ""
echo "=== 4. 验证安装 ==="
ls -la /usr/local/lib/liblyprobe-1.0.0.so /usr/local/bin/tsensor
echo ""
echo "=== 5. 确认新库已生效（时间戳） ==="
stat -c "%y %n" /usr/local/lib/liblyprobe-1.0.0.so
echo ""
echo "=== 6. 重启 tsensor ==="
systemctl restart tsensor
sleep 3
systemctl status tsensor 2>&1 | head -5
echo ""
echo "=== 7. 确认无崩溃（30 秒后检查） ==="
sleep 30
systemctl is-active tsensor
ps aux | grep "[t]sensor" | head -1 | cut -c1-80
dmesg 2>/dev/null | grep -i "trap.*tsensor" | tail -2
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
