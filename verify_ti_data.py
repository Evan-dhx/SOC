import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 1. 查看 TSDB 数据库目录
stdin, stdout, stderr = c.exec_command(
    'ls -la /Agent/data/db/ 2>/dev/null | head -30'
)
print('=== /Agent/data/db/ TSDB 目录 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 2. 查看是否有 sus/black/mining 相关的 TSDB 文件
stdin, stdout, stderr = c.exec_command(
    'find /Agent/data/db/ -name "*sus*" -o -name "*black*" -o -name "*mining*" -o -name "*ip_set*" 2>/dev/null | head -20'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== 威胁相关 TSDB 文件 ===')
print(out if out.strip() else '(未找到威胁相关TSDB文件)')

# 3. 查看 Agent 的 flow 数据目录
stdin, stdout, stderr = c.exec_command(
    'ls -lt /Agent/flow/1/ 2>/dev/null | head -10'
)
print('=== Flow 数据文件 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 4. 查看 indexer 日志中是否有错误信息
stdin, stdout, stderr = c.exec_command(
    'grep -i "error\\|fail\\|warning\\|no entry\\|Could not load" /data/log/indexer.log 2>/dev/null | tail -20'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== Indexer 错误/警告日志 ===')
print(out if out.strip() else '(无错误日志)')

# 5. 查看 indexer 日志中最近的 indexer 进程输出（非 extractor）
stdin, stdout, stderr = c.exec_command(
    'grep -v "tensorflow\\|extractor\\|oneDNN\\|MLIR" /data/log/indexer.log 2>/dev/null | tail -30'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== Indexer 业务日志 (排除TF噪音) ===')
print(out if out.strip() else '(无业务日志)')

c.close()
