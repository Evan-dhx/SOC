import paramiko
import sys
import time

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
# 待办 3: CGI 程序全量重新编译并验证
# =====================================================================
print("=" * 70)
print("待办 3: CGI 程序全量重新编译并验证")
print("=" * 70)

# ---- 3.1 nfdump 全量重新编译 ----
print("\n" + "-" * 50)
print("[3.1] nfdump 全量重新编译")
print("-" * 50)

out, err = run('cd /root/SOC/ly_analyser_src/nfdump/bin && make clean 2>&1 | tail -3', "nfdump make clean")
out, err = run('cd /root/SOC/ly_analyser_src/nfdump/bin && make nfdump 2>&1 | tail -10', "nfdump make", timeout=180)
nfdump_build_ok = 'error' not in out.lower() or 'Error' not in out

if nfdump_build_ok:
    run('ls -la /root/SOC/ly_analyser_src/nfdump/bin/nfdump', "编译结果")
    # 测试
    out, _ = run('/root/SOC/ly_analyser_src/nfdump/bin/nfdump -V 2>&1', "nfdump -V 测试")
    nfdump_test_ok = 'Version' in out and 'symbol lookup error' not in out.lower()
    if nfdump_test_ok:
        # 部署
        run('cp /root/SOC/ly_analyser_src/nfdump/bin/nfdump /Agent/bin/nfdump', "部署 nfdump")
        run('chmod +x /Agent/bin/nfdump', "设置权限")
        out, _ = run('/Agent/bin/nfdump -V 2>&1', "验证部署")
        print(f"  nfdump: {'OK' if 'Version' in out else 'FAIL'}")
    else:
        print(f"  nfdump 测试失败: {out.strip()[:300]}")
else:
    print(f"  nfdump 编译失败: {out[-500:]}")

# ---- 3.2 Server CGI 全量重新编译 ----
print("\n" + "-" * 50)
print("[3.2] Server CGI 全量重新编译")
print("-" * 50)

out, err = run('cd /root/SOC/ly_server_src/server && make clean 2>&1 | tail -5', "Server make clean")
out, err = run('cd /root/SOC/ly_server_src/server && make 2>&1 | tail -30', "Server make all", timeout=300)

# 检查编译是否成功
build_ok = 'Error' not in out and 'error:' not in out
if not build_ok:
    print(f"  编译可能有错误，检查详情...")
    # 显示错误行
    for line in out.split('\n'):
        if 'error' in line.lower():
            print(f"  ERROR: {line}")

# ---- 3.3 部署所有编译成功的程序 ----
print("\n" + "-" * 50)
print("[3.3] 部署所有程序")
print("-" * 50)

# WWW CGI 程序
www_exes = ['auth', 'topn', 'mo', 'internalip', 'event', 'bwlist',
            'feature', 'event_feature', 'locinfo', 'geoinfo',
            'portinfo', 'ipinfo', 'config', 'threatinfo', 'threatinfopro']
# BIN 程序
bin_exes = ['config_pusher', 'gen_event']

deployed = []
failed = []

for exe in www_exes:
    out, _ = run(f'ls -la /root/SOC/ly_server_src/server/{exe} 2>/dev/null', f"检查 {exe}")
    if out.strip():
        run(f'cp /root/SOC/ly_server_src/server/{exe} /Server/www/d/{exe}', f"部署 {exe}")
        run(f'chmod +x /Server/www/d/{exe}', f"权限 {exe}")
        deployed.append(exe)
    else:
        failed.append(exe)

for exe in bin_exes:
    out, _ = run(f'ls -la /root/SOC/ly_server_src/server/{exe} 2>/dev/null', f"检查 {exe}")
    if out.strip():
        run(f'cp /root/SOC/ly_server_src/server/{exe} /Server/bin/{exe}', f"部署 {exe}")
        run(f'chmod +x /Server/bin/{exe}', f"权限 {exe}")
        deployed.append(exe)
    else:
        failed.append(exe)

print(f"\n  部署成功: {len(deployed)} 个程序: {', '.join(deployed)}")
if failed:
    print(f"  部署失败: {', '.join(failed)}")

# ---- 3.4 逐一验证每个程序 ----
print("\n" + "-" * 50)
print("[3.4] 逐一验证每个程序 (检查 symbol lookup error)")
print("-" * 50)

all_results = {}

# nfdump
out, _ = run('/Agent/bin/nfdump -V 2>&1 | head -2', "nfdump")
ok = 'Version' in out and 'symbol lookup error' not in out.lower()
all_results['nfdump'] = ok
print(f"  nfdump:              {'OK' if ok else 'FAIL'}")

# config_pusher
out, _ = run('/Server/bin/config_pusher 2>&1; echo "EXIT=$?"', "config_pusher")
ok = 'EXIT=0' in out and 'symbol lookup error' not in out.lower()
all_results['config_pusher'] = ok
print(f"  config_pusher:      {'OK' if ok else 'FAIL'}")

# gen_event
out, _ = run('/Server/bin/gen_event 2>&1 | head -3', "gen_event")
ok = 'symbol lookup error' not in out.lower()
all_results['gen_event'] = ok
print(f"  gen_event:          {'OK' if ok else 'FAIL'}")

# WWW CGI 程序 - 检查 symbol lookup error
for exe in www_exes:
    out, _ = run(f'/Server/www/d/{exe} 2>&1 | head -3', f"{exe}")
    ok = 'symbol lookup error' not in out.lower()
    all_results[exe] = ok
    print(f"  {exe:20s} {'OK' if ok else 'FAIL'}")

# ---- 3.5 检查 ldd 依赖 ----
print("\n" + "-" * 50)
print("[3.5] 检查程序依赖 (not found)")
print("-" * 50)

check_progs = ['/Agent/bin/nfdump', '/Server/bin/config_pusher', '/Server/bin/gen_event',
               '/Server/www/d/auth', '/Server/www/d/topn']
for prog in check_progs:
    out, _ = run(f'ldd {prog} 2>&1 | grep "not found"', f"依赖检查 {prog.split('/')[-1]}")
    if out.strip():
        print(f"  {prog}: 有缺失依赖!")
        print(f"    {out.strip()}")
    else:
        print(f"  {prog}: 依赖完整")

# ---- 3.6 总结 ----
print("\n" + "-" * 50)
print("[3.6] 待办 3 总结")
print("-" * 50)
ok_count = sum(1 for v in all_results.values() if v)
total = len(all_results)
print(f"  验证通过: {ok_count}/{total}")
if ok_count == total:
    print("  所有程序编译部署验证通过!")
else:
    failed_list = [k for k, v in all_results.items() if not v]
    print(f"  失败: {', '.join(failed_list)}")

c.close()
