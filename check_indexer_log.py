import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 1. 查看 indexer 日志目录
stdin, stdout, stderr = c.exec_command('ls -lt /data/log/ 2>/dev/null | head -10')
print('=== /data/log/ 目录 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 2. 查看最近的 indexer 日志
stdin, stdout, stderr = c.exec_command('tail -50 /data/log/indexer.log 2>/dev/null')
out = stdout.read().decode('utf-8', errors='replace')
print('=== Indexer 日志 (最后50行) ===')
print(out if out.strip() else '(无日志)')

# 3. 搜索威胁情报相关日志
stdin, stdout, stderr = c.exec_command(
    'grep -i "sus_threat\\|ti_dns\\|mining\\|unfiltered\\|ip set\\|no entry" /data/log/indexer.log 2>/dev/null | tail -20'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== 威胁情报相关日志 ===')
print(out if out.strip() else '(未找到威胁情报相关日志)')

# 4. 查看 launch_indexer.sh 内容
stdin, stdout, stderr = c.exec_command('cat /Agent/bin/launch_indexer.sh 2>/dev/null')
print('=== launch_indexer.sh ===')
print(stdout.read().decode('utf-8', errors='replace'))

# 5. 查看 Agent 的 cron 配置
stdin, stdout, stderr = c.exec_command('crontab -l 2>/dev/null; echo "---"; ls /etc/cron.d/ 2>/dev/null')
print('=== Cron 配置 ===')
print(stdout.read().decode('utf-8', errors='replace'))

c.close()
