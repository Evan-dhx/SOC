import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

FORCE_DARK = '''<script id="ly-force-dark">
(function () {
    if (window.__lyForceDark) return;
    window.__lyForceDark = true;
    var link = document.getElementById('theme');
    function forceDark() {
        // 固定深色主题
        if (link && link.href && link.href.indexOf('light') !== -1) {
            link.href = './theme/dark.css';
        }
        // localStorage 强制 dark，防止刷新后恢复浅色
        try {
            var th = localStorage.getItem('theme');
            if (!th || th.indexOf('dark') === -1) localStorage.setItem('theme', 'dark');
        } catch (e) {}
    }
    // 监听主题切换按钮修改 href（立即改回深色）
    if (link) {
        var obs = new MutationObserver(function () { forceDark(); });
        obs.observe(link, { attributes: true, attributeFilter: ['href'] });
    }
    forceDark();
    if (document.readyState !== 'complete') {
        window.addEventListener('load', function () { setTimeout(forceDark, 300); });
    }
    // 轮询兜底（防 React 重渲染覆盖）
    setInterval(forceDark, 1500);
})();
</script>
'''

cmds = [
    ("注入强制深色脚本", f"""
cd /Server/www/ui
echo "=== 1. 备份 ==="
cp index.html index.html.force_dark_bak
echo "已备份 index.html.force_dark_bak"
echo ""
echo "=== 2. 注入 ly-force-dark 脚本 ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
script = {FORCE_DARK!r}
if 'ly-force-dark' in src:
    print('脚本已存在，跳过')
else:
    pos = src.find('</body>')
    if pos < 0:
        print('未找到 body 结束标记')
    else:
        src = src[:pos] + script + src[pos:]
        open('/Server/www/ui/index.html', 'w').write(src)
        print('已注入')
PYEOF
echo ""
echo "=== 3. 验证 ==="
grep -c "ly-force-dark" index.html
echo ""
echo "=== 4. 页面响应 ==="
curl -s -o /dev/null -w "/ui/: %{{http_code}}\\n" "http://127.0.0.1/ui/" --max-time 15
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()