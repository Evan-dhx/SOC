import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("重新部署 + pusher 验证", r"""
echo "=== 1. 部署新二进制 ==="
cp /root/SOC/ly_analyser_src/agent/handlers/actl /home/Agent/cmd/actl
cp /root/SOC/ly_analyser_src/agent/handlers/fsd /home/Agent/bin/fsd
cp /root/SOC/ly_server_src/server/config_pusher /home/Server/bin/config_pusher
echo "部署 OK"
echo ""
echo "=== 2. 重启 fsd（加载新配置启动 nftls server） ==="
pkill -x fsd 2>/dev/null; sleep 1
(setsid /home/Agent/bin/fsd >/dev/null 2>&1 </dev/null &) >/dev/null 2>&1
sleep 3
pgrep -x fsd >/dev/null && echo "fsd 运行中" || echo "fsd 未运行"
echo ""
echo "=== 3. config_pusher 下发（验证不崩溃） ==="
/home/Server/bin/config_pusher > /tmp/pusher2.log 2>&1
echo "exit=$?"
cat /tmp/pusher2.log | head -5
echo ""
echo "=== 4. agent 配置中的 dev（含 psk） ==="
grep -A8 "dev {" /Agent/data/config | head -12
echo ""
echo "=== 5. fsd 是否启动 nftls server（19996 = 19995+devid1） ==="
sleep 5
ss -tlnp 2>/dev/null | grep 19996 || echo "19996 未监听"
ps aux | grep nftls | grep -v grep | head -3
echo ""
echo "=== 6. nftls.psk 文件 ==="
cat /Agent/etc/nftls.psk 2>/dev/null | sed 's/:.*/:***/'
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=400)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()