import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

V3_RULE = '''
/* ========== 登录卡片 v3 重设计 ========== */
.login-form {
    position: relative;
    background: linear-gradient(160deg, rgba(10, 26, 52, 0.88), rgba(4, 14, 30, 0.92)) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(0, 229, 255, 0.22) !important;
    border-radius: 14px !important;
    padding: 54px 44px 36px !important;
    box-shadow:
        0 24px 60px rgba(0, 0, 0, 0.55),
        0 0 34px rgba(0, 229, 255, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
}
/* 顶部高光线 */
.login-form::before {
    content: '';
    position: absolute;
    top: -1px;
    left: 10%;
    right: 10%;
    height: 2px;
    border-radius: 2px;
    background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.85), transparent);
    pointer-events: none;
}
/* 四角科技角标 */
.login-form::after {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: 14px;
    background:
        linear-gradient(#00e5ff, #00e5ff) top left / 20px 2px,
        linear-gradient(#00e5ff, #00e5ff) top left / 2px 20px,
        linear-gradient(#00e5ff, #00e5ff) top right / 20px 2px,
        linear-gradient(#00e5ff, #00e5ff) top right / 2px 20px,
        linear-gradient(#00e5ff, #00e5ff) bottom left / 20px 2px,
        linear-gradient(#00e5ff, #00e5ff) bottom left / 2px 20px,
        linear-gradient(#00e5ff, #00e5ff) bottom right / 20px 2px,
        linear-gradient(#00e5ff, #00e5ff) bottom right / 2px 20px;
    background-repeat: no-repeat;
    opacity: 0.55;
    pointer-events: none;
}
/* 标题区：加底部装饰分隔线 */
.login-title {
    position: relative;
    margin-bottom: 34px !important;
    padding-bottom: 20px;
}
.login-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 56px;
    height: 2px;
    border-radius: 2px;
    background: linear-gradient(90deg, transparent, #00e5ff, transparent);
    box-shadow: 0 0 8px rgba(0, 229, 255, 0.6);
}
.login-title-logo :first-child {
    font-size: 2.2rem !important;
    letter-spacing: 14px !important;
    text-indent: 7px;
}
/* 输入框：更舒适的内边距与聚焦光晕 */
.login-form .ant-input-affix-wrapper {
    padding: 9px 12px !important;
    border-radius: 8px !important;
}
.login-form .ant-input {
    padding: 4px 2px !important;
}
.login-form .ant-input-affix-wrapper:focus-within {
    border-color: #00e5ff !important;
    box-shadow:
        0 0 0 1px rgba(0, 229, 255, 0.35),
        0 0 18px rgba(0, 229, 255, 0.25) !important;
}
/* 表单项间距 */
.login-form .ant-form-item {
    margin-bottom: 26px !important;
}
/* 按钮：流光扫过特效 */
.login-form-button {
    position: relative;
    overflow: hidden;
    letter-spacing: 8px !important;
    border-radius: 10px !important;
    background: linear-gradient(90deg, #0072ff, #00c6e8, #0072ff) !important;
    background-size: 200% 100% !important;
    animation: ly-btn-flow 4s linear infinite !important;
}
@keyframes ly-btn-flow {
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}
.login-form-button::after {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    width: 36%;
    left: -45%;
    background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.35), transparent);
    animation: ly-btn-shine 2.6s ease-in-out infinite;
    pointer-events: none;
}
@keyframes ly-btn-shine {
    0% { left: -45%; }
    55%, 100% { left: 120%; }
}
/* 版本标签：胶囊徽标 */
.version-text {
    background: rgba(0, 229, 255, 0.1) !important;
    border: 1px solid rgba(0, 229, 255, 0.5) !important;
    color: #7df9ff !important;
    border-radius: 12px !important;
    padding: 0 12px !important;
    line-height: 20px !important;
    letter-spacing: 1px;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.25);
    transform: scale(0.9) !important;
}
'''

cmds = [
    ("追加登录卡片 v3 样式", f"""
cd /Server/www/ui
echo "=== 1. 备份 ==="
cp index.html index.html.card_v3_bak
echo "已备份 index.html.card_v3_bak"
echo ""
echo "=== 2. 追加 v3 卡片样式 ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
v3 = {V3_RULE!r}
marker = 'ly-btn-flow'
if marker in src:
    print('v3 样式已存在，跳过')
else:
    pos = src.find('</style>')
    if pos < 0:
        print('未找到 style 结束标记')
    else:
        src = src[:pos] + v3 + src[pos:]
        open('/Server/www/ui/index.html', 'w').write(src)
        print('v3 卡片样式已追加')
PYEOF
echo ""
echo "=== 3. 验证 ==="
grep -c "ly-btn-flow\|ly-btn-shine" /Server/www/ui/index.html
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