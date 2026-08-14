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
        print(out.strip()[:8000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:2000]}")
    return out, err

print("=" * 70)
print("检查 auth.cpp 密码验证逻辑 + 修复登录")
print("=" * 70)

# ---- 1. 检查 auth.cpp 密码验证逻辑 ----
print("\n--- [1] auth.cpp 密码验证相关代码 ---")
run('grep -n "MD5\\|md5\\|pass\\|check_user" /root/SOC/ly_server_src/server/auth.cpp | head -40', "auth.cpp 密码相关行")

# ---- 2. 检查密码哈希 ----
print("\n--- [2] 密码哈希对比 ---")
run('echo -n "admin" | md5sum', "MD5(admin)")
run('echo -n "PP@ssw0rd" | md5sum', "MD5(PP@ssw0rd)")
run('echo -n "password123" | md5sum', "MD5(password123)")
run('echo -n "admin123" | md5sum', "MD5(admin123)")

# ---- 3. 检查数据库密码 ----
print("\n--- [3] 数据库密码 ---")
run('mysql -u root -ppassword123 -e "SELECT name,pass FROM t_user;" server 2>/dev/null', "t_user 密码")

# ---- 4. 检查 auth.cpp 中完整的 check_user_pass 函数 ----
print("\n--- [4] check_user_pass 函数完整代码 ---")
run('sed -n "/check_user_pass/,/^}/p" /root/SOC/ly_server_src/server/auth.cpp', "check_user_pass 函数")

# ---- 5. 重置 admin 密码为 admin ----
print("\n--- [5] 重置 admin 密码为 admin ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET pass=\'21232f297a57a5a743894a0e4a801fc3\', lockedtime=0 WHERE name=\'admin\';" server 2>/dev/null', "重置密码")
run('mysql -u root -ppassword123 -e "SELECT name,pass,lockedtime FROM t_user WHERE name=\'admin\';" server 2>/dev/null', "重置后状态")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")

# ---- 6. 测试登录 ----
print("\n--- [6] 测试登录 ---")
run('curl -s -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "admin/admin 登录")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)
