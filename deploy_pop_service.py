import paramiko
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HOST = '10.10.102.220'
USER = 'root'
PASS = 'PP@ssw0rd'

LOCAL_FILE = r'd:\QorderProject\SOC\ly_analyser\ti\init\pop_service'
REMOTE_FILE = '/Agent/data/pop_service'

print("=" * 60)
print("部署 pop_service 文件")
print("=" * 60)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=30)
print("连接成功!")

# 上传文件
local_size = os.path.getsize(LOCAL_FILE)
print(f"\n上传: {LOCAL_FILE} ({local_size} bytes) -> {REMOTE_FILE}")

sftp = client.open_sftp()
sftp.put(LOCAL_FILE, REMOTE_FILE)
remote_stat = sftp.stat(REMOTE_FILE)
remote_size = remote_stat.st_size
sftp.close()

status = "OK" if remote_size == local_size else "SIZE MISMATCH!"
print(f"远程文件大小: {remote_size} bytes [{status}]")

# 验证文件内容
stdin, stdout, stderr = client.exec_command(f'cat {REMOTE_FILE}')
print(f"\n文件内容:")
print(stdout.read().decode('utf-8', errors='replace'))

# 等待 indexer 下一轮运行，然后检查 syslog
print("\n等待 indexer 下一轮运行 (90秒)...")
time.sleep(90)

# 检查 syslog 中是否还有 pop_service 报错
stdin, stdout, stderr = client.exec_command(
    'journalctl -t indexer --no-pager --since "1 min ago" 2>/dev/null | grep -i "pop_service\\|pop\\|no entry" | tail -10'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== 最近1分钟 syslog 中的 pop_service 日志 ===')
print(out if out.strip() else '(无 pop_service 相关日志)')

# 检查最新 TSDB 文件是否有 pop 相关的
stdin, stdout, stderr = client.exec_command(
    'ls -lt /Agent/data/db/20260813/ 2>/dev/null | head -20'
)
print('\=== 最新 TSDB 文件 ===')
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
print("\n部署完成!")
