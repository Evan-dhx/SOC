import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=30):
    _, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        print(f"[{label}]")
    if out.strip():
        print(out.strip()[:5000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:2000]}")
    return out, err

print("=" * 70)
print("检查并解锁被锁定的账号")
print("=" * 70)

# ---- 1. 检查 t_user 表 lockedtime ----
print("\n--- [1] t_user 表 lockedtime 状态 ---")
run('mysql -u root -ppassword123 -e "SELECT id,name,pass,level,disabled,lockedtime FROM t_user;" server 2>/dev/null', "t_user 全部用户")

# ---- 2. 检查 do_login 函数中的锁定逻辑 ----
print("\n--- [2] do_login 锁定逻辑 ---")
run('sed -n "244,340p" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "do_login 函数")

# ---- 3. 搜索 auth.cpp 和 dbc.cpp 中的锁定相关代码 ----
print("\n--- [3] 锁定相关代码 ---")
run('grep -n "lock\\|LOCK\\|304\\|CODE_LOCK\\|lockedtime\\|locked" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "auth.cpp 锁定相关")
run('grep -n "lock\\|LOCK\\|304\\|CODE_LOCK\\|lockedtime\\|locked" /root/SOC/ly_server_src/server/dbc.cpp 2>/dev/null', "dbc.cpp 锁定相关")

# ---- 4. 查看 dbc.cpp 中用户验证函数 ----
print("\n--- [4] dbc.cpp 用户验证 ---")
run('grep -n "login\\|verify\\|check_user\\|t_user\\|pass\\|lock" /root/SOC/ly_server_src/server/dbc.cpp 2>/dev/null | head -30', "dbc.cpp 用户验证")

# 查看完整的用户验证函数
out, _ = run('grep -n "int.*login\\|int.*verify\\|int.*check.*user\\|bool.*login\\|bool.*verify" /root/SOC/ly_server_src/server/dbc.cpp 2>/dev/null', "查找验证函数定义")
if out.strip():
    for line_info in out.strip().split('\n')[:3]:
        ln = int(line_info.split(':')[0])
        run(f'sed -n "{ln-2},{ln+60}p" /root/SOC/ly_server_src/server/dbc.cpp 2>/dev/null', f"dbc.cpp 行 {ln} 上下文")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)
