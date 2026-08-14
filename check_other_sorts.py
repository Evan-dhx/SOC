import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check if new build was deployed
    ("check build", r"""
echo "=== Check deployed JS ==="
grep -c 'Array.isArray' /Server/www/ui/static/js/main.*.chunk.js 2>/dev/null
echo "---"
ls -la /Server/www/ui/static/js/main.*.chunk.js 2>/dev/null
echo "---"
# Check build time
stat /Server/www/ui/static/js/main.*.chunk.js 2>/dev/null | grep Modify
"""),

    # Check for other .slice().sort() patterns in overview store
    ("check overview store", r"""
echo "=== overview-om/store.js sort calls ==="
grep -n '\.sort\|\.slice' /root/SOC/ly_vis/packages/std/src/page/overview/page-child/overview-om/store.js | head -20
echo "---"
echo "=== overview-ma/store.js sort calls ==="
grep -n '\.sort\|\.slice' /root/SOC/ly_vis/packages/std/src/page/overview/page-child/overview-ma/store.js | head -10
"""),

    # Check the specific lines that could cause the error
    ("check specific lines", r"""
echo "=== overview-om/store.js lines 140-155 ==="
sed -n '140,155p' /root/SOC/ly_vis/packages/std/src/page/overview/page-child/overview-om/store.js
echo "---"
echo "=== overview-om/store.js lines 250-265 ==="
sed -n '250,265p' /root/SOC/ly_vis/packages/std/src/page/overview/page-child/overview-om/store.js
echo "---"
echo "=== overview-om/store.js lines 375-390 ==="
sed -n '375,390p' /root/SOC/ly_vis/packages/std/src/page/overview/page-child/overview-om/store.js
"""),

    # Check tree-matrix component
    ("check tree-matrix", r"""
echo "=== tree-matrix line 63 ==="
sed -n '58,70p' /root/SOC/ly_vis/packages/std/src/components/tree-matrix/index.jsx
"""),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
