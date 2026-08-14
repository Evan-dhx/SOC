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
print("诊断登录报错")
print("=" * 70)

# ---- 1. 检查 admin 锁定状态 ----
print("\n--- [1] 检查 admin 状态 ---")
run('mysql -u root -ppassword123 -e "SELECT id,name,pass,lockedtime,disabled FROM t_user;" server 2>/dev/null', "t_user 表")

# ---- 2. 解锁 admin + 重置密码 ----
print("\n--- [2] 解锁 + 重置密码 ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET pass=\'21232f297a57a5a743894a0e4a801fc3\', lockedtime=0 WHERE name=\'admin\';" server 2>/dev/null', "重置密码+解锁")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")
run('mysql -u root -ppassword123 -e "SELECT name,pass,lockedtime FROM t_user WHERE name=\'admin\';" server 2>/dev/null', "重置后状态")

# ---- 3. 检查 httpd 错误日志 ----
print("\n--- [3] httpd 错误日志 ---")
run('tail -30 /var/log/httpd/ly_error_log 2>/dev/null', "最近错误日志")

# ---- 4. 检查 httpd access 日志 ----
print("\n--- [4] httpd access 日志 ---")
run('tail -20 /var/log/httpd/ly_access_log 2>/dev/null || tail -20 /var/log/httpd/access_log 2>/dev/null', "最近访问日志")

# ---- 5. curl 登录测试 ----
print("\n--- [5] curl 登录测试 ---")
run('curl -s -v -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "admin/admin 详细")

# ---- 6. 检查 auth CGI 是否存在 ----
print("\n--- [6] 检查 auth CGI ---")
run('ls -la /Server/www/d/auth 2>/dev/null', "auth 文件")
run('file /Server/www/d/auth 2>/dev/null', "auth 类型")

# ---- 7. 检查 httpd 配置 ----
print("\n--- [7] httpd 配置 ---")
run('cat /etc/httpd/conf.d/ly_server.conf', "ly_server.conf")

# ---- 8. 重启 httpd ----
print("\n--- [8] 重启 httpd ---")
run('systemctl restart httpd 2>&1', "重启")
import time
time.sleep(2)
run('curl -s -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "重启后登录测试")

c.close()
print("\n" + "=" * 70)
print("诊断完成!")
print("=" * 70)
