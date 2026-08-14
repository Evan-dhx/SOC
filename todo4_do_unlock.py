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
print("解锁 admin 账号并验证登录")
print("=" * 70)

# ---- 1. 解锁前状态 ----
print("\n--- [1] 解锁前状态 ---")
run('mysql -u root -ppassword123 -e "SELECT id,name,level,disabled,lockedtime FROM t_user WHERE name=\'admin\';" server 2>/dev/null', "admin 锁定状态")

# ---- 2. 查看 auth.cpp 完整登录验证逻辑 ----
print("\n--- [2] auth.cpp 登录验证逻辑（第200-230行）---")
run('sed -n "200,240p" /root/SOC/ly_server_src/server/auth.cpp 2>/dev/null', "登录验证逻辑")

# ---- 3. 解锁 admin 账号 ----
print("\n--- [3] 解锁 admin 账号 ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET lockedtime=0 WHERE name=\'admin\';" server 2>/dev/null', "执行解锁")
run('mysql -u root -ppassword123 -e "SELECT id,name,level,disabled,lockedtime FROM t_user WHERE name=\'admin\';" server 2>/dev/null', "解锁后状态")

# ---- 4. 清理旧 session ----
print("\n--- [4] 清理旧 session ---")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session 表")

# ---- 5. 验证登录 ----
print("\n--- [5] 验证 admin/admin 登录 ---")
run('echo "" > /var/log/httpd/ly_error_log', "清理日志")
run('curl -s -v -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "POST 登录 admin/admin")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "错误日志")

# ---- 6. 使用 session 测试 API ----
print("\n--- [6] 使用 session 测试 ---")
run('curl -s -c /tmp/cookies2.txt -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "登录获取 session")
run('curl -s -b /tmp/cookies2.txt "http://127.0.0.1/d/auth?auth_target=auth_status" 2>&1', "auth_status")
run('curl -s -b /tmp/cookies2.txt -X POST -d "auth_target=mo&op=get" http://127.0.0.1/d/auth 2>&1 | head -3', "mo get")

# ---- 7. 验证其他用户也能登录 ----
print("\n--- [7] 验证其他用户 ---")
run('curl -s -X POST -d "auth_user=analyser&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "analyser/admin")
run('curl -s -X POST -d "auth_user=viewer&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "viewer/admin")

# ---- 8. 清理日志 ----
run('echo "=== UNLOCK DONE $(date) ===" > /var/log/httpd/ly_error_log', "清理日志")

c.close()
print("\n" + "=" * 70)
print("解锁完成!")
print("=" * 70)
