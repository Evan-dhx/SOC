import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config_pusher 链接的 libcommon 排查", r"""
echo "=== 1. ldd config_pusher ==="
ldd /home/Server/bin/config_pusher 2>/dev/null | grep -E "common|proto"
echo ""
echo "=== 2. ly_server_src/common 的 libcommon ==="
ls -la /root/SOC/ly_server_src/common/libcommon.* 2>/dev/null
echo ""
echo "=== 3. /lib64 的 libcommon ==="
ls -la /lib64/libcommon.so 2>/dev/null
echo ""
echo "=== 4. 对比新旧（md5） ==="
md5sum /root/SOC/ly_server_src/common/libcommon.so /lib64/libcommon.so /root/SOC/ly_analyser_src/common/libcommon.so 2>/dev/null
echo ""
echo "=== 5. 服务器 ly_server common 的 config.pb.o 时间 ==="
ls -la /root/SOC/ly_server_src/common/config.pb.* 2>/dev/null | head -3
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:500]}")

client.close()