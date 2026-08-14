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
print("完全恢复 config.js + index.html 到原始状态")
print("=" * 70)

# ---- 1. 恢复 config.js 从 bak ----
print("\n--- [1] 恢复 config.js ---")
run('cp /Server/www/ui/app-config/config.js.bak /Server/www/ui/app-config/config.js', "恢复 config.js")
run('cat /Server/www/ui/app-config/config.js', "确认 config.js")

# ---- 2. 移除 index.html 中的 moveVersion 脚本 ----
print("\n--- [2] 移除 index.html 注入脚本 ---")
# 读取当前 index.html
sftp = c.open_sftp()
with sftp.file('/Server/www/ui/index.html', 'r') as f:
    html = f.read().decode('utf-8')

# 保存原始
with sftp.file('/Server/www/ui/index.html.full_bak', 'w') as f:
    f.write(html)

# 移除 moveVersion 脚本
if 'moveVersion' in html:
    # 找到 <script> 包含 moveVersion 到 </script>
    import re
    html_clean = re.sub(r'<script>\s*\(function\(\)\{[^}]*function moveVersion[^}]*\}\)\(\);\s*</script>\s*', '', html)
    if html_clean == html:
        # 如果第一次没匹配到，尝试更宽松的匹配
        html_clean = re.sub(r'<script>[\s\S]*?moveVersion[\s\S]*?</script>\s*', '', html)
    
    # 恢复标题
    html_clean = html_clean.replace('<title>网络流量态势感知平台</title>', '<title>流影</title>')
    
    with sftp.file('/Server/www/ui/index.html', 'w') as f:
        f.write(html_clean)
    print("已移除 moveVersion 脚本并恢复标题")
else:
    print("没有 moveVersion 脚本需要移除")
sftp.close()

# ---- 3. 验证恢复结果 ----
print("\n--- [3] 验证 ---")
run('cat /Server/www/ui/app-config/config.js | grep "subName\\|version"', "config.js 版本")
run('grep -c "moveVersion" /Server/www/ui/index.html 2>/dev/null', "moveVersion 剩余次数")
run('grep -o "<title>[^<]*</title>" /Server/www/ui/index.html', "页面标题")
run('grep "FLOW SHADOW\\|NETWORK TRAFFIC" /Server/www/ui/static/js/main.ff156c89.chunk.js | head -5', "main.js 品牌")

# ---- 4. 重启 httpd ----
print("\n--- [4] 重启 httpd ---")
run('systemctl restart httpd 2>&1', "重启")

# ---- 5. 测试登录 ----
print("\n--- [5] 测试登录 ---")
run('mysql -u root -ppassword123 -e "UPDATE t_user SET pass=\'c3284d0f94606de1fd2af172aba15bf3\', lockedtime=0 WHERE name=\'admin\';" server 2>/dev/null', "重置密码")
run('mysql -u root -ppassword123 -e "DELETE FROM t_user_session;" server 2>/dev/null', "清理 session")

_, stdout, _ = c.exec_command(
    'curl -s -c /tmp/restored_cookie.txt -X POST '
    '-d "auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" '
    'http://127.0.0.1/d/login 2>&1',
    timeout=30
)
print("登录:", stdout.read().decode('utf-8', errors='replace')[:200])

_, stdout, _ = c.exec_command(
    'curl -s -b /tmp/restored_cookie.txt -X POST '
    '-d "auth_target=config&type=event&op=get" '
    'http://127.0.0.1/d/config 2>&1',
    timeout=30
)
body = stdout.read().decode('utf-8', errors='replace')
print("Config 数据:", "event_type" in body, "| 前100字:", body[:100])

c.close()
print("\n" + "=" * 70)
print("完成!")
print("=" * 70)