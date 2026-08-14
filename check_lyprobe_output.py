"""
修复 lyprobe systemd 服务 (移除 -G 守护进程模式)
"""
import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("修复 lyprobe systemd 服务")
print("=" * 60)

# 停止服务
print("\n[1] 停止服务...")
stdin, stdout, stderr = client.exec_command("systemctl stop lyprobe.service; pkill lyprobe", timeout=10)
stdout.read()

# 创建修复后的服务文件 - 移除 -G，使用 Type=simple
print("[2] 修复服务文件...")

service_content = """[Unit]
Description=lyprobe NetFlow Probe with Application Layer Parsing
Documentation=https://github.com/Abyssal-Fish-Technology/ly_probe
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
# 注意: 不使用 -G (守护进程模式)，让 lyprobe 在前台运行
ExecStart=/usr/local/bin/lyprobe -i ens192 -n 127.0.0.1:9995 -T "%%IN_SRC_MAC %%OUT_DST_MAC %%IPV4_SRC_ADDR %%IPV4_DST_ADDR %%PROTOCOL %%L4_SRC_PORT %%L4_DST_PORT %%TCP_FLAGS %%SRC_TOS %%IN_PKTS %%IN_BYTES %%DNS_REQ_DOMAIN %%DNS_REQ_TYPE %%DNS_RES_IP %%HTTP_URL %%HTTP_REQ_METHOD %%HTTP_HOST %%HTTP_MIME %%HTTP_RET_CODE %%HTTP_USER_AGENT %%ICMP_DATA %%ICMP_SEQ_NUM %%ICMP_PAYLOAD_LEN" -e 0 -w 32768
WorkingDirectory=/usr/local/lib/lyprobe
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lyprobe

[Install]
WantedBy=multi-user.target
"""

sftp = client.open_sftp()
with sftp.open('/etc/systemd/system/lyprobe.service', 'w') as f:
    f.write(service_content)
sftp.close()
print("  已修复: 移除 -G 参数，使用前台模式")

# 重新加载并启动
print("[3] 重新加载并启动...")
cmds = [
    "systemctl daemon-reload",
    "systemctl enable lyprobe.service",
    "systemctl start lyprobe.service",
    "sleep 3",
]
for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    stdout.read()

# 验证
print("\n[4] 服务状态:")
stdin, stdout, stderr = client.exec_command("systemctl status lyprobe.service --no-pager", timeout=10)
status_out = stdout.read().decode('utf-8', errors='replace')
print(status_out)

print("[5] 进程验证:")
stdin, stdout, stderr = client.exec_command("ps -ef | grep lyprobe | grep -v grep", timeout=10)
out = stdout.read().decode('utf-8', errors='replace')
if out.strip():
    print("  lyprobe 正在运行:")
    for line in out.strip().split('\n'):
        print(f"  {line}")
else:
    print("  lyprobe 未运行")

client.close()

# 判断结果
if "active (running)" in status_out:
    print("\n" + "=" * 60)
    print("lyprobe 自启动配置成功!")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print("lyprobe 服务可能仍在启动中，请稍后检查")
    print("=" * 60)

print("\n服务文件: /etc/systemd/system/lyprobe.service")
print("\n管理命令:")
print("  查看状态: systemctl status lyprobe")
print("  启动:     systemctl start lyprobe")
print("  停止:     systemctl stop lyprobe")
print("  重启:     systemctl restart lyprobe")
print("  查看日志: journalctl -u lyprobe -f")
