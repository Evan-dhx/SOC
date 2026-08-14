import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 1. 检查 indexer 进程状态
stdin, stdout, stderr = c.exec_command('ps aux | grep indexer | grep -v grep')
print('=== Indexer 进程状态 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 2. 检查 cron 调度
stdin, stdout, stderr = c.exec_command('cat /etc/cron.d/ly_agent 2>/dev/null')
out = stdout.read().decode('utf-8', errors='replace')
print('=== Cron 调度配置 (/etc/cron.d/ly_agent) ===')
print(out if out.strip() else '(不存在)')

# 3. 检查 indexer 最近日志
stdin, stdout, stderr = c.exec_command('ls -lt /Agent/log/ 2>/dev/null | head -10')
print('=== /Agent/log/ 目录 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 4. 查看最近的 indexer 日志
stdin, stdout, stderr = c.exec_command('tail -30 /Agent/log/indexer.log 2>/dev/null')
out = stdout.read().decode('utf-8', errors='replace')
print('=== Indexer 日志 (最后30行) ===')
print(out if out.strip() else '(无 indexer.log)')

# 5. 查看最近的 flow 日志
stdin, stdout, stderr = c.exec_command('tail -30 /Agent/log/flow.log 2>/dev/null')
out = stdout.read().decode('utf-8', errors='replace')
print('=== Flow 日志 (最后30行) ===')
print(out if out.strip() else '(无 flow.log)')

c.close()
