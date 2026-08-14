import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 改名脚本 v3：流影/天網 → 天鯨
BRAND_V3 = '''<script id="ly-brand-rename">
(function () {
    if (window.__lyBrandRename) return;
    window.__lyBrandRename = true;
    function replaceText(node) {
        if (node.nodeType === 3) {
            var t = node.nodeValue;
            if (t.indexOf('流影') !== -1 || t.indexOf('天網') !== -1) {
                node.nodeValue = t.split('流影').join('天鯨').split('天網').join('天鯨');
            }
            return;
        }
        if (node.nodeType !== 1) return;
        var tag = node.tagName;
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'TEXTAREA' || tag === 'INPUT') return;
        var children = node.childNodes;
        for (var i = 0; i < children.length; i++) replaceText(children[i]);
    }
    function fixTitle() {
        var t = document.title;
        if (t.indexOf('流影') !== -1 || t.indexOf('天網') !== -1) {
            document.title = t.split('流影').join('天鯨').split('天網').join('天鯨');
        }
    }
    function run() {
        if (!document.body) return;
        replaceText(document.body);
        fixTitle();
    }
    run();
    if (document.readyState !== 'complete') {
        window.addEventListener('load', function () { setTimeout(run, 300); });
    }
    var obs = new MutationObserver(function () { run(); });
    if (document.body) obs.observe(document.body, { childList: true, subtree: true, characterData: true });
})();
</script>
'''

HIDE_LOGO = '''
/* ========== 隐藏左上角标题 ========== */
.login-left-top {
    display: none !important;
}
'''

cmds = [
    ("天鯨改名 + 隐藏左上角标题 + 更新 favicon", f"""
cd /Server/www/ui
echo "=== 1. 备份 ==="
cp index.html index.html.whale_bak
echo "已备份 index.html.whale_bak"
echo ""
echo "=== 2. 上传新 favicon（天鯨） ==="
echo "（由本地 SFTP 上传）"
echo ""
echo "=== 3. 替换改名脚本 + 追加隐藏样式 + favicon 版本号 ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
brand = {BRAND_V3!r}
hide = {HIDE_LOGO!r}
changed = []
# 1) 替换 ly-brand-rename 整块
start = src.find('<script id="ly-brand-rename">')
if start < 0:
    print('未找到改名脚本')
else:
    end = src.find('</script>', start) + len('</script>')
    src = src[:start] + brand + src[end:]
    changed.append('brand')
# 2) 追加隐藏左上角标题样式
if '隐藏左上角标题' in src:
    print('隐藏样式已存在')
else:
    pos = src.find('</style>')
    if pos >= 0:
        src = src[:pos] + hide + src[pos:]
        changed.append('hide')
# 3) favicon 加版本号防缓存
if 'favicon.svg?v=' in src:
    print('favicon 版本号已存在')
else:
    src = src.replace('href="./favicon.svg"', 'href="./favicon.svg?v=2"')
    changed.append('favicon')
if changed:
    open('/Server/www/ui/index.html', 'w').write(src)
    print('已完成:', changed)
PYEOF
echo ""
echo "=== 4. 验证 ==="
echo -n "天鯨: "; grep -c "天鯨" index.html
echo -n "天網: "; grep -c "天網" index.html
echo -n "隐藏左上角: "; grep -c "隐藏左上角标题" index.html
echo -n "favicon v2: "; grep -c "favicon.svg?v=2" index.html
echo ""
echo "=== 5. 页面响应 ==="
curl -s -o /dev/null -w "/ui/: %{{http_code}}\\n" "http://127.0.0.1/ui/" --max-time 15
"""),
]

# 先上传 favicon
sftp = client.open_sftp()
sftp.put(r'd:\QorderProject\SOC\favicon.svg', '/Server/www/ui/favicon.svg')
sftp.close()
print("favicon.svg（天鯨）已上传")

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()