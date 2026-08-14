import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 查看 TSDB 数据库目录内容
stdin, stdout, stderr = c.exec_command(
    'ls -la /Agent/data/db/20260813/ 2>/dev/null'
)
print('=== /Agent/data/db/20260813/ TSDB 文件 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 查看 eventdb 目录
stdin, stdout, stderr = c.exec_command(
    'ls -la /Agent/data/eventdb/ 2>/dev/null; ls -la /Agent/data/eventdb/20260813/ 2>/dev/null'
)
print('=== /Agent/data/eventdb/ 事件数据库 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 查看文件名中包含的特征标签
stdin, stdout, stderr = c.exec_command(
    'ls /Agent/data/db/20260813/ 2>/dev/null | sort'
)
print('=== TSDB 文件名列表 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 查看配置文件了解有哪些过滤器
stdin, stdout, stderr = c.exec_command(
    'cat /Agent/data/config 2>/dev/null | head -50'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== Agent 配置文件 (前50行) ===')
print(out if out.strip() else '(无配置文件)')

c.close()
