import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ============ v2 科技风样式 ============
STYLE_V2 = '''
<style id="ly-tech-v2">
/* ========== 天網 科技风登录界面 v2 ========== */
body, #root {
    background: #0B1220 !important;
}
.login-page {
    background: radial-gradient(ellipse at 15% 0%, #14294a 0%, #0b1220 55%, #070d19 100%) !important;
    position: relative;
    overflow: hidden;
}
/* 网格背景 */
.login-page::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        linear-gradient(rgba(0, 229, 255, 0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 229, 255, 0.06) 1px, transparent 1px);
    background-size: 44px 44px;
    pointer-events: none;
    z-index: 1;
}
/* 扫描光带 */
.login-page::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.7), transparent);
    animation: ly-scan 6s linear infinite;
    pointer-events: none;
    z-index: 2;
}
@keyframes ly-scan {
    0% { top: -2px; opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { top: 100%; opacity: 0; }
}
.ly-net-canvas {
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
}
/* 左侧品牌区 */
.login_left {
    background: transparent !important;
    z-index: 3;
}
/* 删除左侧能力列表（4 行整块） */
.login-left-center {
    display: none !important;
}
.login-left-logo {
    color: #7df9ff !important;
    text-shadow: 0 0 10px rgba(0, 229, 255, 0.9), 0 0 26px rgba(0, 229, 255, 0.45) !important;
    letter-spacing: 4px !important;
    font-size: 1.7rem !important;
}
.login-left-logo-tip {
    display: none !important;
}
/* 右侧登录区 */
.login_right {
    background: transparent !important;
    z-index: 3;
}
.login-form {
    background: rgba(7, 18, 36, 0.78);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(0, 229, 255, 0.3);
    border-radius: 16px;
    padding: 46px 42px 30px;
    box-shadow:
        0 0 44px rgba(0, 229, 255, 0.12),
        inset 0 0 32px rgba(0, 229, 255, 0.05);
    width: 55%;
    max-width: 420px;
}
.login-title {
    margin-bottom: 30px;
}
.login-title-logo :first-child {
    color: #7df9ff !important;
    font-size: 2.1rem !important;
    letter-spacing: 12px !important;
    text-indent: 6px;
    text-shadow: 0 0 12px rgba(0, 229, 255, 0.9), 0 0 34px rgba(0, 229, 255, 0.4) !important;
}
.login-title-logo :last-child {
    display: none !important;
}
/* 版本徽标 */
.version-text {
    background: rgba(0, 229, 255, 0.08) !important;
    border: 1px solid rgba(0, 229, 255, 0.45) !important;
    color: #7df9ff !important;
    border-radius: 12px !important;
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.25);
}
/* 表单标签 */
.login-form .ant-form-item-label > label {
    color: rgba(210, 235, 255, 0.8) !important;
    letter-spacing: 2px;
}
/* 输入框 */
.login-form .ant-input-affix-wrapper,
.login-form .ant-input {
    background: rgba(3, 14, 30, 0.9) !important;
    border: 1px solid rgba(0, 229, 255, 0.28) !important;
    color: #e0f7ff !important;
    border-radius: 8px !important;
    transition: all 0.3s;
}
.login-form .ant-input-affix-wrapper:hover,
.login-form .ant-input:hover,
.login-form .ant-input-affix-wrapper:focus-within {
    border-color: #00e5ff !important;
    box-shadow: 0 0 14px rgba(0, 229, 255, 0.3) !important;
    background: rgba(4, 20, 42, 0.95) !important;
}
.login-form .ant-input::placeholder {
    color: rgba(150, 200, 230, 0.45) !important;
}
.login-form .anticon {
    color: rgba(0, 229, 255, 0.75) !important;
}
/* 登录按钮 */
.login-form-button {
    background: linear-gradient(90deg, #0072ff, #00e5ff) !important;
    border: none !important;
    height: 46px !important;
    font-size: 16px !important;
    letter-spacing: 6px !important;
    border-radius: 10px !important;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.35) !important;
    transition: all 0.3s !important;
}
.login-form-button:hover {
    box-shadow: 0 0 34px rgba(0, 229, 255, 0.65) !important;
    transform: translateY(-1px);
}
.company-text {
    color: rgba(150, 200, 230, 0.35) !important;
}
</style>
'''

