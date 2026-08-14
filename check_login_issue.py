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
        print(f"  STDERR: {err.strip()[:1000]}")
    return out, err

print("=" * 70)
print("检查登录问题 + 最终验证")
print("=" * 70)

# ---- 1. 检查 t_user 表 ----
print("\n--- [1] 检查 t_user 表 ---")
run('mysql -u root -ppassword123 -e "SELECT id,name,pass,level,disabled,lockedtime FROM t_user;" server 2>/dev/null', "t_user 表")
run('echo -n "admin" | md5sum', "admin 的 MD5")

# ---- 2. 解锁并清理 ----
print("\n--- [2] 解锁并清理 ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET lockedtime=0 WHERE name=\'admin\';" server 2>/dev/null', "解锁 admin")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")
run('mysql -u root -ppassword123 -e "SELECT name,lockedtime FROM t_user;" server 2>/dev/null', "解锁后状态")

# ---- 3. 清理 httpd 日志 ----
print("\n--- [3] 清理日志 ---")
run('echo "" > /var/log/httpd/ly_error_log', "清理日志")

# ---- 4. curl 登录测试 ----
print("\n--- [4] curl 登录测试 ---")
run('curl -s -v -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "admin/admin 详细")
run('cat /var/log/httpd/ly_error_log 2>/dev/null', "错误日志")

# ---- 5. 验证全部修改效果 ----
print("\n--- [5] 验证全部修改 ---")
run('curl -s http://127.0.0.1/ 2>&1 | grep -o "<title>.*</title>"', "页面标题")
run('curl -s http://127.0.0.1/ 2>&1 | grep -c "moveVersion"', "moveVersion 脚本")
run('cat /Server/www/ui/app-config/config.js | grep "subName\\|version"', "config.js 版本号")
run('grep -c "NETWORK TRAFFIC" /Server/www/ui/static/js/main.ff156c89.chunk.js', "左侧 NETWORK TRAFFIC")
run('grep -c "SITUATIONAL AWARENESS" /Server/www/ui/static/js/main.ff156c89.chunk.js', "左侧 SITUATIONAL AWARENESS")

c.close()
print("\n" + "=" * 70)
print("验证完成!")
print("=" * 70)
