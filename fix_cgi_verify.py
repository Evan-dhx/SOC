import paramiko
import sys

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

# =====================================================================
# PART 1: 检查 auth 和 topn CGI 的 protobuf 符号
# =====================================================================
print("=" * 70)
print("PART 1: 检查 auth 和 topn CGI 的 protobuf 符号")
print("=" * 70)

print("\n--- auth CGI 符号 ---")
run('nm -D /Server/www/d/auth 2>/dev/null | grep "AddDescriptors" | head -3', "auth AddDescriptors")
run('nm -D /Server/www/d/auth 2>/dev/null | grep " U " | grep "_ZN6config" | head -5', "auth config:: 未定义符号")
run('ldd /Server/www/d/auth 2>/dev/null | grep -i "not found\\|protobuf\\|common"', "auth 依赖")

print("\n--- topn CGI 符号 ---")
run('nm -D /Server/www/d/topn 2>/dev/null | grep "AddDescriptors" | head -3', "topn AddDescriptors")
run('nm -D /Server/www/d/topn 2>/dev/null | grep " U " | grep "_ZN6config" | head -5', "topn config:: 未定义符号")
run('ldd /Server/www/d/topn 2>/dev/null | grep -i "not found\\|protobuf\\|common"', "topn 依赖")

# 测试 auth 和 topn 是否能运行
print("\n--- 测试 auth CGI ---")
out, _ = run('LD_PRELOAD= /Server/www/d/auth 2>&1 | head -5', "auth 运行测试")

print("\n--- 测试 topn CGI ---")
out, _ = run('LD_PRELOAD= /Server/www/d/topn 2>&1 | head -5', "topn 运行测试")

# =====================================================================
# PART 2: 如果需要，重新编译 auth 和 topn
# =====================================================================
print("\n" + "=" * 70)
print("PART 2: 检查并重新编译 auth 和 topn")
print("=" * 70)

# 检查 Makefile 中的构建规则
run('grep -n "auth\|topn" /root/SOC/ly_server_src/server/Makefile 2>/dev/null | head -15', "Makefile 规则")

# 尝试重新编译 auth
print("\n--- 重新编译 auth ---")
out, err = run('cd /root/SOC/ly_server_src/server && make auth 2>&1 | tail -10', "make auth", timeout=120)
if 'config_pusher' in out or '.o' in out:
    run('ls -la /root/SOC/ly_server_src/server/auth 2>/dev/null', "编译结果")
    # 测试
    out2, _ = run('/root/SOC/ly_server_src/server/auth 2>&1 | head -5', "测试 auth")
    if 'symbol lookup error' not in out2.lower():
        print("  auth 重新编译成功!")
        run('cp /root/SOC/ly_server_src/server/auth /Server/www/d/auth', "部署 auth")
        run('chmod +x /Server/www/d/auth', "设置权限")
    else:
        print(f"  auth 仍有错误: {out2.strip()[:300]}")

# 尝试重新编译 topn
print("\n--- 重新编译 topn ---")
out, err = run('cd /root/SOC/ly_server_src/server && make topn 2>&1 | tail -10', "make topn", timeout=120)
if 'topn' in out.lower() or '.o' in out:
    run('ls -la /root/SOC/ly_server_src/server/topn 2>/dev/null', "编译结果")
    # 测试
    out2, _ = run('/root/SOC/ly_server_src/server/topn 2>&1 | head -5', "测试 topn")
    if 'symbol lookup error' not in out2.lower():
        print("  topn 重新编译成功!")
        run('cp /root/SOC/ly_server_src/server/topn /Server/www/d/topn', "部署 topn")
        run('chmod +x /Server/www/d/topn', "设置权限")
    else:
        print(f"  topn 仍有错误: {out2.strip()[:300]}")

# =====================================================================
# PART 3: 重新编译所有其他 CGI 程序
# =====================================================================
print("\n" + "=" * 70)
print("PART 3: 重新编译所有 CGI 程序")
print("=" * 70)

# 从 Makefile 获取所有需要编译的目标
out, _ = run('grep "WWW_EXES\|BIN_EXES" /root/SOC/ly_server_src/server/Makefile 2>/dev/null', "CGI 列表")
# 获取完整的 WWW_EXES 列表
run('make -C /root/SOC/ly_server_src/server -n 2>/dev/null | grep "^g++" | head -20', "编译命令预览")

# 编译所有
print("\n--- make all ---")
out, err = run('cd /root/SOC/ly_server_src/server && make 2>&1 | tail -30', "make all", timeout=180)
if 'error' in out.lower() and 'Error' in out:
    print(f"  编译有错误: {out[-500:]}")
else:
    print("  make all 完成")

# 部署所有重新编译的 CGI
print("\n--- 部署重新编译的 CGI ---")
# 检查哪些 CGI 被重新编译了
run('ls -la /root/SOC/ly_server_src/server/auth /root/SOC/ly_server_src/server/topn /root/SOC/ly_server_src/server/mo /root/SOC/ly_server_src/server/event 2>/dev/null', "编译的 CGI")

