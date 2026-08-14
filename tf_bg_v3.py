import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

GLOW_RULE = '''
/* ========== 背景光晕增强 ========== */
.login-page {
    background:
        radial-gradient(ellipse 55% 45% at 18% 12%, rgba(0, 114, 255, 0.30), transparent 62%),
        radial-gradient(ellipse 45% 35% at 82% 88%, rgba(0, 229, 255, 0.18), transparent 60%),
        radial-gradient(ellipse 35% 30% at 68% 18%, rgba(90, 70, 255, 0.16), transparent 60%),
        radial-gradient(ellipse at 15% 0%, #14294a 0%, #0b1220 55%, #070d19 100%) !important;
}
'''

ANIM_V2 = '''<script id="ly-net-anim">
(function () {
    if (window.__lyNetAnimLoaded) return;
    window.__lyNetAnimLoaded = true;
    var app = function () {
        var page = document.querySelector('[class*="login-page"]');
        if (!page) { setTimeout(app, 300); return; }
        var canvas = document.createElement('canvas');
        canvas.className = 'ly-net-canvas';
        page.appendChild(canvas);
        var ctx = canvas.getContext('2d');
        var W, H, DPR = window.devicePixelRatio || 1;
        var w = page.clientWidth, h = page.clientHeight;
        function resize() {
            w = page.clientWidth; h = page.clientHeight;
            W = canvas.width = w * DPR; H = canvas.height = h * DPR;
            canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
            ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
        }
        resize();
        window.addEventListener('resize', resize);
        // 网络节点
        var N = 90, nodes = [];
        for (var i = 0; i < N; i++) {
            nodes.push({
                x: Math.random() * w, y: Math.random() * h,
                vx: (Math.random() - 0.5) * 0.4, vy: (Math.random() - 0.5) * 0.4,
                r: Math.random() * 1.6 + 1
            });
        }
        // 中心枢纽
        var hub = { x: w * 0.22, y: h * 0.35, r: 26 };
        // 数据包（带尾迹）
        var pkts = [];
        for (var i = 0; i < 16; i++) {
            pkts.push({
                x: Math.random() * w, y: Math.random() * h,
                vx: (Math.random() - 0.5) * 2.2, vy: (Math.random() - 0.5) * 2.2,
                life: Math.random() * 200, hist: []
            });
        }
        // 二进制雨
        var cols = Math.floor(w / 26), rains = [];
        for (var i = 0; i < cols; i++) {
            rains.push({ x: i * 26 + Math.random() * 26, y: Math.random() * h, sp: Math.random() * 1.1 + 0.35, len: Math.random() * 10 + 5 });
        }
        var linkDist = 150;
        function draw() {
            ctx.clearRect(0, 0, w, h);
            // 节点连线
            ctx.lineWidth = 1;
            for (var i = 0; i < N; i++) {
                for (var j = i + 1; j < N; j++) {
                    var dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y, d = Math.sqrt(dx * dx + dy * dy);
                    if (d < linkDist) {
                        ctx.strokeStyle = 'rgba(0, 229, 255, ' + ((1 - d / linkDist) * 0.3).toFixed(3) + ')';
                        ctx.beginPath(); ctx.moveTo(nodes[i].x, nodes[i].y); ctx.lineTo(nodes[j].x, nodes[j].y); ctx.stroke();
                    }
                }
            }
            // 枢纽连线
            for (var i = 0; i < N; i++) {
                var dx = nodes[i].x - hub.x, dy = nodes[i].y - hub.y, d = Math.sqrt(dx * dx + dy * dy);
                if (d < 260 && d > 40) {
                    ctx.strokeStyle = 'rgba(0, 229, 255, ' + ((1 - d / 260) * 0.22).toFixed(3) + ')';
                    ctx.beginPath(); ctx.moveTo(nodes[i].x, nodes[i].y); ctx.lineTo(hub.x, hub.y); ctx.stroke();
                }
            }
            // 节点
            for (var i = 0; i < N; i++) {
                var n = nodes[i];
                n.x += n.vx; n.y += n.vy;
                if (n.x < 0 || n.x > w) n.vx *= -1;
                if (n.y < 0 || n.y > h) n.vy *= -1;
                ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0, 229, 255, 0.5)'; ctx.fill();
            }
            // 中心枢纽：呼吸外圈
            var t = Date.now() / 1000;
            for (var k = 1; k <= 3; k++) {
                var rr = hub.r + k * 10 + Math.sin(t * 1.5 + k) * 3;
                ctx.beginPath(); ctx.arc(hub.x, hub.y, rr, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(0, 229, 255, ' + (0.35 - 0.09 * k).toFixed(2) + ')';
                ctx.stroke();
            }
            ctx.beginPath(); ctx.arc(hub.x, hub.y, hub.r, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(0, 229, 255, 0.12)'; ctx.fill();
            ctx.beginPath(); ctx.arc(hub.x, hub.y, 4, 0, Math.PI * 2);
            ctx.fillStyle = '#7df9ff'; ctx.fill();
            // 数据包尾迹
            for (var i = 0; i < pkts.length; i++) {
                var p = pkts[i];
                p.hist.push({ x: p.x, y: p.y });
                if (p.hist.length > 8) p.hist.shift();
                p.x += p.vx; p.y += p.vy; p.life++;
                if (p.life > 260 || p.x < 0 || p.x > w || p.y < 0 || p.y > h) {
                    p.x = Math.random() * w; p.y = Math.random() * h;
                    p.vx = (Math.random() - 0.5) * 2.2; p.vy = (Math.random() - 0.5) * 2.2;
                    p.life = 0; p.hist = [];
                }
                ctx.lineWidth = 1;
                for (var jj = 0; jj < p.hist.length - 1; jj++) {
                    ctx.beginPath(); ctx.moveTo(p.hist[jj].x, p.hist[jj].y); ctx.lineTo(p.hist[jj + 1].x, p.hist[jj + 1].y);
                    ctx.strokeStyle = 'rgba(125, 249, 255, ' + (jj / p.hist.length * 0.4).toFixed(3) + ')';
                    ctx.stroke();
                }
                var g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, 6);
                g.addColorStop(0, 'rgba(125, 249, 255, 0.95)');
                g.addColorStop(1, 'rgba(0, 229, 255, 0)');
                ctx.beginPath(); ctx.arc(p.x, p.y, 6, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
            }
            // 二进制雨（低透明度矩阵风）
            ctx.font = '12px monospace';
            for (var i = 0; i < rains.length; i++) {
                var r = rains[i];
                r.y += r.sp;
                if (r.y - h > r.len * 18) r.y = -r.len * 18;
                for (var jj = 0; jj < r.len; jj++) {
                    var yy = r.y - jj * 18;
                    if (yy < 0 || yy > h) continue;
                    ctx.fillStyle = 'rgba(0, 229, 255, ' + (0.12 * (1 - jj / r.len)).toFixed(3) + ')';
                    ctx.fillText(Math.random() > 0.5 ? '1' : '0', r.x, yy);
                }
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

cmds = [
    ("背景增强 + 动画升级", f"""
cd /Server/www/ui
echo "=== 1. 备份 ==="
cp index.html index.html.bg_v3_bak
echo "已备份 index.html.bg_v3_bak"
echo ""
echo "=== 2. 追加光晕样式 + 替换动画脚本 ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
glow = {GLOW_RULE!r}
anim = {ANIM_V2!r}
changed = []
# 光晕样式（在 style 块末尾追加）
if '背景光晕增强' in src:
    print('光晕样式已存在')
else:
    pos = src.find('</style>')
    if pos < 0:
        print('未找到 style 结束标记')
    else:
        src = src[:pos] + glow + src[pos:]
        changed.append('glow')
# 替换动画脚本（按 id 整块替换）
start = src.find('<script id="ly-net-anim">')
if start < 0:
    print('未找到动画脚本')
else:
    end = src.find('</script>', start) + len('</script>')
    src = src[:start] + anim + src[end:]
    changed.append('anim')
if changed:
    open('/Server/www/ui/index.html', 'w').write(src)
    print('已完成:', changed)
PYEOF
echo ""
echo "=== 3. 验证 ==="
echo -n "光晕: "; grep -c "背景光晕增强" index.html
echo -n "中心枢纽: "; grep -c "中心枢纽" index.html
echo -n "二进制雨: "; grep -c "二进制雨" index.html
echo -n "动画脚本数: "; grep -c "ly-net-anim" index.html
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