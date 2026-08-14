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
print("搜索所有包含 '流影' 和 'Flow Shadow' 的文件")
print("=" * 70)

# ---- 1. 搜索前端 UI 目录 ----
print("\n--- [1] 前端 UI 中的 '流影' ---")
run('grep -rl "流影" /Server/www/ui/ 2>/dev/null', "包含'流影'的文件列表")

print("\n--- [2] 前端 UI 中的 'Flow Shadow' / 'flow shadow' ---")
run('grep -ril "flow.shadow" /Server/www/ui/ 2>/dev/null', "包含'flow shadow'的文件列表")
run('grep -ril "shadowflow" /Server/www/ui/ 2>/dev/null', "包含'shadowflow'的文件列表")

# ---- 2. 搜索 httpd 配置 ----
print("\n--- [3] httpd 配置中的 '流影' ---")
run('grep -rn "流影" /etc/httpd/ 2>/dev/null', "httpd 配置中的'流影'")

# ---- 3. 搜索后端源码 ----
print("\n--- [4] 后端源码中的 '流影' ---")
run('grep -rn "流影" /root/SOC/ly_server_src/ 2>/dev/null | head -20', "后端源码中的'流影'")
run('grep -rn "流影" /root/SOC/ly_analyser_src/ 2>/dev/null | head -20', "analyser 源码中的'流影'")

# ---- 4. 搜索 Server 其他目录 ----
print("\n--- [5] Server 其他目录中的 '流影' ---")
run('grep -rn "流影" /Server/etc/ 2>/dev/null', "Server etc 中的'流影'")
run('grep -rn "流影" /Server/bin/ 2>/dev/null | head -5', "Server bin 中的'流影'")

# ---- 5. 查看前端 config.js 中的品牌名称 ----
print("\n--- [6] 前端 config.js 品牌信息 ---")
run('cat /Server/www/ui/app-config/config.js 2>/dev/null', "前端配置")

# ---- 6. 查看前端 index.html 标题 ----
print("\n--- [7] 前端 index.html ---")
run('cat /Server/www/ui/index.html 2>/dev/null', "index.html")

# ---- 7. 在前端 JS 中搜索所有 '流影' 出现的位置 ----
print("\n--- [8] 前端 JS 中的 '流影' 具体位置 ---")
run('grep -n "流影" /Server/www/ui/static/js/main.*.chunk.js 2>/dev/null | head -20', "main.js 中的'流影'")
run('grep -rn "流影" /Server/www/ui/static/js/ 2>/dev/null | head -20', "static/js 中的'流影'")
run('grep -rn "流影" /Server/www/ui/static/css/ 2>/dev/null | head -10', "static/css 中的'流影'")

# ---- 8. 搜索其他文件 ----
print("\n--- [9] 其他文件中的 '流影' ---")
run('find /Server/www/ui -type f \\( -name "*.html" -o -name "*.json" -o -name "*.txt" -o -name "*.ico" -o -name "*.xml" \\) -exec grep -l "流影" {} \\; 2>/dev/null', "其他文件类型中的'流影'")

# ---- 9. 搜索 manifest.json ----
print("\n--- [10] manifest.json ---")
run('cat /Server/www/ui/manifest.json 2>/dev/null', "manifest.json")
run('cat /Server/www/ui/asset-manifest.json 2>/dev/null | head -20', "asset-manifest.json")

# ---- 10. 搜索 favicon 和其他静态资源 ----
print("\n--- [11] 静态资源目录结构 ---")
run('ls -la /Server/www/ui/ 2>/dev/null', "UI 根目录")
run('ls -la /Server/www/ui/app-config/ 2>/dev/null', "app-config 目录")

c.close()
print("\n" + "=" * 70)
print("搜索完成!")
print("=" * 70)
