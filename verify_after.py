import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 1. 查看最新的 TSDB 文件
stdin, stdout, stderr = c.exec_command(
    'ls -lt /Agent/data/db/20260813/ 2>/dev/null'
)
print('=== /Agent/data/db/20260813/ TSDB 文件 (最新) ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 2. 查看 eventdb
stdin, stdout, stderr = c.exec_command(
    'find /Agent/data/eventdb/ -type f 2>/dev/null | head -20'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== 事件数据库文件 ===')
print(out if out.strip() else '(无事件数据)')

# 3. 搜索 indexer 日志中的 sus/no entry/ip set 相关信息
stdin, stdout, stderr = c.exec_command(
    'grep -i "sus\\|no entry\\|ip set\\|Could not load\\|unfiltered" /data/log/indexer.log 2>/dev/null | tail -30'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== Indexer 威胁情报相关日志 ===')
print(out if out.strip() else '(无威胁情报相关日志)')

# 4. 查看最新 indexer 日志（排除 TF 噪音）
stdin, stdout, stderr = c.exec_command(
    'grep -v "tensorflow\\|oneDNN\\|MLIR" /data/log/indexer.log 2>/dev/null | tail -20'
)
print('=== Indexer 业务日志 (最新20行) ===')
print(stdout.read().decode('utf-8', errors='replace'))

c.close()
