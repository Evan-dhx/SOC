"""
lyprobe → tsensor 重命名：服務器端
"""
import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("lyprobe → tsensor 重命名 (服務器端)")
print("=" * 60)

# 步驟1: 停止服務
print("\n[1] 停止 lyprobe 服務...")
stdin, stdout, stderr = client.exec_command("systemctl stop lyprobe.service 2>/dev/null; pkill lyprobe 2>/dev/null; sleep 1", timeout=15)
stdout.read()
print("  已停止")

# 步驟2: 重命名二進制文件
print("[2] 重命名二進制文件...")
stdin, stdout, stderr = client.exec_command("""
# 重命名二進制
mv /usr/local/bin/lyprobe /usr/local/bin/tsensor
# 創建向後兼容的符號鏈接
ln -sf tsensor /usr/local/bin/lyprobe
ls -la /usr/local/bin/tsensor /usr/local/bin/lyprobe
""", timeout=10)
print(stdout.read().decode('utf-8', errors='replace'))

# 步驟3: 重命名庫目錄
print("[3] 重命名庫目錄...")
stdin, stdout, stderr = client.exec_command("""
# 重命名庫目錄
mv /usr/local/lib/lyprobe /usr/local/lib/tsensor
# 創建向後兼容的符號鏈接
ln -sf tsensor /usr/local/lib/lyprobe
ls -la /usr/local/lib/ | grep -E 'tsensor|lyprobe'
""", timeout=10)
print(stdout.read().decode('utf-8', errors='replace'))

# 步驟4: 重命名源碼目錄
print("[4] 重命名源碼目錄...")
stdin, stdout, stderr = client.exec_command("""
mv /root/ly_probe /root/tsensor
ln -sf tsensor /root/ly_probe
ls -la /root/ | grep -E 'tsensor|ly_probe'
""", timeout=10)
print(stdout.read().decode('utf-8', errors='replace'))

# 步驟5: 刪除舊服務文件，創建新的
print("[5] 創建 tsensor.service...")

service_content = r"""[Unit]
Description=tsensor NetFlow Probe with Application Layer Parsing
Documentation=https://github.com/Abyssal-Fish-Technology/ly_probe
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/tsensor -i ens192 -n 127.0.0.1:9995 -T "%%IN_SRC_MAC %%OUT_DST_MAC %%IPV4_SRC_ADDR %%IPV4_DST_ADDR %%PROTOCOL %%L4_SRC_PORT %%L4_DST_PORT %%TCP_FLAGS %%SRC_TOS %%IN_PKTS %%IN_BYTES %%FIRST_SWITCHED %%LAST_SWITCHED %%DNS_REQ_DOMAIN %%DNS_REQ_TYPE %%DNS_RES_IP %%HTTP_URL %%HTTP_REQ_METHOD %%HTTP_HOST %%HTTP_MIME %%HTTP_RET_CODE %%HTTP_USER_AGENT %%HTTP_COOKIE %%ICMP_DATA %%ICMP_SEQ_NUM %%ICMP_PAYLOAD_LEN %%SRV_TYPE %%SRV_NAME %%SRV_VERS %%DEV_TYPE %%DEV_NAME %%DEV_VEND %%DEV_VERS %%OS_TYPE %%OS_NAME %%OS_VERS %%THREAT_TYPE %%THREAT_NAME %%THREAT_VERS %%THREAT_TIME %%SIP_CALL_ID %%SIP_CALLING_PARTY %%SIP_CALLED_PARTY %%SIP_RTP_CODECS %%SIP_INVITE_TIME %%SIP_TRYING_TIME %%SIP_RINGING_TIME %%SIP_OK_TIME %%SIP_BYE_TIME %%SIP_RTP_SRC_IP %%SIP_RTP_SRC_PORT %%SIP_RTP_DST_IP %%SIP_RTP_DST_PORT %%RTP_FIRST_SSRC %%RTP_FIRST_TS %%RTP_LAST_SSRC %%RTP_LAST_TS %%RTP_IN_JITTER %%RTP_OUT_JITTER %%RTP_IN_PKT_LOST %%RTP_OUT_PKT_LOST %%RTP_OUT_PAYLOAD_TYPE %%SMTP_MAIL_FROM %%SMTP_RCPT_TO %%FLOW_ID" -e 0 -w 32768
WorkingDirectory=/usr/local/lib/tsensor
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tsensor

[Install]
WantedBy=multi-user.target
"""

sftp = client.open_sftp()
# 刪除舊服務
try:
    sftp.remove('/etc/systemd/system/lyprobe.service')
    print("  已刪除 lyprobe.service")
except:
    pass

# 寫入新服務
with sftp.open('/etc/systemd/system/tsensor.service', 'w') as f:
    f.write(service_content)
sftp.close()
print("  已創建 tsensor.service")

# 步驟6: 啟用並啟動
print("[6] 啟用並啟動 tsensor 服務...")
cmds = [
    "systemctl daemon-reload",
    "systemctl disable lyprobe.service 2>/dev/null",
    "systemctl enable tsensor.service",
    "systemctl start tsensor.service",
    "sleep 3",
]
for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    stdout.read()

# 步驟7: 驗證
print("[7] 驗證...")
stdin, stdout, stderr = client.exec_command("""
echo "=== 服務狀態 ==="
systemctl status tsensor.service --no-pager | head -15

echo ""
echo "=== 進程驗證 ==="
ps -ef | grep tsensor | grep -v grep

echo ""
echo "=== 向後兼容測試 ==="
which lyprobe
which tsensor
lyprobe --help 2>&1 | head -2

echo ""
echo "=== 插件加載 ==="
journalctl -u tsensor --no-pager -n 10 | grep -E 'plugin|enabled'
""", timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()

print("\n" + "=" * 60)
print("服務器端重命名完成!")
print("=" * 60)
