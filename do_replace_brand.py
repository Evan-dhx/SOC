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
        print(out.strip()[:10000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:2000]}")
    return out, err

print("=" * 70)
print("替换品牌名称：流影 → 网络流量态势感知平台")
print("              FLOW SHADOW → NETWORK TRAFFIC SITUATIONAL AWARENESS PLATFORM")
print("=" * 70)

# Unicode 编码:
# 流影 = \u6d41\u5f71
# 网络流量态势感知平台 = \u7f51\u7edc\u6d41\u91cf\u6001\u52bf\u611f\u77e5\u5e73\u53f0

# ---- 1. 备份原文件 ----
print("\n--- [1] 备份原文件 ---")
run('cp /Server/www/ui/index.html /Server/www/ui/index.html.bak', "备份 index.html")
run('cp /Server/www/ui/static/js/main.ff156c89.chunk.js /Server/www/ui/static/js/main.ff156c89.chunk.js.bak', "备份 main.js")
run('cp /Server/www/ui/app-config/config.js /Server/www/ui/app-config/config.js.bak', "备份 config.js")

# ---- 2. 替换 index.html 中的 <title>流影</title> ----
print("\n--- [2] 替换 index.html ---")
run('sed -i "s/<title>流影<\\/title>/<title>网络流量态势感知平台<\\/title>/" /Server/www/ui/index.html', "替换 title")
run('grep -o "<title>.*</title>" /Server/www/ui/index.html', "验证 title")

# ---- 3. 替换 main.js 中的 Unicode 品牌名 ----
print("\n--- [3] 替换 main.js 中的品牌名 ---")
# 替换 \u6d41\u5f71 (流影) → \u7f51\u7edc\u6d41\u91cf\u6001\u52bf\u611f\u77e5\u5e73\u53f0 (网络流量态势感知平台)
run(r'''sed -i 's/\\u6d41\\u5f71/\\u7f51\\u7edc\\u6d41\\u91cf\\u6001\\u52bf\\u611f\\u77e5\\u5e73\\u53f0/g' /Server/www/ui/static/js/main.ff156c89.chunk.js''', "替换中文品牌名")

# 替换 FLOW SHADOW → NETWORK TRAFFIC SITUATIONAL AWARENESS PLATFORM
run('sed -i "s/FLOW SHADOW/NETWORK TRAFFIC SITUATIONAL AWARENESS PLATFORM/g" /Server/www/ui/static/js/main.ff156c89.chunk.js', "替换英文品牌名")

# ---- 4. 验证替换结果 ----
print("\n--- [4] 验证替换结果 ---")
run('grep -o ".\\{0,30\\}网络流量态势感知平台.\\{0,30\\}" /Server/www/ui/index.html 2>/dev/null', "index.html 中的新名称")
run('grep -o ".\\{0,20\\}NETWORK TRAFFIC.\\{0,30\\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5', "main.js 中的新英文名")
run('grep -c "\\\\u7f51\\\\u7edc\\\\u6d41\\\\u91cf\\\\u6001\\\\u52bf\\\\u611f\\\\u77e5\\\\u5e73\\\\u53f0" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null', "main.js 中文品牌替换计数")
run('grep -c "FLOW SHADOW" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null', "main.js 残留 FLOW SHADOW 计数（应为0）")

# ---- 5. 检查是否还有残留的"流影" ----
print("\n--- [5] 检查残留 ---")
run('grep -rn "流影" /Server/www/ui/index.html 2>/dev/null', "index.html 残留流影")
run('grep -c "\\\\u6d41\\\\u5f71" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null', "main.js 残留流影Unicode（应为0）")

# ---- 6. 重启 httpd 使更改生效 ----
print("\n--- [6] 重启 httpd ---")
run('systemctl restart httpd 2>&1', "重启 httpd")
run('systemctl status httpd 2>&1 | head -5', "httpd 状态")

# ---- 7. 验证前端页面 ----
print("\n--- [7] 验证前端页面 ---")
run('curl -s http://127.0.0.1/ 2>&1 | grep -o "<title>.*</title>"', "页面标题")
run('curl -s -o /dev/null -w "HTTP_CODE=%{http_code}" http://127.0.0.1/ 2>&1', "首页 HTTP 状态")

# ---- 8. 验证登录功能仍正常 ----
print("\n--- [8] 验证登录功能 ---")
run('curl -s -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "admin 登录测试")

c.close()
print("\n" + "=" * 70)
print("替换完成!")
print("=" * 70)
