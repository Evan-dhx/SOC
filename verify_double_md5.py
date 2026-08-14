import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=60):
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
print("验证双重 MD5 假设")
print("=" * 70)

# ---- 1. 计算双重 MD5 ----
print("\n--- [1] 计算双重 MD5 ---")
run('echo -n "admin" | md5sum', "第一层 MD5(admin)")
run('echo -n "21232f297a57a5a743894a0e4a801fc3" | md5sum', "第二层 MD5(MD5(admin))")

# ---- 2. 对比数据库中的原始密码 ----
print("\n--- [2] 数据库中 admin 原始密码 ---")
run('mysql -u root -ppassword123 -e "SELECT name,pass FROM t_user;" server 2>/dev/null', "当前密码")

# ---- 3. 检查 qi 函数定义 ----
print("\n--- [3] 搜索 qi 函数定义 ---")
run('grep -oP "function qi\\(.{0,200}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -5', "qi 函数")
run('grep -oP "qi=function.{0,200}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -5', "qi 赋值")
run('grep -oP "var qi.{0,200}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -5', "var qi")

# ---- 4. 搜索 md5 在 main.js 中的使用 ----
print("\n--- [4] 搜索 md5 相关 ---")
run('grep -oP ".{0,60}md5.{0,60}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "md5 引用")
run('grep -oP ".{0,60}Md5.{0,60}" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -10', "Md5 引用")

# ---- 5. 搜索 2.2db6edf7.chunk.js 中的 md5 ----
print("\n--- [5] 搜索 vendor chunk 中的 md5 ---")
run('grep -oP ".{0,80}md5.{0,80}" /Server/www/ui/static/js/2.2db6edf7.chunk.js | head -10', "vendor md5")

# ---- 6. 如果双重 MD5 成立，恢复正确密码 ----
print("\n--- [6] 恢复正确密码 ---")
# MD5(MD5("admin")) 应该等于原始密码 c3284d0f94606de1fd2af172aba15bf3
# 先验证
run('echo -n "21232f297a57a5a743894a0e4a801fc3" | md5sum | awk \'{print $1}\'', "MD5(MD5(admin)) 计算结果")
run('echo "原始密码: c3284d0f94606de1fd2af172aba15bf3"', "原始密码")

# 恢复原始密码
run('mysql -u root -ppassword123 -e "UPDATE t_user SET pass=\'c3284d0f94606de1fd2af172aba15bf3\', lockedtime=0 WHERE name=\'admin\';" server 2>/dev/null', "恢复原始密码")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")
run('mysql -u root -ppassword123 -e "SELECT name,pass,lockedtime FROM t_user;" server 2>/dev/null', "恢复后状态")

# ---- 7. 测试登录 ----
print("\n--- [7] 测试登录 ---")
# curl 模拟浏览器（前端先做 MD5，发送 MD5 后的值）
run('curl -s -X POST -d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3&auth_target=login" http://127.0.0.1/d/login 2>&1', "模拟浏览器登录(MD5后)")
# curl 直接明文
run('curl -s -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "明文登录")

c.close()
print("\n" + "=" * 70)
print("验证完成!")
print("=" * 70)
