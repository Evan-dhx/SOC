import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Simplify tsensor template", r"""
echo "=== 1. 备份原 service ==="
cp /etc/systemd/system/tsensor.service /etc/systemd/system/tsensor.service.bak_fulltemplate

echo "=== 2. 精简 -T 模板 ==="
# 保留核心 NetFlow + DNS（AI 检测需要）+ HTTP（URL 检测需要）
cat > /etc/systemd/system/tsensor.service << 'EOF'
[Unit]
Description=tsensor NetFlow Probe with Application Layer Parsing
Documentation=https://github.com/Abyssal-Fish-Technology/ly_probe
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/tsensor -i ens192 -n 127.0.0.1:9995 -T "%%IN_SRC_MAC %%OUT_DST_MAC %%IPV4_SRC_ADDR %%IPV4_DST_ADDR %%PROTOCOL %%L4_SRC_PORT %%L4_DST_PORT %%TCP_FLAGS %%SRC_TOS %%IN_PKTS %%IN_BYTES %%FIRST_SWITCHED %%LAST_SWITCHED %%DNS_REQ_DOMAIN %%DNS_REQ_TYPE %%DNS_RES_IP %%HTTP_URL %%HTTP_REQ_METHOD %%HTTP_HOST %%HTTP_MIME %%HTTP_RET_CODE %%HTTP_USER_AGENT %%HTTP_COOKIE %%FLOW_ID" -e 0 -w 32768
WorkingDirectory=/usr/local/lib/tsensor
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tsensor

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
echo "Service 已更新"

echo "=== 3. 重启 tsensor ==="
systemctl restart tsensor
sleep 3
systemctl status tsensor 2>&1 | head -5
echo ""
echo "=== 4. 新进程确认 ==="
ps aux | grep "[t]sensor" | head -1 | cut -c1-120
"""),

    ("Verify template smaller", r"""
echo "=== 5. 验证 nfcapd 是否解析成功 ==="
# 等待导出周期
sleep 35
echo "--- nfcapd 最近日志 ---"
journalctl --no-pager --since '1 minute ago' 2>/dev/null | grep -iE "nfcapd|flowset|Process_v9" | tail -10
echo ""
echo "--- nfcapd.current 大小 ---"
stat -c "%s bytes %y" /data/flow/nfcapd.current
ls -la /data/flow/ | tail -4
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
