import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Rebuild tsensor", r"""
echo "=== 1. make 重新编译 ==="
cd /root/tsensor
make 2>&1 | tail -25
echo ""
echo "Make exit: $?"
"""),

    ("Install", r"""
echo "=== 2. make install ==="
cd /root/tsensor
make install 2>&1 | tail -15
echo ""
echo "=== 3. 验证安装 ==="
ls -la /usr/local/lib/liblyprobe-1.0.0.so /usr/local/bin/tsensor
echo ""
echo "=== 4. 验证新缓冲区（strings 检查） ==="
strings /usr/local/lib/liblyprobe-1.0.0.so | grep -c "flowBuffer" 
echo ""
echo "=== 5. 重启 tsensor ==="
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
