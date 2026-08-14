import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 1. 查看 /Agent/data/ 所有文件
stdin, stdout, stderr = c.exec_command('ls -la /Agent/data/ 2>/dev/null')
print('=== /Agent/data/ 目录 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 2. 查看 indexer_process 文件内容
stdin, stdout, stderr = c.exec_command('cat /Agent/data/indexer_process 2>/dev/null')
out = stdout.read().decode('utf-8', errors='replace')
print('=== indexer_process (过滤器开关) ===')
print(out if out.strip() else '(不存在)')

# 3. 查看 indexer_feature 文件
stdin, stdout, stderr = c.exec_command('cat /Agent/data/indexer_feature 2>/dev/null')
out = stdout.read().decode('utf-8', errors='replace')
print('=== indexer_feature (pattern配置) ===')
print(out if out.strip() else '(不存在)')

# 4. 查看 indexer_cache 文件
stdin, stdout, stderr = c.exec_command('cat /Agent/data/indexer_cache 2>/dev/null')
out = stdout.read().decode('utf-8', errors='replace')
print('=== indexer_cache (缓存配置) ===')
print(out if out.strip() else '(不存在)')

# 5. 查看 /Agent/data/db/ 权限
stdin, stdout, stderr = c.exec_command('ls -la /Agent/data/db/ 2>/dev/null')
print('=== /Agent/data/db/ 权限 ===')
print(stdout.read().decode('utf-8', errors='replace'))

c.close()
