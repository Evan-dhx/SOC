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
        print(out.strip()[:4000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:1000]}")
    return out, err

# =====================================================================
# PART 1: 检查 config_pusher 实际日志（正确路径）
# =====================================================================
print("=" * 70)
print("PART 1: 检查 config_pusher 实际日志")
print("=" * 70)

run('tail -50 /data/log/config_pusher.log 2>/dev/null || echo "日志文件不存在"', "config_pusher 日志")

# 再次手动运行并查看完整输出
print("\n--- 手动运行 config_pusher ---")
out, err = run('/Server/bin/config_pusher 2>&1; echo "EXIT=$?"', "config_pusher 运行")

# =====================================================================
# PART 2: 检查 nfdump 源码结构
# =====================================================================
print("\n" + "=" * 70)
print("PART 2: 检查 nfdump 源码结构")
print("=" * 70)

# 列出源码目录
print("\n--- nfdump bin 目录 ---")
run('ls -la /root/SOC/ly_analyser_src/nfdump/bin/*.c /root/SOC/ly_analyser_src/nfdump/bin/*.h 2>/dev/null | head -30', "源文件")

# 检查 .pb.cc 和 .pb.h 文件
print("\n--- protobuf 生成文件 ---")
run('find /root/SOC/ly_analyser_src/ -name "*.pb.cc" -o -name "*.pb.h" 2>/dev/null | head -20', "pb 文件")

# 检查 nfdump 的 Makefile
print("\n--- nfdump Makefile 关键部分 ---")
run('head -50 /root/SOC/ly_analyser_src/nfdump/bin/Makefile 2>/dev/null', "Makefile 头部")
run('grep -n "nfdump_LDADD\|nfdump_SOURCES\|nfdump_OBJECTS\|DEPS_LIBS\|LIBS" /root/SOC/ly_analyser_src/nfdump/bin/Makefile 2>/dev/null', "Makefile 链接配置")

# 检查 .pb.cc 文件是否包含 protobuf 版本信息
print("\n--- .pb.cc 文件版本信息 ---")
run('head -20 /root/SOC/ly_analyser_src/nfdump/bin/config.pb.cc 2>/dev/null || find /root/SOC/ly_analyser_src/ -name "config.pb.cc" 2>/dev/null | head -3', "config.pb.cc")
run('grep -r "AddDescriptors\|AddDescriptorsRunner\|ConstantInitialized" /root/SOC/ly_analyser_src/nfdump/bin/*.pb.cc 2>/dev/null | head -10', "protobuf 版本标记")

# 检查 agent 目录下的 .pb.cc 文件
print("\n--- agent 目录的 .pb.cc 文件 ---")
run('find /root/SOC/ly_analyser_src/agent/ -name "*.pb.cc" 2>/dev/null | head -10', "agent pb 文件")
run('grep -r "AddDescriptors\|AddDescriptorsRunner" /root/SOC/ly_analyser_src/agent/*.pb.cc /root/SOC/ly_analyser_src/agent/**/*.pb.cc 2>/dev/null | head -5', "agent protobuf 版本")

# =====================================================================
# PART 3: 检查 libflow_filter.so 是否有 config:: 符号
# =====================================================================
print("\n" + "=" * 70)
print("PART 3: 检查 libflow_filter.so 的 config:: 符号")
print("=" * 70)

run('ls -la /Agent/lib/libflow_filter.so 2>/dev/null', "libflow_filter.so 文件")
run('nm -D /Agent/lib/libflow_filter.so 2>/dev/null | grep "_ZN6config6Config\\|_ZN6config5Event" | head -20', "libflow_filter config:: 符号")
run('nm -D /Agent/lib/libflow_filter.so 2>/dev/null | grep " T " | grep "_ZN6config" | head -20', "libflow_filter config:: 定义")

# 检查 libcommon.so 是否有 Config 和 Event 符号
print("\n--- libcommon.so 的 Config/Event 符号 ---")
run('nm -D /lib64/libcommon.so 2>/dev/null | grep "_ZN6config6Config\\|_ZN6config5Event" | head -20', "libcommon Config/Event")

# =====================================================================
# PART 4: 检查是否能直接 make
# =====================================================================
print("\n" + "=" * 70)
print("PART 4: 尝试从源码编译 nfdump")
print("=" * 70)

# 检查编译环境
print("\n--- 编译环境 ---")
run('g++ --version 2>/dev/null | head -1', "g++ 版本")
run('ls /usr/local/lib/libprotobuf.so 2>/dev/null', "libprotobuf.so")
run('ls /Agent/lib/libflow_filter.so /Agent/lib/libcommon.so 2>/dev/null', "Agent 库")

# 尝试 make
print("\n--- 尝试 make ---")
out, err = run('cd /root/SOC/ly_analyser_src/nfdump/bin && make nfdump 2>&1 | tail -30', "make nfdump", timeout=120)

# 检查是否生成了新的 nfdump
run('ls -la /root/SOC/ly_analyser_src/nfdump/bin/nfdump 2>/dev/null', "编译结果")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)
