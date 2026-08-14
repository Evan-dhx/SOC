import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

BRAND_SCRIPT = '''<script id="ly-brand-rename">
(function () {
    if (window.__lyBrandRename) return;
    window.__lyBrandRename = true;
    function replaceText(node) {
        if (node.nodeType === 3) {
            var t = node.nodeValue;
            if (t.indexOf('流影') !== -1) {
                node.nodeValue = t.split('流影').join('天网');
            }
            return;
        }
        if (node.nodeType !== 1) return;
        var tag = node.tagName;
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'TEXTAREA' || tag === 'INPUT') return;
        if (node.classList && node.classList.contains('login-left-logo-tip')) {
            node.style.display = 'none';
            return;
        }
        var children = node.childNodes;
        for (var i = 0; i < children.length; i++) replaceText(children[i]);
    }
    function fixTitle() {
        if (document.title.indexOf('流影') !== -1) {
            document.title = document.title.split('流影').join('天网');
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

cmds = [
    ("流影→天网 改名", f"""
cd /Server/www/ui
echo "=== 1. 备份 ==="
cp index.html index.html.brand_bak
echo "已备份 index.html.brand_bak"
echo ""
echo "=== 2. 追加样式（隐藏表单标题 FLOW SHADOW）+ 改名脚本 ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
style_rule = '\\n/* 隐藏表单标题 FLOW SHADOW */\\n.login-title-logo > :last-child {{ display: none !important; }}\\n'
brand_script = {BRAND_SCRIPT!r}
changed = []
if 'login-title-logo > :last-child' in src:
    print('样式已存在')
else:
    pos = src.find('</style>')
    if pos < 0:
        print('未找到 style 结束标记')
    else:
        src = src[:pos] + style_rule + src[pos:]
        changed.append('style')
if 'ly-brand-rename' in src:
    print('改名脚本已存在')
else:
    pos = src.find('</body>')
    if pos < 0:
        print('未找到 body 结束标记')
    else:
        src = src[:pos] + brand_script + src[pos:]
        changed.append('script')
if changed:
    open('/Server/www/ui/index.html', 'w').write(src)
    print('已追加:', changed)
PYEOF
echo ""
echo "=== 3. 验证 ==="
grep -c "ly-brand-rename\|天网" /Server/www/ui/index.html
echo ""
echo "=== 4. 页面响应 + JS 引用 ==="
curl -s -o /dev/null -w "/ui/: %{{http_code}}\\n" "http://127.0.0.1/ui/" --max-time 15
curl -s "http://127.0.0.1/ui/" --max-time 15 2>&1 | grep -o "static/js/[a-z0-9.]*\\.js" | head -5
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