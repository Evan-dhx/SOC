import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=120):
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
# 修复 gen_event 和 bwlist
# =====================================================================
print("=" * 70)
print("修复 gen_event 和 bwlist (未被 make all 编译)")
print("=" * 70)

# ---- 检查 Makefile 构建规则 ----
print("\n--- 检查 Makefile 构建规则 ---")
run('grep -n "gen_event\|bwlist\|^all\|^BIN_EXES\|^WWW_EXES" /root/SOC/ly_server_src/server/Makefile 2>/dev/null', "Makefile 规则")

# ---- 1. 编译 gen_event ----
print("\n" + "-" * 50)
print("[1] 编译 gen_event")
print("-" * 50)

out, err = run('cd /root/SOC/ly_server_src/server && make gen_event 2>&1', "make gen_event", timeout=120)
run('ls -la /root/SOC/ly_server_src/server/gen_event 2>/dev/null', "编译结果")

# 测试
out, _ = run('/root/SOC/ly_server_src/server/gen_event 2>&1 | head -5', "测试 gen_event")
if 'symbol lookup error' not in out.lower():
    print("  gen_event 编译测试成功!")
    run('cp /root/SOC/ly_server_src/server/gen_event /Server/bin/gen_event', "部署 gen_event")
    run('chmod +x /Server/bin/gen_event', "设置权限")
    out, _ = run('/Server/bin/gen_event 2>&1 | head -3', "验证部署")
    print(f"  部署验证: {'OK' if 'symbol lookup error' not in out.lower() else 'FAIL'}")
else:
    print(f"  gen_event 仍有错误: {out.strip()[:300]}")
    # 检查 gen_event 源码依赖
    run('grep -n "gen_event" /root/SOC/ly_server_src/server/Makefile 2>/dev/null', "gen_event 规则")
    # 检查 GenEventReq 符号
    run('nm -D /Server/bin/gen_event 2>/dev/null | grep "GenEventReq" | head -5', "gen_event GenEventReq 符号")

# ---- 2. 编译 bwlist ----
print("\n" + "-" * 50)
print("[2] 编译 bwlist")
print("-" * 50)

out, err = run('cd /root/SOC/ly_server_src/server && make bwlist 2>&1', "make bwlist", timeout=120)
run('ls -la /root/SOC/ly_server_src/server/bwlist 2>/dev/null', "编译结果")

# 测试
out, _ = run('/root/SOC/ly_server_src/server/bwlist 2>&1 | head -5', "测试 bwlist")
if 'symbol lookup error' not in out.lower():
    print("  bwlist 编译测试成功!")
    run('cp /root/SOC/ly_server_src/server/bwlist /Server/www/d/bwlist', "部署 bwlist")
    run('chmod +x /Server/www/d/bwlist', "设置权限")
    out, _ = run('/Server/www/d/bwlist 2>&1 | head -3', "验证部署")
    print(f"  部署验证: {'OK' if 'symbol lookup error' not in out.lower() else 'FAIL'}")
else:
    print(f"  bwlist 仍有错误: {out.strip()[:300]}")

# ---- 3. 编译所有其他未被 make all 编译的程序 ----
print("\n" + "-" * 50)
print("[3] 确保所有 WWW_EXES 和 BIN_EXES 都被编译")
print("-" * 50)

# 从 Makefile 获取所有目标
all_exes = ['auth', 'topn', 'mo', 'internalip', 'event', 'bwlist',
            'feature', 'event_feature', 'locinfo', 'geoinfo',
            'portinfo', 'ipinfo', 'config', 'threatinfo', 'threatinfopro',
            'config_pusher', 'gen_event', 'sctl', 'evidence']

for exe in all_exes:
    # 检查源码目录是否有编译好的二进制
    out, _ = run(f'ls /root/SOC/ly_server_src/server/{exe} 2>/dev/null', f"检查 {exe}")
    if not out.strip():
        # 需要编译
        print(f"  {exe} 不存在，尝试编译...")
        out, err = run(f'cd /root/SOC/ly_server_src/server && make {exe} 2>&1 | tail -5', f"make {exe}", timeout=120)
        if 'No rule' in out or 'make:' in out and 'Error' in out:
            print(f"    无法编译 {exe}: {out.strip()[:200]}")
        else:
            run(f'ls -la /root/SOC/ly_server_src/server/{exe} 2>/dev/null', f"编译结果 {exe}")

# ---- 4. 重新部署所有程序 ----
print("\n" + "-" * 50)
print("[4] 重新部署所有程序")
print("-" * 50)

www_exes = ['auth', 'topn', 'mo', 'internalip', 'event', 'bwlist',
            'feature', 'event_feature', 'locinfo', 'geoinfo',
            'portinfo', 'ipinfo', 'config', 'threatinfo', 'threatinfopro']
bin_exes = ['config_pusher', 'gen_event']

for exe in www_exes:
    out, _ = run(f'cp /root/SOC/ly_server_src/server/{exe} /Server/www/d/{exe} 2>/dev/null && chmod +x /Server/www/d/{exe}', f"部署 {exe}")
    
for exe in bin_exes:
    out, _ = run(f'cp /root/SOC/ly_server_src/server/{exe} /Server/bin/{exe} 2>/dev/null && chmod +x /Server/bin/{exe}', f"部署 {exe}")

# ---- 5. 最终验证 ----
print("\n" + "-" * 50)
print("[5] 最终验证所有程序")
print("-" * 50)

all_results = {}

# nfdump
out, _ = run('/Agent/bin/nfdump -V 2>&1 | head -2', "nfdump")
ok = 'Version' in out and 'symbol lookup error' not in out.lower()
all_results['nfdump'] = ok

# config_pusher
out, _ = run('/Server/bin/config_pusher 2>&1; echo "EXIT=$?"', "config_pusher")
ok = 'EXIT=0' in out and 'symbol lookup error' not in out.lower()
all_results['config_pusher'] = ok

# gen_event
out, _ = run('/Server/bin/gen_event 2>&1 | head -3', "gen_event")
ok = 'symbol lookup error' not in out.lower()
all_results['gen_event'] = ok

# gen_dns_event (if exists)
out, _ = run('/Server/bin/gen_dns_event 2>&1 | head -3 2>/dev/null || echo "不存在"')
if '不存在' not in out:
    ok = 'symbol lookup error' not in out.lower()
    all_results['gen_dns_event'] = ok

# WWW CGI 程序
for exe in www_exes:
    out, _ = run(f'/Server/www/d/{exe} 2>&1 | head -3', f"{exe}")
    ok = 'symbol lookup error' not in out.lower()
    all_results[exe] = ok

# 打印结果
print()
for name, ok in all_results.items():
    print(f"  {name:20s} {'OK' if ok else 'FAIL'}")

ok_count = sum(1 for v in all_results.values() if v)
total = len(all_results)
print(f"\n  验证通过: {ok_count}/{total}")

if ok_count == total:
    print("  所有程序编译部署验证通过!")
else:
    failed_list = [k for k, v in all_results.items() if not v]
    print(f"  失败: {', '.join(failed_list)}")

c.close()
