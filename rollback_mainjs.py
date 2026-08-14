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
    if label: print(f"[{label}]")
    if out.strip(): print(out.strip()[:5000])
    if err.strip(): print(f"  STDERR: {err.strip()[:1000]}")
    return out, err

print("=" * 70)
print("回滚 main.js 恢复原始版本 + 测试登录")
print("=" * 70)

# ---- 1. 备份当前 main.js（如果尚未备份） ----
print("\n--- [1] 备份当前 main.js ---")
run('cp /Server/www/ui/static/js/main.ff156c89.chunk.js /Server/www/ui/static/js/main.ff156c89.chunk.js.modified_bak', "备份当前")

# ---- 2. 从 .bak 恢复原始 main.js ----
print("\n--- [2] 恢复 bak 到 main.js ---")
run('cp /Server/www/ui/static/js/main.ff156c89.chunk.js.bak /Server/www/ui/static/js/main.ff156c89.chunk.js', "恢复原始")
run('ls -la /Server/www/ui/static/js/main.ff156c89.chunk.js', "确认恢复")

# ---- 3. 验证 config.js 和 index.html 修改仍在 ----
print("\n--- [3] 验证 config.js 和 index.html ---")
run('grep "version" /Server/www/ui/app-config/config.js', "config.js version")
run('grep "subName" /Server/www/ui/app-config/config.js', "config.js subName")
run('grep -c "网络流量态势感知平台" /Server/www/ui/index.html', "index.html 标题")
run('grep -c "moveVersion" /Server/www/ui/index.html', "moveVersion 脚本")

# ---- 4. 重置 admin 密码（双重 MD5） ----
print("\n--- [4] 确保 admin 密码正确 ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET pass=\'c3284d0f94606de1fd2af172aba15bf3\', lockedtime=0 WHERE name=\'admin\';" server 2>/dev/null', "重置密码")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")
run('mysql -u root -ppassword123 -e "SELECT name,pass,lockedtime FROM t_user;" server 2>/dev/null', "确认状态")

# ---- 5. 重启 httpd ----
print("\n--- [5] 重启 httpd ---")
run('systemctl restart httpd 2>&1', "重启")

# ---- 6. 测试完整浏览器流程（带 cookie 持久化） ----
print("\n--- [6] Python 完整流测试 ---")
sftp = c.open_sftp()
with sftp.file('/tmp/test_rollback.py', 'w') as f:
    f.write("""import urllib.request, http.cookiejar
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Step 1: Pre-login config (simulates browser page load)
print("=== Step 1: Pre-login config ===")
data = b"auth_target=config&type=event&op=get"
req = urllib.request.Request("http://127.0.0.1/d/config", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
try: 
    resp = opener.open(req)
    print("Response:", resp.read().decode()[:100])
except Exception as e:
    print("Error:", e)
for c in cj:
    print("  Cookie:", c.name, "=", c.value, "domain:", c.domain)

# Step 2: Login
print()
print("=== Step 2: Login ===")
data = b"auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3"
req = urllib.request.Request("http://127.0.0.1/d/login", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
resp = opener.open(req)
print("Login:", resp.read().decode())
for c in cj:
    print("  Cookie:", c.name, "=", c.value)

# Step 3: Config after login
print()
print("=== Step 3: Config after login ===")
data = b"auth_target=config&type=event&op=get"
req = urllib.request.Request("http://127.0.0.1/d/config", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
resp = opener.open(req)
body = resp.read().decode()
print("Config:", body[:200])
print("Has data:", "event_type" in body)
""")
sftp.close()
run('python3 /tmp/test_rollback.py 2>&1', "Python 流测试")

# ---- 7. curl 直接测试 ----
print("\n--- [7] curl 模拟浏览器登录 ---")
_, stdout, _ = c.exec_command(
    'curl -s -v -c /tmp/rollback_cookie.txt -X POST '
    '-d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" '
    '-H "Accept: application/json, text/plain, */*" '
    '-H "Content-Type: application/x-www-form-urlencoded" '
    'http://10.10.102.220/d/login 2>&1',
    timeout=30
)
print("登录（通过 10.10.102.220）:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

# 检查 cookie
_, stdout, _ = c.exec_command('cat /tmp/rollback_cookie.txt 2>/dev/null', timeout=10)
print("\nCookie 文件:")
print(stdout.read().decode('utf-8', errors='replace')[:2000])

c.close()
print("\n" + "=" * 70)
print("回滚完成，等待浏览器测试!")
print("=" * 70)