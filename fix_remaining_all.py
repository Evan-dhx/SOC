import paramiko
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=30):
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
# PART 1: 诊断 config_pusher SQL "ip" 列错误
# =====================================================================
print("=" * 70)
print("PART 1: 诊断 config_pusher SQL 'ip' 列错误")
print("=" * 70)

# 检查 t_event_config_dnstunnel 表结构
print("\n--- t_event_config_dnstunnel 表结构 ---")
run('mysql -u root -ppassword123 -e "DESCRIBE t_event_config_dnstunnel;" server 2>/dev/null || '
    'mysql -u root -ppassword123 -e "DESCRIBE server.t_event_config_dnstunnel;" 2>/dev/null || '
    'mysql -u root -ppassword123 -e "SHOW COLUMNS FROM t_event_config_dnstunnel;" server 2>/dev/null',
    "表结构")

# 检查所有事件配置表
print("\n--- 检查所有 t_event_config_* 表的 ip 列 ---")
run('mysql -u root -ppassword123 -e "SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=\'server\' AND TABLE_NAME LIKE \'t_event_config_%\' AND COLUMN_NAME=\'ip\' ORDER BY TABLE_NAME;" 2>/dev/null', "有 ip 列的表")

run('mysql -u root -ppassword123 -e "SELECT TABLE_NAME, GROUP_CONCAT(COLUMN_NAME) as cols FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=\'server\' AND TABLE_NAME=\'t_event_config_dnstunnel\' GROUP BY TABLE_NAME;" 2>/dev/null', "dnstunnel 所有列")

# 手动执行 config_pusher 使用的 SQL 查询
print("\n--- 手动执行 config_pusher 的 SQL 查询 ---")
run('mysql -u root -ppassword123 -e "SELECT t1.\`id\`, t2.\`devid\`, t1.\`ip\`, t1.\`namelen\`, t1.\`fqcount\`, t1.\`detvalue\`, t2.\`weekday\`, t2.\`stime\`, t2.\`etime\`, t2.\`coverrange\` FROM \`t_event_config_dnstunnel\` t1, \`t_event_list\` t2, \`t_event_status\` t3 WHERE t1.\`id\`=t2.\`config_id\` AND t2.\`type_id\`=7 AND t2.\`status_id\`=t3.\`id\` AND t3.\`status\`=\'ON\';" server 2>&1 | head -5', "带表前缀的查询")

run('mysql -u root -ppassword123 -e "SELECT t1.\`id\`, t2.\`devid\`, \`ip\`, \`namelen\`, \`fqcount\`, \`detvalue\`, t2.\`weekday\`, t2.\`stime\`, t2.\`etime\`, t2.\`coverrange\` FROM \`t_event_config_dnstunnel\` t1, \`t_event_list\` t2, \`t_event_status\` t3 WHERE t1.\`id\`=t2.\`config_id\` AND t2.\`type_id\`=7 AND t2.\`status_id\`=t3.\`id\` AND t3.\`status\`=\'ON\';" server 2>&1 | head -5', "不带表前缀的查询(原始)")

# 检查 t_event_list 表是否有 ip 列（可能冲突）
print("\n--- 检查 t_event_list 表是否有 ip 列 ---")
run('mysql -u root -ppassword123 -e "SHOW COLUMNS FROM t_event_list;" server 2>/dev/null', "t_event_list 列")

# =====================================================================
# PART 2: 检查 nfdump 缺失的 protobuf 符号
# =====================================================================
print("\n" + "=" * 70)
print("PART 2: 检查 nfdump 缺失的 protobuf 符号")
print("=" * 70)

# 确保 nfdump 是原始二进制
run('ls -la /Agent/bin/nfdump /Agent/bin/nfdump.real 2>/dev/null', "nfdump 文件")
run('file /Agent/bin/nfdump', "nfdump 类型")

# 运行 nfdump 看完整的错误
print("\n--- nfdump 运行测试 ---")
out, _ = run('LD_PRELOAD=/usr/local/lib/compat/libadd_descriptors_shim.so /Agent/bin/nfdump -V 2>&1 || true', "nfdump -V (with shim)")

# 列出 nfdump 所有未定义的 config:: 和 protobuf 符号
print("\n--- nfdump 未定义的 config:: 符号 ---")
run('nm -D /Agent/bin/nfdump 2>/dev/null | grep " U " | grep "_ZN6config"', "config:: 未定义符号")

print("\n--- nfdump 未定义的 protobuf 符号(非AddDescriptors) ---")
run('nm -D /Agent/bin/nfdump 2>/dev/null | grep " U " | grep "protobuf" | grep -v "AddDescriptors" | head -20', "protobuf 未定义符号")

# 检查 libcommon.so 提供的 config:: 符号
print("\n--- libcommon.so 提供的 config:: 符号 ---")
run('nm -D /lib64/libcommon.so 2>/dev/null | grep " T " | grep "_ZN6config" | head -20', "libcommon.so config:: 定义符号")

# 检查 nfdump 源码是否在远程主机
print("\n--- 检查 nfdump 源码 ---")
run('ls /root/analyse/nfdump/bin/Makefile 2>/dev/null || echo "nfdump 源码不在 /root/analyse"', "源码位置")
run('ls /Agent/src/nfdump/bin/ 2>/dev/null | head -10 || echo "nfdump 源码不在 /Agent/src"', "Agent 源码")
run('find / -name "nfdump.c" -path "*/bin/*" 2>/dev/null | head -5', "搜索 nfdump.c")

# 检查是否有 protoc 和 protobuf 开发头文件
print("\n--- 检查 protobuf 开发环境 ---")
run('protoc --version 2>/dev/null || echo "protoc 不可用"', "protoc 版本")
run('ls /usr/local/include/google/protobuf/message.h 2>/dev/null || echo "protobuf 头文件不可用"', "protobuf 头文件")
run('pkg-config --modversion protobuf 2>/dev/null || echo "pkg-config protobuf 不可用"', "protobuf pkg-config")

# =====================================================================
# PART 3: 检查 config_pusher 当前运行状态
# =====================================================================
print("\n" + "=" * 70)
print("PART 3: 检查 config_pusher 当前运行状态")
print("=" * 70)

# 手动运行 config_pusher
print("\n--- 手动运行 config_pusher ---")
out, err = run('/Server/bin/config_pusher 2>&1; echo "EXIT_CODE=$?"', "config_pusher 运行", timeout=30)
if 'EXIT_CODE=0' in out:
    print("  config_pusher 运行成功 (退出码 0)")
else:
    print(f"  config_pusher 运行失败!")

# 检查最近的 config_pusher 日志
print("\n--- 最近 config_pusher 日志 ---")
run('tail -30 /Server/log/config_pusher.log 2>/dev/null || echo "日志文件不存在"', "config_pusher 日志")

# 检查 crontab
print("\n--- config_pusher crontab ---")
run('crontab -l 2>/dev/null | grep config_pusher', "crontab")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)
