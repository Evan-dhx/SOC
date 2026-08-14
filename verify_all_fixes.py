import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print("=" * 60)
print("最终验证 - 所有修复")
print("=" * 60)

# 1. 确认文件存在
print("\n[1] 文件确认")
for f in ['/Agent/data/indexer_feature', '/Agent/data/indexer_cache',
          '/Agent/data/pop_service', '/Agent/data/sus_threat',
          '/Agent/data/ti_dns', '/Agent/data/mining_domain', '/Agent/data/mining_ip']:
    stdin, stdout, stderr = c.exec_command(f'ls -la {f} 2>&1')
    line = stdout.read().decode('utf-8', errors='replace').strip()
    exists = "OK" if "No such" not in line and "cannot" not in line else "MISSING"
    print(f"  {exists}: {f}")

# 2. 检查 16:42 之后所有报错
print("\n[2] 16:42 之后 syslog 报错检查")
stdin, stdout, stderr = c.exec_command(
    'journalctl -t indexer --no-pager --since "16:42" 2>/dev/null | grep -i "pattern config\\|cache config\\|Permission denied\\|Could not create\\|no entry\\|pop_service" | tail -20'
)
out = stdout.read().decode('utf-8', errors='replace')
if out.strip():
    print(f"  发现报错:")
    for line in out.strip().split('\n'):
        print(f"    {line}")
else:
    print("  (无任何报错 - 所有修复成功!)")

# 3. 检查 indexer 最近完整日志
print("\n[3] Indexer 最近15条 syslog")
stdin, stdout, stderr = c.exec_command(
    'journalctl -t indexer --no-pager -n 15 2>/dev/null'
)
print(stdout.read().decode('utf-8', errors='replace'))

# 4. TSDB 文件统计
print("[4] TSDB 文件统计")
stdin, stdout, stderr = c.exec_command(
    'ls /Agent/data/db/20260813/ 2>/dev/null | wc -l'
)
print(f"  今日 TSDB 文件数: {stdout.read().decode().strip()}")
stdin, stdout, stderr = c.exec_command(
    'ls -lt /Agent/data/db/20260813/ 2>/dev/null | head -10'
)
print("  最新文件:")
print(stdout.read().decode('utf-8', errors='replace'))

# 5. 检查目录权限
print("[5] 目录权限")
for d in ['/Agent/data/db/', '/Agent/data/eventdb/']:
    stdin, stdout, stderr = c.exec_command(f'ls -ld {d}')
    print(f"  {stdout.read().decode().strip()}")

c.close()
print("\n验证完成!")
