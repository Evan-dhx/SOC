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
# PART 1: 测试源码目录的 nfdump 二进制
# =====================================================================
print("=" * 70)
print("PART 1: 测试源码目录的 nfdump 二进制")
print("=" * 70)

# 检查源码 nfdump 的符号
print("\n--- 源码 nfdump 的 config:: 符号 ---")
run('nm -D /root/SOC/ly_analyser_src/nfdump/bin/nfdump 2>/dev/null | grep " U " | grep "_ZN6config" | head -10', "源码 nfdump config:: 未定义符号")

# 检查源码 nfdump 是否有 AddDescriptors (旧版) 或 AddDescriptorsRunner (新版)
print("\n--- 源码 nfdump 的 AddDescriptors 符号 ---")
run('nm -D /root/SOC/ly_analyser_src/nfdump/bin/nfdump 2>/dev/null | grep "AddDescriptors" | head -5', "AddDescriptors 符号")

# 测试源码 nfdump
print("\n--- 测试源码 nfdump ---")
out, _ = run('/root/SOC/ly_analyser_src/nfdump/bin/nfdump -V 2>&1 || true', "源码 nfdump -V")
if 'symbol lookup error' in out.lower():
    print("  [!] 源码 nfdump 也有符号错误!")
    # 尝试不带 LD_PRELOAD
    out2, _ = run('LD_PRELOAD= /root/SOC/ly_analyser_src/nfdump/bin/nfdump -V 2>&1 || true', "源码 nfdump -V (无 preload)")
    if 'symbol lookup error' not in out2.lower():
        print("  源码 nfdump 无 preload 可以运行!")
        out = out2
elif out.strip():
    print(f"  源码 nfdump 运行成功!")
    print(f"  输出: {out.strip()[:300]}")

# =====================================================================
# PART 2: 如果源码 nfdump 可用，部署到 /Agent/bin/
# =====================================================================
print("\n" + "=" * 70)
print("PART 2: 部署源码 nfdump 到 /Agent/bin/")
print("=" * 70)

source_ok = 'symbol lookup error' not in out.lower() and out.strip() != ''

if source_ok:
    # 备份当前 nfdump
    run('cp /Agent/bin/nfdump.real /Agent/bin/nfdump.bak 2>/dev/null || cp /Agent/bin/nfdump /Agent/bin/nfdump.bak 2>/dev/null', "备份当前 nfdump")
    
    # 复制源码 nfdump
    run('cp /root/SOC/ly_analyser_src/nfdump/bin/nfdump /Agent/bin/nfdump', "部署源码 nfdump")
    run('chmod +x /Agent/bin/nfdump', "设置权限")
    
    # 验证
    print("\n--- 验证部署 ---")
    out, _ = run('/Agent/bin/nfdump -V 2>&1 || true', "部署后 nfdump -V")
    if 'symbol lookup error' in out.lower():
        print("  [!] 部署后仍有错误!")
        print(f"  错误: {out.strip()[:500]}")
        # 恢复
        run('cp /Agent/bin/nfdump.bak /Agent/bin/nfdump', "恢复备份")
        source_ok = False
    else:
        print(f"  nfdump 部署成功!")
        print(f"  输出: {out.strip()[:300]}")
        
        # 测试实际命令
        out2, _ = run('/Agent/bin/nfdump -r /Agent/flow/1/nfcapd.current -s record -n 5 2>&1 | head -10', "nfdump 实际命令")
        if 'symbol lookup error' in out2.lower() or 'error' in out2.lower():
            print(f"  实际命令有错误: {out2.strip()[:500]}")
        else:
            print(f"  实际命令成功!")
            print(f"  输出: {out2.strip()[:300]}")
        
        # 检查是否还有 AddDescriptors 问题
        out3, _ = run('nm -D /Agent/bin/nfdump 2>/dev/null | grep "AddDescriptors" | head -5', "部署后 AddDescriptors 符号")
        print(f"  AddDescriptors 符号:\n{out3.strip()}")