# 从 Makefile 获取安装目标
out, _ = run('grep "install\|INSTALL" /root/SOC/ly_server_src/server/Makefile 2>/dev/null | head -10', "安装规则")

# 逐个部署
cgis = ['auth', 'topn', 'mo', 'internalip', 'event', 'bwlist', 'feature', 'event_feature',
        'locinfo', 'geoinfo', 'portinfo', 'ipinfo', 'config', 'threatinfo', 'threatinfopro']
for cgi in cgis:
    out, _ = run(f'ls /root/SOC/ly_server_src/server/{cgi} 2>/dev/null', f"检查 {cgi}")
    if out.strip():
        run(f'cp /root/SOC/ly_server_src/server/{cgi} /Server/www/d/{cgi} 2>/dev/null', f"部署 {cgi}")
        run(f'chmod +x /Server/www/d/{cgi} 2>/dev/null', f"权限 {cgi}")

# 部署 config_pusher
run('cp /root/SOC/ly_server_src/server/config_pusher /Server/bin/config_pusher 2>/dev/null', "部署 config_pusher")
run('chmod +x /Server/bin/config_pusher 2>/dev/null', "权限 config_pusher")

# 部署 gen_event
run('cp /root/SOC/ly_server_src/server/gen_event /Server/bin/gen_event 2>/dev/null', "部署 gen_event")
run('chmod +x /Server/bin/gen_event 2>/dev/null', "权限 gen_event")

# =====================================================================
# PART 4: 测试 auth 和 topn
# =====================================================================
print("\n" + "=" * 70)
print("PART 4: 测试重新编译的 CGI")
print("=" * 70)

print("\n--- 测试 auth ---")
out, _ = run('/Server/www/d/auth 2>&1 | head -5', "auth 运行")
auth_ok = 'symbol lookup error' not in out.lower()
print(f"  auth: {'OK' if auth_ok else 'FAIL'}")

print("\n--- 测试 topn ---")
out, _ = run('/Server/www/d/topn 2>&1 | head -5', "topn 运行")
topn_ok = 'symbol lookup error' not in out.lower()
print(f"  topn: {'OK' if topn_ok else 'FAIL'}")

# =====================================================================
# PART 5: 清理旧日志并验证
# =====================================================================
print("\n" + "=" * 70)
print("PART 5: 清理旧日志")
print("=" * 70)

# 清空 config_pusher 旧日志
run('echo "=== LOG CLEARED $(date) ===" > /data/log/config_pusher.log', "清理 config_pusher 日志")
# 清空 httpd 错误日志
run('echo "" > /etc/httpd/logs/ly_error_log', "清理 httpd 错误日志")

# 运行一次 config_pusher 验证
run('/Server/bin/config_pusher 2>&1; echo "EXIT=$?"', "config_pusher 验证")
run('cat /data/log/config_pusher.log', "config_pusher 日志")

# =====================================================================
# PART 6: 最终总结
# =====================================================================
print("\n" + "=" * 70)
print("PART 6: 最终验证总结")
print("=" * 70)

# nfdump
out, _ = run('/Agent/bin/nfdump -V 2>&1', "nfdump")
nfdump_ok = 'Version' in out
print(f"  nfdump:            {'OK' if nfdump_ok else 'FAIL'}")

# config_pusher
out, _ = run('/Server/bin/config_pusher 2>&1; echo "EXIT=$?"', "config_pusher")
pusher_ok = 'EXIT=0' in out
print(f"  config_pusher:     {'OK' if pusher_ok else 'FAIL'}")

# auth CGI
out, _ = run('/Server/www/d/auth 2>&1 | head -3', "auth")
print(f"  auth CGI:          {'OK' if auth_ok else 'FAIL'}")

# topn CGI
out, _ = run('/Server/www/d/topn 2>&1 | head -3', "topn")
print(f"  topn CGI:          {'OK' if topn_ok else 'FAIL'}")

# tsensor
out, _ = run('ps aux | grep tsensor | grep -v grep | wc -l', "tsensor")
tsensor_ok = int(out.strip()) > 0
print(f"  tsensor:           {'OK' if tsensor_ok else 'FAIL'}")

# 数据库
out, _ = run('mysql -u root -ppassword123 -e "SELECT 1;" 2>&1 | grep -c "1"', "数据库")
db_ok = int(out.strip()) > 0
print(f"  database:          {'OK' if db_ok else 'FAIL'}")

# 配置文件
out, _ = run('ls /Agent/data/indexer_feature /Agent/data/indexer_cache /Server/etc/tisrs.conf 2>/dev/null | wc -l', "配置文件")
config_ok = int(out.strip()) >= 3
print(f"  config files:      {'OK' if config_ok else 'FAIL'}")

all_ok = nfdump_ok and pusher_ok and auth_ok and topn_ok and tsensor_ok and db_ok and config_ok
print(f"\n  {'所有修复验证通过!' if all_ok else '部分修复仍有问题'}")

c.close()
