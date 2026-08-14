import paramiko
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HOST = '10.10.102.220'
USER = 'root'
PASS = 'PP@ssw0rd'

print("=" * 60)
print("部署 indexer_feature + indexer_cache + 修复权限")
print("=" * 60)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=30)
print("连接成功!\n")

# ===== 1. 上传 indexer_feature =====
local_feat = r'd:\QorderProject\SOC\ly_analyser\ti\init\indexer_feature'
remote_feat = '/Agent/data/indexer_feature'
local_size = os.path.getsize(local_feat)
print(f"[1/4] 上传 indexer_feature ({local_size} bytes)")
sftp = client.open_sftp()
sftp.put(local_feat, remote_feat)
remote_stat = sftp.stat(remote_feat)
status = "OK" if remote_stat.st_size == local_size else "SIZE MISMATCH!"
print(f"  远程大小: {remote_stat.st_size} bytes [{status}]")

# 验证内容
stdin, stdout, stderr = client.exec_command(f'cat {remote_feat}')
print("  内容:")
for line in stdout.read().decode('utf-8', errors='replace').strip().split('\n'):
    print(f"    {line}")

# ===== 2. 上传 indexer_cache =====
local_cache = r'd:\QorderProject\SOC\ly_analyser\ti\init\indexer_cache'
remote_cache = '/Agent/data/indexer_cache'
local_size = os.path.getsize(local_cache)
print(f"\n[2/4] 上传 indexer_cache ({local_size} bytes)")
sftp.put(local_cache, remote_cache)
remote_stat = sftp.stat(remote_cache)
status = "OK" if remote_stat.st_size == local_size else "SIZE MISMATCH!"
print(f"  远程大小: {remote_stat.st_size} bytes [{status}]")

# ===== 3. 修复目录权限 =====
print(f"\n[3/4] 修复目录权限")

# /Agent/data/db/ - apache 用户需要写入
stdin, stdout, stderr = client.exec_command('ls -ld /Agent/data/db/')
print(f"  修复前 db/: {stdout.read().decode().strip()}")

client.exec_command('chown -R apache:apache /Agent/data/db/')
client.exec_command('chmod -R 777 /Agent/data/db/')
time.sleep(1)

stdin, stdout, stderr = client.exec_command('ls -ld /Agent/data/db/')
print(f"  修复后 db/: {stdout.read().decode().strip()}")

# /Agent/data/eventdb/ - apache 用户需要写入
client.exec_command('mkdir -p /Agent/data/eventdb/')
client.exec_command('chown -R apache:apache /Agent/data/eventdb/')
client.exec_command('chmod -R 777 /Agent/data/eventdb/')

stdin, stdout, stderr = client.exec_command('ls -ld /Agent/data/eventdb/')
print(f"  eventdb/: {stdout.read().decode().strip()}")

# 确保 /Agent/data/ 本身可写
client.exec_command('chmod 777 /Agent/data/')

sftp.close()

# ===== 4. 等待 indexer 运行并验证 =====
print(f"\n[4/4] 等待 indexer 下一轮运行 (90秒)...")
time.sleep(90)

print("\n=== 验证 syslog 中的报错 ===")

# 检查 indexer_feature 报错
stdin, stdout, stderr = client.exec_command(
    'journalctl -t indexer --no-pager --since "2 min ago" 2>/dev/null | grep -i "pattern config\\|indexer_feature" | tail -5'
)
out = stdout.read().decode('utf-8', errors='replace')
print(f"indexer_feature 报错: {out.strip() if out.strip() else '(无报错 - 修复成功!)'}")

# 检查 indexer_cache 报错
stdin, stdout, stderr = client.exec_command(
    'journalctl -t indexer --no-pager --since "2 min ago" 2>/dev/null | grep -i "cache config\\|indexer_cache" | tail -5'
)
out = stdout.read().decode('utf-8', errors='replace')
print(f"indexer_cache 报错: {out.strip() if out.strip() else '(无报错 - 修复成功!)'}")

# 检查权限报错
stdin, stdout, stderr = client.exec_command(
    'journalctl -t indexer --no-pager --since "2 min ago" 2>/dev/null | grep -i "Permission denied\\|Could not create" | tail -5'
)
out = stdout.read().decode('utf-8', errors='replace')
print(f"权限报错: {out.strip() if out.strip() else '(无报错 - 修复成功!)'}")

# 检查 pop_service 报错
stdin, stdout, stderr = client.exec_command(
    'journalctl -t indexer --no-pager --since "2 min ago" 2>/dev/null | grep -i "pop_service\\|no entry" | tail -5'
)
out = stdout.read().decode('utf-8', errors='replace')
print(f"pop_service 报错: {out.strip() if out.strip() else '(无报错 - 之前已修复!)'}")

# 最近完整的 indexer 日志
print("\n=== Indexer 最近10条 syslog ===")
stdin, stdout, stderr = client.exec_command(
    'journalctl -t indexer --no-pager -n 10 2>/dev/null'
)
print(stdout.read().decode('utf-8', errors='replace'))

# TSDB 文件
print("=== TSDB 最新文件 ===")
stdin, stdout, stderr = client.exec_command(
    'ls -lt /Agent/data/db/20260813/ 2>/dev/null | head -15'
)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
print("\n部署和修复完成!")