# ============ 粒子动画 ============
ANIM_SCRIPT = '''
<script id="ly-net-anim">
(function () {
    if (window.__lyNetAnimLoaded) return;
    window.__lyNetAnimLoaded = true;
    var app = function () {
        var page = document.querySelector('.login-page');
        if (!page) { setTimeout(app, 300); return; }
        var canvas = document.createElement('canvas');
        canvas.className = 'ly-net-canvas';
        page.appendChild(canvas);
        var ctx = canvas.getContext('2d');
        var W, H;
        function resize() {
            W = canvas.width = page.clientWidth;
            H = canvas.height = page.clientHeight;
        }
        resize();
        window.addEventListener('resize', resize);
        var nodes = [];
        var N = 60;
        for (var i = 0; i < N; i++) {
            nodes.push({
                x: Math.random() * W,
                y: Math.random() * H,
                vx: (Math.random() - 0.5) * 0.4,
                vy: (Math.random() - 0.5) * 0.4,
                r: Math.random() * 1.8 + 1
            });
        }
        var pkts = [];
        for (var i = 0; i < 12; i++) {
            pkts.push({
                x: Math.random() * W,
                y: Math.random() * H,
                vx: (Math.random() - 0.5) * 1.6,
                vy: (Math.random() - 0.5) * 1.6,
                life: Math.random() * 200
            });
        }
        var linkDist = 130;
        function draw() {
            ctx.clearRect(0, 0, W, H);
            ctx.lineWidth = 1;
            for (var i = 0; i < N; i++) {
                for (var j = i + 1; j < N; j++) {
                    var dx = nodes[i].x - nodes[j].x;
                    var dy = nodes[i].y - nodes[j].y;
                    var d = Math.sqrt(dx * dx + dy * dy);
                    if (d < linkDist) {
                        var a = (1 - d / linkDist) * 0.35;
                        ctx.strokeStyle = 'rgba(0, 229, 255, ' + a + ')';
                        ctx.beginPath();
                        ctx.moveTo(nodes[i].x, nodes[i].y);
                        ctx.lineTo(nodes[j].x, nodes[j].y);
                        ctx.stroke();
                    }
                }
            }
            for (var i = 0; i < N; i++) {
                var n = nodes[i];
                n.x += n.vx; n.y += n.vy;
                if (n.x < 0 || n.x > W) n.vx *= -1;
                if (n.y < 0 || n.y > H) n.vy *= -1;
                ctx.beginPath();
                ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0, 229, 255, 0.55)';
                ctx.fill();
            }
            for (var i = 0; i < pkts.length; i++) {
                var p = pkts[i];
                p.x += p.vx; p.y += p.vy; p.life++;
                if (p.life > 300 || p.x < 0 || p.x > W || p.y < 0 || p.y > H) {
                    p.x = Math.random() * W; p.y = Math.random() * H;
                    p.vx = (Math.random() - 0.5) * 1.6;
                    p.vy = (Math.random() - 0.5) * 1.6;
                    p.life = 0;
                }
                var grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, 6);
                grad.addColorStop(0, 'rgba(125, 249, 255, 0.95)');
                grad.addColorStop(1, 'rgba(0, 229, 255, 0)');
                ctx.beginPath();
                ctx.arc(p.x, p.y, 6, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();
            }
            requestAnimationFrame(draw);
        }
        draw();
    };
    if (document.readyState === 'complete') app();
    else window.addEventListener('load', function () { setTimeout(app, 200); });
})();
</script>
'''

# ============ 改名脚本（繁体 天網） ============
BRAND_SCRIPT = '''
<script id="ly-brand-rename">
(function () {
    if (window.__lyBrandRename) return;
    window.__lyBrandRename = true;
    function replaceText(node) {
        if (node.nodeType === 3) {
            var t = node.nodeValue;
            if (t.indexOf('流影') !== -1) {
                node.nodeValue = t.split('流影').join('天網');
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
        if (document.title.indexOf('流影') !== -1) {
            document.title = document.title.split('流影').join('天網');
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

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# SFTP 上传 favicon.svg
sftp = client.open_sftp()
sftp.put(r'd:\QorderProject\SOC\favicon.svg', '/Server/www/ui/favicon.svg')
sftp.close()
print("favicon.svg 已上传")

cmds = [
    ("重建 index.html + 注入 v2 全套", f"""
cd /Server/www/ui
echo "=== 1. 备份当前版本 ==="
cp index.html index.html.v2_bak
echo "已备份 index.html.v2_bak"
echo ""
echo "=== 2. 从干净基底重建 + 注入 ==="
python3 - <<'PYEOF'
import shutil
shutil.copy('/Server/www/ui/index.html.bak', '/Server/www/ui/index.html')
src = open('/Server/www/ui/index.html').read()
style = {STYLE_V2!r}
anim = {ANIM_SCRIPT!r}
brand = {BRAND_SCRIPT!r}
# 替换 favicon 为 SVG
src = src.replace('<link rel="icon" href="./favicon.ico"/>', '<link rel="icon" type="image/svg+xml" href="./favicon.svg"/>')
# 注入 style 到 head
src = src.replace('</head>', style + '</head>')
# 注入脚本到 body 末尾
src = src.replace('</body>', anim + brand + '</body>')
open('/Server/www/ui/index.html', 'w').write(src)
print('重建完成，大小:', len(src))
PYEOF
echo ""
echo "=== 3. 验证 ==="
echo -n "style v2: "; grep -c "ly-tech-v2" index.html
echo -n "anim: "; grep -c "ly-net-anim" index.html
echo -n "brand: "; grep -c "ly-brand-rename" index.html
echo -n "favicon svg: "; grep -c "favicon.svg" index.html
echo -n "4行隐藏: "; grep -c "login-left-center" index.html
echo -n "天網: "; grep -c "天網" index.html
echo ""
echo "=== 4. 页面响应 + JS 引用 ==="
curl -s -o /dev/null -w "/ui/: %{{http_code}}\\n" "http://127.0.0.1/ui/" --max-time 15
curl -s "http://127.0.0.1/ui/" --max-time 15 2>&1 | grep -o "static/js/[a-z0-9.]*\\.js" | head -5
echo ""
echo "=== 5. favicon 可访问 ==="
curl -s -o /dev/null -w "favicon.svg: %{{http_code}}\\n" "http://127.0.0.1/ui/favicon.svg" --max-time 15
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