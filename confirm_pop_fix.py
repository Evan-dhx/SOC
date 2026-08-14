import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 检查 16:34 之后是否还有 pop_service 报错
stdin, stdout, stderr = c.exec_command(
    'journalctl -t indexer --no-pager --since "16:34" 2>/dev/null | grep -i "pop_service\\|no entry.*pop" | tail -10'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== 16:34 之后的 pop_service 报错 ===')
print(out if out.strip() else '(无 pop_service 报错 - 修复确认成功!)')

# 检查 16:34 之后的完整 indexer 日志
stdin, stdout, stderr = c.exec_command(
    'journalctl -t indexer --no-pager --since "16:34" 2>/dev/null | head -40'
)
print('\n=== 16:34 之后的 indexer 完整日志 (前40行) ===')
print(stdout.read().decode('utf-8', errors='replace'))

c.close()
