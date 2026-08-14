import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 1. 检查 syslog 中的 indexer 相关日志
stdin, stdout, stderr = c.exec_command(
    'grep -i "indexer\\|sus\\|no entry\\|Could not load\\|unfiltered\\|ip set\\|LoadIP\\|mining" /var/log/messages 2>/dev/null | tail -30'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== syslog 中的 indexer 日志 ===')
print(out if out.strip() else '(syslog中无相关日志)')

# 2. 检查 /var/log/syslog
stdin, stdout, stderr = c.exec_command(
    'grep -i "indexer\\|sus\\|no entry\\|unfiltered\\|ip set" /var/log/syslog 2>/dev/null | tail -30'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== /var/log/syslog ===')
print(out if out.strip() else '(无 syslog 文件或无相关日志)')

# 3. 手动运行 indexer 测试加载
stdin, stdout, stderr = c.exec_command(
    'cd /Agent/bin && sudo -u apache DEBUG=ALL ./extractor -v 1 -t 1786609500 -i ./indexer 2>&1 | grep -v "tensorflow\\|oneDNN\\|MLIR" | head -50'
)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print('=== 手动运行 indexer (DEBUG模式, 前50行) ===')
print(out if out.strip() else '(无输出)')
if err.strip():
    print(f'STDERR: {err[:500]}')

# 4. 查看 indexer 的 syslog 输出（journalctl）
stdin, stdout, stderr = c.exec_command(
    'journalctl -t indexer --no-pager -n 30 2>/dev/null || journalctl --no-pager -n 30 2>/dev/null | grep -i "indexer\\|sus\\|unfiltered\\|ip set" | tail -20'
)
out = stdout.read().decode('utf-8', errors='replace')
print('=== journalctl indexer 日志 ===')
print(out if out.strip() else '(无 journalctl 日志)')

c.close()
