import paramiko
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=60):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        print(f"[{label}]")
    if out.strip():
        print(out.strip()[:3000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:500]}")
    return out, err

results = {}

# =====================================================================
# 1. 验证 nfdump
# =====================================================================
print("=" * 70)
print("[1] 验证 nfdump")
print("=" * 70)

out, _ = run('/Agent/bin/nfdump -V 2>&1', "nfdump -V")
nfdump_ok = 'Version' in out and 'symbol lookup error' not in out.lower()
results['nfdump'] = nfdump_ok

# 测试实际流量查询
out, _ = run('/Agent/bin/nfdump -r /Agent/flow/1/nfcapd.current -s record -n 3 2>&1 | head -5', "nfdump 实际查询")
nfdump_real_ok = 'symbol lookup error' not in out.lower() and 'error' not in out.lower()
print(f"  nfdump 实际查询: {'成功' if nfdump_real_ok else '失败'}")
results['nfdump_real'] = nfdump_real_ok

# =====================================================================
# 2. 验证 config_pusher
# =====================================================================
print("\n" + "=" * 70)
print("[2] 验证 config_pusher")
print("=" * 70)

# 标记日志并运行
run('echo "=== VERIFY $(date) ===" >> /data/log/config_pusher.log', "标记日志")
out, _ = run('/Server/bin/config_pusher 2>&1; echo "EXIT=$?"', "config_pusher 运行")
pusher_ok = 'EXIT=0' in out and 'symbol lookup error' not in out.lower()
results['config_pusher'] = pusher_ok

# 检查日志是否有新错误
out, _ = run('tail -5 /data/log/config_pusher.log 2>/dev/null', "最新日志")
pusher_log_ok = 'symbol lookup error' not in out.lower() and 'command not found' not in out.lower()
print(f"  config_pusher 日志: {'无新错误' if pusher_log_ok else '有错误'}")
results['config_pusher_log'] = pusher_log_ok

# =====================================================================
# 3. 验证 tisrs.conf
# =====================================================================
print("\n" + "=" * 70)
print("[3] 验证 tisrs.conf")
print("=" * 70)

out, _ = run('cat /Server/etc/tisrs.conf', "tisrs.conf 内容")
tisrs_ok = 'TISRSEOF' not in out and 'KEY=' in out
results['tisrs'] = tisrs_ok

# =====================================================================
# 4. 验证 httpd error_log
# =====================================================================
print("\n" + "=" * 70)
print("[4] 验证 httpd error_log")
print("=" * 70)

run('ls -la /etc/httpd/logs/error_log /etc/httpd/logs/ly_error_log 2>/dev/null', "日志文件")
out, _ = run('tail -10 /etc/httpd/logs/ly_error_log 2>/dev/null', "最近错误")
httpd_errors = [line for line in out.split('\n') if 'error' in line.lower() or 'Error' in line]
print(f"  最近 httpd 错误数: {len(httpd_errors)}")

# 检查 topn 是否缺失
run('ls -la /Server/www/d/topn 2>/dev/null || echo "topn CGI 不存在"', "topn CGI")
# 检查 auth CGI
run('ls -la /Server/www/d/auth 2>/dev/null || echo "auth CGI 不存在"', "auth CGI")

results['httpd'] = len(httpd_errors) == 0

# =====================================================================
# 5. 验证 indexer 日志
# =====================================================================
print("\n" + "=" * 70)
print("[5] 验证 indexer 日志")
print("=" * 70)

# 检查最近 indexer 日志
out, _ = run('ls /Agent/log/indexer*.log 2>/dev/null | tail -1', "最新 indexer 日志文件")
if out.strip():
    logfile = out.strip().split('\n')[0]
    out, _ = run(f'tail -30 "{logfile}" 2>/dev/null', f"indexer 日志 ({logfile})")
    indexer_errors = [line for line in out.split('\n') if 'error' in line.lower() and 'nfdump' in line.lower()]
    indexer_nf_ok = len(indexer_errors) == 0
    print(f"  indexer nfdump 错误: {len(indexer_errors)} 条")
    
    # 检查最近的 nfdump 调用
    out2, _ = run(f'grep -i "nfdump\\|cache" "{logfile}" 2>/dev/null | tail -10', "nfdump/cache 相关日志")
    if out2.strip():
        print(f"  nfdump/cache 日志:\n{out2.strip()[:500]}")
else:
    run('ls /data/log/indexer*.log 2>/dev/null | tail -1', "搜索 indexer 日志")
    run('find / -name "indexer*.log" 2>/dev/null | tail -3', "搜索 indexer 日志")
    indexer_nf_ok = True

results['indexer'] = indexer_nf_ok

# =====================================================================
# 6. 验证 tsensor
# =====================================================================
print("\n" + "=" * 70)
print("[6] 验证 tsensor")
print("=" * 70)

# 检查 tsensor 进程
out, _ = run('ps aux | grep tsensor | grep -v grep | head -3', "tsensor 进程")
tsensor_running = len(out.strip()) > 0
print(f"  tsensor 进程: {'运行中' if tsensor_running else '未运行'}")

# 检查 tsensor 日志
out, _ = run('tail -5 /Agent/log/tsensor.log 2>/dev/null || tail -5 /data/log/tsensor*.log 2>/dev/null || echo "无 tsensor 日志"', "tsensor 日志")
tsensor_errors = [line for line in out.split('\n') if 'error' in line.lower() or 'segfault' in line.lower()]
print(f"  tsensor 最近错误: {len(tsensor_errors)} 条")

results['tsensor'] = tsensor_running and len(tsensor_errors) == 0

# =====================================================================
# 7. 验证 Agent 进程
# =====================================================================
print("\n" + "=" * 70)
print("[7] 验证 Agent 进程")
print("=" * 70)

run('ps aux | grep -E "nfcapd|indexer|extract_feature" | grep -v grep | head -5', "Agent 进程")

# =====================================================================
# 8. 验证数据库连接
# =====================================================================
print("\n" + "=" * 70)
print("[8] 验证数据库连接")
print("=" * 70)

out, _ = run('mysql -u root -ppassword123 -e "SELECT 1 as test;" 2>&1', "数据库连接")
db_ok = 'test' in out and 'error' not in out.lower()
results['database'] = db_ok

# =====================================================================
# 9. 检查所有关键文件
# =====================================================================
print("\n" + "=" * 70)
print("[9] 检查所有关键配置文件")
print("=" * 70)

files_to_check = [
    '/Agent/data/indexer_feature',
    '/Agent/data/indexer_cache',
    '/Agent/data/ti_dns',
    '/Agent/data/sus_threat',
    '/Agent/data/mining_domain',
    '/Agent/data/mining_ip',
    '/Server/etc/tisrs.conf',
    '/etc/my.cnf.d/gl.server.cnf',
]

for f in files_to_check:
    out, _ = run(f'ls -la "{f}" 2>/dev/null || echo "不存在: {f}"', f"文件检查")
    exists = '不存在' not in out
    print(f"  {f}: {'存在' if exists else '不存在'}")

# =====================================================================
# 10. 总结
# =====================================================================
print("\n" + "=" * 70)
print("[10] 修复验证总结")
print("=" * 70)

all_ok = True
for key, val in results.items():
    status = "OK" if val else "FAIL"
    print(f"  {key:25s}: {status}")
    if not val:
        all_ok = False

print("\n" + "=" * 70)
if all_ok:
    print("所有修复验证通过!")
else:
    print("部分修复仍有问题，需要进一步处理")
print("=" * 70)

c.close()
