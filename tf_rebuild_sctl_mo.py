import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重编译 sctl/mo + 同步 libcommon", r"""
cd /root/SOC/ly_server_src/server
echo "=== 1. 备份旧二进制 ==="
cp /Server/www/d/sctl /Server/www/d/sctl.bak_old 2>/dev/null
cp /Server/www/d/mo /Server/www/d/mo.bak_old 2>/dev/null
echo ""
echo "=== 2. 重编译 sctl ==="
make sctl 2>&1 | tail -5
echo ""
echo "=== 3. 检查 sctl 符号（应为 Impl_ 新版） ==="
nm -u sctl 2>/dev/null | grep -c "Impl_" || echo "0"
nm -u sctl 2>/dev/null | grep "give_permission" | head -3
echo ""
echo "=== 4. 重编译 mo ==="
make mo 2>&1 | tail -5
echo ""
echo "=== 5. 同步 libcommon 副本 ==="
cp /lib64/libcommon.so /root/SOC/ly_server_src/common/libcommon.so
cp /lib64/libcommon.so /home/Server/lib/libcommon.so
cp /lib64/libcommon.so /home/Agent/lib/libcommon.so
echo "同步完成"
md5sum /root/SOC/ly_server_src/common/libcommon.so /home/Server/lib/libcommon.so /home/Agent/lib/libcommon.so
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
