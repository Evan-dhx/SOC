import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 科技网络安全风格登录页样式
STYLE = """
<style id="ly-tech-login-style">
/* ========== 科技网络安全风登录界面 ========== */
.login-page {
    background: #030a18 !important;
    position: relative;
    overflow: hidden;
}
/* 网格背景 */
.login-page::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        linear-gradient(rgba(0, 229, 255, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 229, 255, 0.05) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 1;
}
/* 顶部扫描光带 */
.login-page::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.8), transparent);
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
/* 粒子动画层 */
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
.login-left-logo {
    color: #7df9ff !important;
    text-shadow: 0 0 8px rgba(0, 229, 255, 0.9), 0 0 20px rgba(0, 229, 255, 0.5) !important;
    letter-spacing: 3px !important;
    font-size: 1.6rem !important;
}
.login-left-logo-tip div {
    color: rgba(125, 249, 255, 0.75) !important;
}
.login-left-center-item {
    position: relative;
    padding-left: 22px;
}
.login-left-center-item::before {
    content: '';
    position: absolute;
    left: 0;
    top: 6px;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #00e5ff;
    box-shadow: 0 0 10px #00e5ff, 0 0 20px #00e5ff;
    animation: ly-pulse 1.8s ease-in-out infinite;
}
.login-left-center-item::after {
    content: '';
    position: absolute;
    left: 1px;
    top: 12px;
    bottom: -30px;
    width: 1px;
    background: linear-gradient(to bottom, rgba(0, 229, 255, 0.5), transparent);
}
.login-left-center-item .item-title {
    color: #e8f6ff !important;
    text-shadow: 0 0 12px rgba(0, 229, 255, 0.4) !important;
}
.login-left-center-item .item-text {
    color: rgba(200, 230, 255, 0.65) !important;
}
@keyframes ly-pulse {
    0%, 100% { box-shadow: 0 0 6px #00e5ff, 0 0 12px #00e5ff; }
    50% { box-shadow: 0 0 14px #00e5ff, 0 0 30px #00e5ff; }
}
/* 右侧登录卡片区 */
.login_right {
    background: transparent !important;
    z-index: 3;
}
.login-form {
    background: rgba(8, 25, 50, 0.72);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 229, 255, 0.28);
    border-radius: 16px;
    padding: 48px 40px 30px;
    box-shadow:
        0 0 40px rgba(0, 229, 255, 0.10),
        inset 0 0 30px rgba(0, 229, 255, 0.04);
    width: 55%;
    max-width: 420px;
}
.login-title {
    margin-bottom: 28px;
}
.login-title-logo :first-child {
    color: #7df9ff !important;
    font-size: 2rem !important;
    letter-spacing: 10px !important;
    text-shadow: 0 0 10px rgba(0, 229, 255, 0.9), 0 0 30px rgba(0, 229, 255, 0.4) !important;
}
.login-title-logo :last-child {
    color: rgba(125, 249, 255, 0.6) !important;
    letter-spacing: 3px !important;
}
/* 版本徽标 */
.version-text {
    background: transparent !important;
    border: 1px solid rgba(0, 229, 255, 0.5);
    color: #7df9ff !important;
    border-radius: 12px !important;
    box-shadow: 0 0 8px rgba(0, 229, 255, 0.3);
}
/* 表单标签 */
.login-form .ant-form-item-label > label {
    color: rgba(200, 230, 255, 0.75) !important;
    letter-spacing: 1px;
}
/* 输入框 */
.login-form .ant-input-affix-wrapper,
.login-form .ant-input {
    background: rgba(3, 15, 32, 0.85) !important;
    border: 1px solid rgba(0, 229, 255, 0.25) !important;
    color: #d8f4ff !important;
    border-radius: 8px !important;
    transition: all 0.3s;
}
.login-form .ant-input-affix-wrapper:hover,
.login-form .ant-input:hover,
.login-form .ant-input-affix-wrapper:focus-within {
    border-color: #00e5ff !important;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.25) !important;
    background: rgba(3, 20, 42, 0.95) !important;
}
.login-form .ant-input::placeholder {
    color: rgba(140, 190, 220, 0.5) !important;
}
.login-form .anticon {
    color: rgba(0, 229, 255, 0.7) !important;
}
/* 登录按钮 */
.login-form-button {
    background: linear-gradient(90deg, #0072ff, #00e5ff) !important;
    border: none !important;
    height: 44px !important;
    font-size: 16px !important;
    letter-spacing: 4px !important;
    border-radius: 10px !important;
    box-shadow: 0 0 18px rgba(0, 229, 255, 0.35) !important;
    transition: all 0.3s !important;
}
.login-form-button:hover {
    box-shadow: 0 0 30px rgba(0, 229, 255, 0.6) !important;
    transform: translateY(-1px);
}
.company-text {
    color: rgba(140, 190, 220, 0.4) !important;
}
</style>
"""

# 网络拓扑粒子动画脚本
SCRIPT = """
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
        // 节点（模拟网络拓扑）
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
        // 移动数据包（网络安全数据流）
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
            // 连线
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
            // 节点
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
            // 数据包（小光点带尾迹）
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
"""

import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ===== 上方为样式/脚本常量 =====

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("注入科技风样式与动画", f"""
cd /Server/www/ui
echo "=== 1. 备份当前 index.html ==="
cp index.html index.html.tech_bak
echo "已备份为 index.html.tech_bak"
echo ""
echo "=== 2. 注入 style + script ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
if 'ly-tech-login-style' in src:
    print("已存在注入，跳过")
else:
    style = {STYLE!r}
    script = {SCRIPT!r}
    src = src.replace('</head>', style + '</head>')
    src = src.replace('</body>', script + '</body>')
    open('/Server/www/ui/index.html', 'w').write(src)
    print("注入完成")
PYEOF
echo ""
echo "=== 3. 验证注入 ==="
grep -c "ly-tech-login-style\|ly-net-anim" /Server/www/ui/index.html
echo ""
echo "=== 4. 页面响应 + JS 引用完整性 ==="
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