import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 1. 确认文件存在
stdin, stdout, stderr = c.exec_command(
    'ls -la /Agent/data/pop_service 2>&1'
)
print('=== /Agent/data/pop_service 文件 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 2. 查看最近5分钟 syslog 中的 pop 相关日志
stdin, stdout, stderr = c.exec_command(
    'journalctl -t indexer --no-pager --since "5 min ago" 2>/dev/null | grep -i "pop\\|no entry" | tail -20'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== 最近5分钟 syslog pop/no entry 日志 ===')
print(out if out.strip() else '(无 pop_service 报错 - 修复成功!)')

# 3. 对比之前的报错（查看部署前的日志）
stdin, stdout, stderr = c.exec_command(
    'journalctl -t indexer --no-pager --since "10 min ago" 2>/dev/null | grep -i "pop_service\\|no entry" | tail -10'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== 最近10分钟 syslog pop_service/no entry 日志 (含部署前) ===')
print(out if out.strip() else '(无相关日志)')

# 4. 查看最新 syslog 中 indexer 的完整日志
stdin, stdout, stderr = c.exec_command(
    'journalctl -t indexer --no-pager -n 20 2>/dev/null'
)
print('=== Indexer 最近20条 syslog ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 5. 查看 TSDB 文件
stdin, stdout, stderr = c.exec_command(
    'ls -lt /Agent/data/db/20260813/ 2>/dev/null'
)
print('=== TSDB 文件 ===')
print(stdout.read().decode('utf-8', errors='replace'))

c.close()
