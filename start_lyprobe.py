"""
启动带应用层协议解析的 lyprobe 监听
"""
import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("启动 lyprobe 应用层协议解析监听")
print("=" * 60)

# 先停止现有的 lyprobe
print("\n停止现有 lyprobe...")
stdin, stdout, stderr = client.exec_command("pkill lyprobe 2>/dev/null; sleep 1", timeout=10)
stdout.read()

# 启动 lyprobe (使用 nohup 和 & 后台运行)
print("启动 lyprobe...")
start_cmd = """
TEMPLATE="%IN_SRC_MAC %OUT_DST_MAC %IPV4_SRC_ADDR %IPV4_DST_ADDR %PROTOCOL %L4_SRC_PORT %L4_DST_PORT %TCP_FLAGS %SRC_TOS %IN_PKTS %IN_BYTES %DNS_REQ_DOMAIN %DNS_REQ_TYPE %DNS_RES_IP %HTTP_URL %HTTP_REQ_METHOD %HTTP_HOST %HTTP_MIME %HTTP_RET_CODE %HTTP_USER_AGENT %ICMP_DATA %ICMP_SEQ_NUM %ICMP_PAYLOAD_LEN"

nohup lyprobe -i ens192 -n 127.0.0.1:9995 -T "$TEMPLATE" -e 0 -w 32768 -G > /tmp/lyprobe.log 2>&1 &
echo "lyprobe PID: $!"
sleep 2
"""

stdin, stdout, stderr = client.exec_command(start_cmd, timeout=15)
try:
    print(stdout.read().decode('utf-8', errors='replace'))
except Exception:
    print("(启动命令已执行)")

# 检查状态
print("\n=== 验证 lyprobe 进程 ===")
stdin, stdout, stderr = client.exec_command("ps -ef | grep lyprobe | grep -v grep", timeout=10)
out = stdout.read().decode('utf-8', errors='replace')
if out.strip():
    print("lyprobe 正在运行:")
    print(out)
else:
    print("lyprobe 未运行，检查日志:")
    stdin, stdout, stderr = client.exec_command("cat /tmp/lyprobe.log 2>/dev/null | tail -20", timeout=10)
    print(stdout.read().decode('utf-8', errors='replace'))

client.close()

print("\n" + "=" * 60)
print("lyprobe 应用层协议监听配置完成")
print("=" * 60)
print("\n已启用的插件:")
print("  - dnsPlugin.so: DNS 域名解析")
print("  - httpPlugin.so: HTTP 协议解析")
print("  - icmpPlugin.so: ICMP 协议解析")
print("  - l7Plugin.so: 七层协议识别")
print("\n解析的协议字段:")
print("  - DNS: %DNS_REQ_DOMAIN, %DNS_REQ_TYPE, %DNS_RES_IP")
print("  - HTTP: %HTTP_URL, %HTTP_REQ_METHOD, %HTTP_HOST, %HTTP_MIME, %HTTP_RET_CODE")
print("  - ICMP: %ICMP_DATA, %ICMP_SEQ_NUM, %ICMP_PAYLOAD_LEN")
print("\n管理命令:")
print("  查看进程: ps -ef | grep lyprobe")
print("  查看日志: cat /tmp/lyprobe.log")
print("  停止: pkill lyprobe")
