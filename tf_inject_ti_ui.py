import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

UI_SCRIPT = '''<script id="ly-threat-conf">
(function () {
    if (window.__lyThreatConf) return;
    window.__lyThreatConf = true;

    var css = '' +
        '.ly-ti-btn{' +
        'display:inline-block;margin-right:14px;padding:2px 12px;border:1px solid rgba(0,229,255,.45);' +
        'border-radius:12px;color:#7df9ff;font-size:12px;line-height:20px;cursor:pointer;' +
        'letter-spacing:2px;background:rgba(0,229,255,.08);transition:all .3s;' +
        'box-shadow:0 0 8px rgba(0,229,255,.2);' +
        '}' +
        '.ly-ti-btn:hover{background:rgba(0,229,255,.2);box-shadow:0 0 14px rgba(0,229,255,.4);}' +
        '.ly-ti-mask{position:fixed;inset:0;background:rgba(3,10,22,.68);backdrop-filter:blur(6px);' +
        '-webkit-backdrop-filter:blur(6px);z-index:9999;display:flex;align-items:center;justify-content:center;}' +
        '.ly-ti-panel{width:520px;max-width:92vw;background:linear-gradient(160deg,rgba(10,26,52,.96),rgba(4,14,30,.97));' +
        'border:1px solid rgba(0,229,255,.25);border-radius:14px;padding:26px 30px;' +
        'box-shadow:0 24px 60px rgba(0,0,0,.6),0 0 34px rgba(0,229,255,.1);color:#d8f4ff;position:relative;}' +
        '.ly-ti-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;' +
        'padding-bottom:12px;border-bottom:1px solid rgba(0,229,255,.2);}' +
        '.ly-ti-title{font-size:16px;letter-spacing:3px;color:#7df9ff;text-shadow:0 0 10px rgba(0,229,255,.5);}' +
        '.ly-ti-close{cursor:pointer;color:rgba(200,230,255,.7);font-size:18px;padding:0 4px;}' +
        '.ly-ti-close:hover{color:#7df9ff;}' +
        '.ly-ti-group{margin-bottom:14px;}' +
        '.ly-ti-group-title{font-size:12px;color:rgba(0,229,255,.75);letter-spacing:2px;margin-bottom:10px;' +
        'border-left:3px solid rgba(0,229,255,.7);padding-left:8px;}' +
        '.ly-ti-row{display:flex;align-items:center;margin-bottom:10px;}' +
        '.ly-ti-row label{width:90px;color:rgba(210,235,255,.8);font-size:13px;flex-shrink:0;}' +
        '.ly-ti-row input{flex:1;background:rgba(3,14,30,.9);border:1px solid rgba(0,229,255,.28);' +
        'border-radius:6px;color:#e0f7ff;padding:7px 10px;font-size:13px;outline:none;transition:all .3s;}' +
        '.ly-ti-row input:focus{border-color:#00e5ff;box-shadow:0 0 12px rgba(0,229,255,.3);}' +
        '.ly-ti-tip{font-size:12px;color:rgba(150,200,230,.5);margin:-4px 0 12px 90px;}' +
        '.ly-ti-actions{display:flex;gap:12px;margin-top:20px;}' +
        '.ly-ti-save{flex:1;background:linear-gradient(90deg,#0072ff,#00e5ff);border:none;border-radius:8px;' +
        'color:#fff;font-size:14px;letter-spacing:4px;padding:10px 0;cursor:pointer;' +
        'box-shadow:0 0 16px rgba(0,229,255,.35);transition:all .3s;}' +
        '.ly-ti-save:hover{box-shadow:0 0 26px rgba(0,229,255,.6);}' +
        '.ly-ti-test{flex:1;background:transparent;border:1px solid rgba(0,229,255,.45);border-radius:8px;' +
        'color:#7df9ff;font-size:14px;letter-spacing:4px;padding:10px 0;cursor:pointer;transition:all .3s;}' +
        '.ly-ti-test:hover{background:rgba(0,229,255,.12);}' +
        '.ly-ti-cancel{flex:1;background:transparent;border:1px solid rgba(150,200,230,.3);border-radius:8px;' +
        'color:rgba(200,230,255,.7);font-size:14px;letter-spacing:4px;padding:10px 0;cursor:pointer;}' +
        '.ly-ti-msg{margin-top:12px;font-size:12px;min-height:18px;color:#7df9ff;text-align:center;' +
        'letter-spacing:1px;}' +
        '';
    var s = document.createElement('style');
    s.textContent = css;
    document.head.appendChild(s);

    function buildUI() {
        var tools = document.querySelector('.nav-tools');
        if (!tools) { setTimeout(buildUI, 500); return; }
        if (document.querySelector('.ly-ti-btn')) return;
        var btn = document.createElement('span');
        btn.className = 'ly-ti-btn';
        btn.title = '威胁情报服务配置';
        btn.textContent = '情报';
        tools.insertBefore(btn, tools.firstChild);
        btn.addEventListener('click', openModal);
    }

    function openModal() {
        if (document.querySelector('.ly-ti-mask')) return;
        var mask = document.createElement('div');
        mask.className = 'ly-ti-mask';
        mask.innerHTML =
            '<div class="ly-ti-panel">' +
            '<div class="ly-ti-head"><span class="ly-ti-title">威胁情报服务配置</span>' +
            '<span class="ly-ti-close">&#10005;</span></div>' +
            '<div class="ly-ti-group"><div class="ly-ti-group-title">威胁情报查询（threatinfo）</div>' +
            '<div class="ly-ti-row"><label>API Key</label><input id="ly-ti-key" type="password" placeholder="威胁情报服务 KEY"></div>' +
            '<div class="ly-ti-row"><label>服务地址</label><input id="ly-ti-host" placeholder="HOST，如 10.0.0.1"></div>' +
            '<div class="ly-ti-row"><label>服务端口</label><input id="ly-ti-port" placeholder="PORT，如 8080"></div>' +
            '</div>' +
            '<div class="ly-ti-group"><div class="ly-ti-group-title">高级情报服务（threatinfopro）</div>' +
            '<div class="ly-ti-row"><label>API Key</label><input id="ly-ti-apikey" type="password" placeholder="高级服务 API_KEY"></div>' +
            '<div class="ly-ti-row"><label>服务地址</label><input id="ly-ti-tic-host" placeholder="HOST"></div>' +
            '<div class="ly-ti-row"><label>服务端口</label><input id="ly-ti-tic-port" placeholder="PORT"></div>' +
            '<div class="ly-ti-tip">保存后立即生效，无需重启服务；测试按钮验证服务连通性</div>' +
            '</div>' +
            '<div class="ly-ti-actions">' +
            '<button class="ly-ti-save" id="ly-ti-save">保存</button>' +
            '<button class="ly-ti-test" id="ly-ti-test">测试</button>' +
            '<button class="ly-ti-cancel" id="ly-ti-cancel">关闭</button>' +
            '</div>' +
            '<div class="ly-ti-msg" id="ly-ti-msg"></div>' +
            '</div>';
        document.body.appendChild(mask);

        mask.querySelector('.ly-ti-close').addEventListener('click', closeModal);
        mask.querySelector('#ly-ti-cancel').addEventListener('click', closeModal);
        mask.addEventListener('click', function (e) { if (e.target === mask) closeModal(); });
        mask.querySelector('#ly-ti-save').addEventListener('click', doSave);
        mask.querySelector('#ly-ti-test').addEventListener('click', doTest);

        var msg = mask.querySelector('#ly-ti-msg');
        msg.textContent = '读取当前配置…';
        fetch('/d/threatconf?op=get', { credentials: 'same-origin' })
            .then(function (r) { return r.json(); })
            .then(function (d) {
                var v = d[0] || {};
                mask.querySelector('#ly-ti-key').value = v.key || '';
                mask.querySelector('#ly-ti-host').value = v.tisrs_host || '';
                mask.querySelector('#ly-ti-port').value = v.tisrs_port || '';
                mask.querySelector('#ly-ti-apikey').value = v.api_key || '';
                mask.querySelector('#ly-ti-tic-host').value = v.tic_host || '';
                mask.querySelector('#ly-ti-tic-port').value = v.tic_port || '';
                msg.textContent = v.key ? '已加载当前配置' : '当前未配置（可填写后保存）';
            })
            .catch(function () { msg.textContent = '读取配置失败'; });
    }

    function closeModal() {
        var m = document.querySelector('.ly-ti-mask');
        if (m) m.parentNode.removeChild(m);
    }

    function doSave() {
        var mask = document.querySelector('.ly-ti-mask');
        var msg = mask.querySelector('#ly-ti-msg');
        var data = {
            op: 'save',
            key: mask.querySelector('#ly-ti-key').value,
            tisrs_host: mask.querySelector('#ly-ti-host').value,
            tisrs_port: mask.querySelector('#ly-ti-port').value,
            api_key: mask.querySelector('#ly-ti-apikey').value,
            tic_host: mask.querySelector('#ly-ti-tic-host').value,
            tic_port: mask.querySelector('#ly-ti-tic-port').value
        };
        msg.textContent = '保存中…';
        var body = Object.keys(data).map(function (k) {
            return encodeURIComponent(k) + '=' + encodeURIComponent(data[k]);
        }).join('&');
        fetch('/d/threatconf', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: body
        }).then(function (r) { return r.json(); })
            .then(function (d) {
                msg.textContent = (d[0] && d[0].msg) ? d[0].msg : '保存完成';
            })
            .catch(function () { msg.textContent = '保存失败'; });
    }

    function doTest() {
        var mask = document.querySelector('.ly-ti-mask');
        var msg = mask.querySelector('#ly-ti-msg');
        msg.textContent = '测试中…';
        fetch('/d/threatconf', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'op=test'
        }).then(function (r) { return r.json(); })
            .then(function (d) {
                var v = d[0] || {};
                msg.textContent = v.msg || '测试完成';
                msg.style.color = v.code === 200 ? '#7df9ff' : '#ffa63f';
            })
            .catch(function () { msg.textContent = '测试失败'; });
    }

    buildUI();
})();
</script>
'''

cmds = [
    ("注入威胁情报配置 UI", f"""
cd /Server/www/ui
echo "=== 1. 备份 ==="
cp index.html index.html.ti_ui_bak
echo "已备份 index.html.ti_ui_bak"
echo ""
echo "=== 2. 注入 UI 脚本 ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
ui = {UI_SCRIPT!r}
if 'ly-threat-conf' in src:
    print('UI 脚本已存在，跳过')
else:
    pos = src.find('</body>')
    if pos < 0:
        print('未找到 body 结束标记')
    else:
        src = src[:pos] + ui + src[pos:]
        open('/Server/www/ui/index.html', 'w').write(src)
        print('已注入')
PYEOF
echo ""
echo "=== 3. 验证 ==="
grep -c "ly-threat-conf\|ly-ti-btn" index.html
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