else:
    print("  源码 nfdump 不可用，需要重新编译")
    
    # =====================================================================
    # PART 2B: 强制重新编译
    # =====================================================================
    print("\n" + "=" * 70)
    print("PART 2B: 强制重新编译 nfdump")
    print("=" * 70)
    
    # 检查是否有 .o 文件需要清理
    run('ls /root/SOC/ly_analyser_src/nfdump/bin/nfdump*.o 2>/dev/null | head -10', "现有 .o 文件")
    
    # 清理并重新编译
    print("\n--- make clean && make nfdump ---")
    out, err = run('cd /root/SOC/ly_analyser_src/nfdump/bin && make clean 2>&1 | tail -5', "make clean", timeout=60)
    out, err = run('cd /root/SOC/ly_analyser_src/nfdump/bin && make nfdump 2>&1 | tail -30', "make nfdump", timeout=120)
    
    # 检查编译结果
    run('ls -la /root/SOC/ly_analyser_src/nfdump/bin/nfdump 2>/dev/null', "编译结果")
    
    # 测试
    out, _ = run('/root/SOC/ly_analyser_src/nfdump/bin/nfdump -V 2>&1 || true', "重新编译 nfdump -V")
    if 'symbol lookup error' not in out.lower() and out.strip():
        print(f"  重新编译成功!")
        print(f"  输出: {out.strip()[:300]}")
        
        # 部署
        run('cp /root/SOC/ly_analyser_src/nfdump/bin/nfdump /Agent/bin/nfdump', "部署重新编译 nfdump")
        run('chmod +x /Agent/bin/nfdump', "设置权限")
        out2, _ = run('/Agent/bin/nfdump -V 2>&1', "验证部署")
        print(f"  部署验证: {out2.strip()[:300]}")
        source_ok = True
    else:
        print(f"  重新编译失败或有错误: {out.strip()[:500]}")

# =====================================================================
# PART 3: 检查 config_pusher 完整状态
# =====================================================================
print("\n" + "=" * 70)
print("PART 3: 检查 config_pusher 完整状态")
print("=" * 70)

# 检查完整 crontab
print("\n--- 完整 crontab ---")
run('crontab -l 2>/dev/null', "crontab")

# 检查 config_pusher 日志最后 10 行
print("\n--- config_pusher 日志最后 10 行 ---")
run('tail -10 /data/log/config_pusher.log 2>/dev/null', "日志")

# 再次手动运行
print("\n--- 手动运行 config_pusher ---")
out, _ = run('/Server/bin/config_pusher 2>&1; echo "EXIT=$?"', "运行结果")

# =====================================================================
# PART 4: 检查 tisrs.conf 和 httpd 状态
# =====================================================================
print("\n" + "=" * 70)
print("PART 4: 检查 tisrs.conf 和 httpd 状态")
print("=" * 70)

run('cat /Server/etc/tisrs.conf 2>/dev/null', "tisrs.conf")
run('ls -la /etc/httpd/logs/ 2>/dev/null | head -10', "httpd logs 目录")
run('tail -5 /etc/httpd/logs/ly_error_log 2>/dev/null', "httpd error_log 最后5行")

# =====================================================================
# PART 5: 清理 shim 相关文件
# =====================================================================
if source_ok:
    print("\n" + "=" * 70)
    print("PART 5: 清理不再需要的 shim 文件")
    print("=" * 70)
    
    # 清理 shim 库
    run('rm -f /usr/local/lib/compat/libadd_descriptors_shim.so', "删除 shim 库")
    run('rm -f /tmp/shim.c /tmp/shim.cpp', "删除临时文件")
    run('rm -f /Agent/bin/nfdump.bak /Agent/bin/nfdump.real 2>/dev/null', "清理备份文件")
    print("  清理完成")

c.close()
print("\n" + "=" * 70)
print("修复完成!")
print("=" * 70)
