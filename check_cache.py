import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check index.html references
    ("check index.html", r"""
grep 'main\.' /Server/www/ui/index.html
echo "---"
grep '2\.' /Server/www/ui/index.html
"""),

    # Check if old chunk files still exist
    ("check old files", r"""
ls /Server/www/ui/static/js/main.*.chunk.js 2>/dev/null
echo "---"
ls /Server/www/ui/static/js/2.*.chunk.js 2>/dev/null
"""),

    # Check if the new JS has the fix
    ("verify fix in build", r"""
grep -c 'Array.isArray' /Server/www/ui/static/js/main.ff156c89.chunk.js
echo "---"
# Also check the 2.* chunk
grep -c 'Array.isArray' /Server/www/ui/static/js/2.*.chunk.js 2>/dev/null
"""),

    # Check HTTP cache headers
    ("check cache headers", r"""
curl -sI http://localhost/ui/static/js/main.ff156c89.chunk.js 2>&1 | grep -i 'cache\|etag\|last-modified'
echo "---"
curl -sI http://localhost/ui/ 2>&1 | grep -i 'cache\|etag\|last-modified'
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
