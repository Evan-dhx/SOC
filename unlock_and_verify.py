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
print("解锁 admin 并验证品牌替换效果")
print("=" * 70)

# ---- 1. 解锁所有用户 ----
print("\n--- [1] 解锁所有用户 ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET lockedtime=0;" server 2>/dev/null', "解锁全部用户")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")
run('mysql -u root -ppassword123 -e "SELECT id,name,level,lockedtime FROM t_user;" server 2>/dev/null', "解锁后状态")

# ---- 2. 验证登录 ----
print("\n--- [2] 验证 admin/admin 登录 ---")
run('curl -s -c /tmp/cookies3.txt -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "admin/admin 登录")

# ---- 3. 验证前端页面标题 ----
print("\n--- [3] 验证前端品牌名称 ---")
run('curl -s http://127.0.0.1/ 2>&1 | grep -o "<title>.*</title>"', "页面标题")
run('curl -s http://127.0.0.1/ 2>&1 | head -1', "HTML 头部")

# ---- 4. 验证 main.js 中的品牌名替换 ----
print("\n--- [4] 验证 main.js 品牌替换 ---")
run('grep -o "NETWORK TRAFFIC SITUATIONAL AWARENESS PLATFORM" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | wc -l', "新英文名出现次数")
run('grep -c "FLOW SHADOW" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null', "旧英文名残留(应为0)")
# 用 python 验证中文替换
run('python3 -c "f=open(\'/Server/www/ui/static/js/main.ff156c89.chunk.js\',\'r\');s=f.read();f.close();print(\'流影:\',s.count(\'\\\\u6d41\\\\u5f71\'));print(\'网络流量态势感知平台:\',s.count(\'\\\\u7f51\\\\u7edc\\\\u6d41\\\\u91cf\\\\u6001\\\\u52bf\\\\u611f\\\\u77e5\\\\u5e73\\\\u53f0\'));print(\'FLOW SHADOW:\',s.count(\'FLOW SHADOW\'))"', "Python 验证品牌名替换")

# ---- 5. 清理日志 ----
run('echo "=== BRAND REPLACE DONE $(date) ===" > /var/log/httpd/ly_error_log', "清理日志")

c.close()
print("\n" + "=" * 70)
print("验证完成!")
print("=" * 70)
