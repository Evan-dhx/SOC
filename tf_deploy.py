import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("部署二进制 + tsensor.conf + 启动脚本", r"""
set -e
echo "=== 1. 备份并部署二进制 ==="
TS=$(date +%H%M%S)
cp /home/Server/lib/config_agent.so /home/Server/lib/config_agent.so.bak_$TS
cp /home/Server/bin/config_pusher /home/Server/bin/config_pusher.bak_$TS
cp /home/Agent/cmd/actl /home/Agent/cmd/actl.bak_$TS 2>/dev/null || true
cp /home/Agent/bin/fsd /home/Agent/bin/fsd.bak_$TS 2>/dev/null || true
cp /root/SOC/ly_server_src/lib/config_agent.so /home/Server/lib/config_agent.so
cp /root/SOC/ly_server_src/server/config_pusher /home/Server/bin/config_pusher
cp /root/SOC/ly_analyser_src/agent/handlers/actl /home/Agent/cmd/actl
cp /root/SOC/ly_analyser_src/agent/handlers/fsd /home/Agent/bin/fsd
cp /root/SOC/ly_analyser_src/nftls/nftls /home/Agent/bin/nftls
chmod 755 /home/Agent/bin/nftls
echo "部署完成:"
ls -la /home/Server/lib/config_agent.so /home/Server/bin/config_pusher /home/Agent/cmd/actl /home/Agent/bin/fsd /home/Agent/bin/nftls
echo ""
echo "=== 2. 创建 tsensor.conf（配置文件，支持 psk） ==="
cat > /Agent/etc/tsensor.conf <<'EOF'
# tsensor 探针配置文件
# interface: 采集网卡
# collector: NetFlow 发送目标 (127.0.0.1:9996 = 本机 nftls 加密代理端口)
# template: 流量元数据模板
# pcap_level: 数据包留存级别 0-3
# filter: BPF 过滤
# psk: TLS 加密传输预共享密钥（留空 = 明文直连 nfcapd）
interface=ens192
collector=127.0.0.1:9996
template=%IN_SRC_MAC %OUT_DST_MAC %IPV4_SRC_ADDR %IPV4_DST_ADDR %PROTOCOL %L4_SRC_PORT %L4_DST_PORT %TCP_FLAGS %SRC_TOS %IN_PKTS %IN_BYTES %FIRST_SWITCHED %LAST_SWITCHED %DNS_REQ_DOMAIN %DNS_REQ_TYPE %DNS_RES_IP %HTTP_URL %HTTP_REQ_METHOD %HTTP_HOST %HTTP_MIME %HTTP_RET_CODE %HTTP_USER_AGENT %HTTP_COOKIE %FLOW_ID
pcap_level=0
filter=
psk=
EOF
chmod 600 /Agent/etc/tsensor.conf
echo ""
echo "=== 3. 创建 tsensor 启动包装脚本（读 tsensor.conf） ==="
cat > /Agent/etc/tsensor_start.sh <<'EOF'
#!/bin/bash
# tsensor 启动包装：读取 /Agent/etc/tsensor.conf
# psk 非空 -> 启动本机 nftls client（UDP 9996 -> TLS 远端 19995+devid），探针发往 127.0.0.1:9996
# psk 为空 -> 明文直连 collector
CONF=/Agent/etc/tsensor.conf
if [ ! -f "$CONF" ]; then
  echo "tsensor.conf not found"
  exit 1
fi
. "$CONF"
CMD="/usr/local/bin/tsensor -i $interface -n $collector -T \"$template\" -e 0 -w 32768"
if [ -n "$psk" ] && [ "$psk" != "none" ]; then
  # 本机加密代理：nftls client 收 UDP 9996 -> TLS 发 127.0.0.1:(19995+devid)
  DEVID=${devid:-1}
  TLS_PORT=$((19995 + DEVID))
  nftls -m client -l 127.0.0.1:9996 -r 127.0.0.1:$TLS_PORT -i "$name" -k "$psk" -d
fi
if [ -n "$filter" ] && [ "$filter" != "none" ]; then
  CMD="$CMD -f \"$filter\""
fi
if [ "$pcap_level" != "0" ] && [ -n "$pcap_level" ]; then
  mkdir -p /data/cap/1
  CMD="$CMD -k $pcap_level -K /data/cap/1"
fi
echo "tsensor start: $CMD"
exec bash -c "$CMD"
EOF
chmod 755 /Agent/etc/tsensor_start.sh
echo ""
echo "=== 4. 修改 tsensor.service 使用包装脚本 ==="
sed -i 's|^ExecStart=.*|ExecStart=/Agent/etc/tsensor_start.sh|' /etc/systemd/system/tsensor.service
grep "ExecStart" /etc/systemd/system/tsensor.service
systemctl daemon-reload
echo ""
echo "=== 5. 启动 fsd（nftls server 生命周期 + 状态守护） ==="
pgrep -f "/home/Agent/bin/fsd" >/dev/null && echo "fsd 已在运行" || (setsid /home/Agent/bin/fsd >/dev/null 2>&1 </dev/null &) >/dev/null 2>&1
sleep 2
pgrep -f "Agent/bin/fsd" >/dev/null && echo "fsd 已启动" || echo "fsd 启动失败"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1200]}")

client.close()