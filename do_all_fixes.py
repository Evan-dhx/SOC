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
print("执行全部修改：左侧品牌 + 版本号 + 位置")
print("=" * 70)

# ---- 1. 替换左侧 FLOW/SHADOW ----
print("\n--- [1] 替换左侧 FLOW/SHADOW ---")
# children:"FLOW" → children:"NETWORK TRAFFIC"
run('sed -i \'s/{children:"FLOW"}/{children:"NETWORK TRAFFIC"}/g\' /Server/www/ui/static/js/main.ff156c89.chunk.js', "替换 FLOW")
# children:"SHADOW" → children:"SITUATIONAL AWARENESS"
run('sed -i \'s/{children:"SHADOW"}/{children:"SITUATIONAL AWARENESS"}/g\' /Server/www/ui/static/js/main.ff156c89.chunk.js', "替换 SHADOW")
# 验证
run('grep -o "NETWORK TRAFFIC" /Server/www/ui/static/js/main.ff156c89.chunk.js | wc -l', "NETWORK TRAFFIC 计数")
run('grep -o "SITUATIONAL AWARENESS" /Server/www/ui/static/js/main.ff156c89.chunk.js | wc -l', "SITUATIONAL AWARENESS 计数")
run('grep -c \'"FLOW"\' /Server/www/ui/static/js/main.ff156c89.chunk.js', "残留 FLOW（应为0或只有FLOW_CANCELLED）")
run('grep -c \'"SHADOW"\' /Server/www/ui/static/js/main.ff156c89.chunk.js', "残留 SHADOW（应为0）")

# ---- 2. 修改 config.js 版本号 ----
print("\n--- [2] 修改 config.js 版本号 ---")
# subName: '开源版' → subName: ''
run("sed -i \"s/subName: '开源版'/subName: ''/\" /Server/www/ui/app-config/config.js", "清空 subName")
# version: '1.0.2' → version: '1.1.1'
run("sed -i \"s/version: '1.0.2'/version: '1.1.1'/\" /Server/www/ui/app-config/config.js", "修改版本号")
run('cat /Server/www/ui/app-config/config.js', "修改后 config.js")

# ---- 3. 搜索版本号在 main.js 中的渲染位置 ----
print("\n--- [3] 搜索版本号渲染位置 ---")
# 直接用 python3 在远程搜索
run("""python3 -c "
import re
with open('/Server/www/ui/static/js/main.ff156c89.chunk.js','r') as f:
    s = f.read()
# 搜索 version-text 出现的位置
for m in re.finditer(r'.{0,200}version-text.{0,200}', s):
    print('version-text:', m.group()[:400])
    print()
# 搜索 subName 和 version 的使用
for m in re.finditer(r'.{0,100}subName.{0,100}', s):
    print('subName:', m.group()[:200])
    print()
for m in re.finditer(r'Wa.*Ga.*version', s):
    print('Wa/Ga:', s[max(0,m.start()-50):m.end()+200])
    print()
# 搜索 login-btn
for m in re.finditer(r'.{0,150}login-btn.{0,150}', s):
    print('login-btn:', m.group()[:300])
    print()
# 搜索 version-text class
for m in re.finditer(r'.{0,100}version-text.{0,200}', s):
    print('version-text context:', m.group()[:300])
""", "Python 搜索版本号位置", timeout=30)

# ---- 4. 解锁 admin ----
print("\n--- [4] 解锁 admin ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET lockedtime=0;" server 2>/dev/null', "解锁")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")

# ---- 5. 重启 httpd ----
print("\n--- [5] 重启 httpd ---")
run('systemctl restart httpd 2>&1', "重启")
run('curl -s -o /dev/null -w "HTTP_CODE=%{http_code}" http://127.0.0.1/ 2>&1', "首页状态")
run('curl -s http://127.0.0.1/ 2>&1 | grep -o "<title>.*</title>"', "页面标题")

c.close()
print("\n" + "=" * 70)
print("修改完成!")
print("=" * 70)
