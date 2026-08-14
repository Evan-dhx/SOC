import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== 1. 检查关键二进制文件时间 ===')
for cmd in [
    'ls -la /Agent/bin/actl 2>/dev/null',
    'ls -la /Agent/cmd/actl 2>/dev/null',
    'ls -la /Agent/bin/config_updater 2>/dev/null',
    'ls -la /Server/bin/config_pusher 2>/dev/null',
    'ls -la /Agent/lib/libcommon.so 2>/dev/null',
    'ls -la /Server/lib/libcommon.so 2>/dev/null',
    'ls -la /usr/local/lib/libcommon.so 2>/dev/null',
]:
    i, o, e = c.exec_command(cmd, timeout=10)
    out = o.read().decode().strip()
    print(f'  {out}')

print()
print('=== 2. 检查 Apache /actl 映射 ===')
i, o, e = c.exec_command("grep -n ScriptAlias /etc/httpd/conf.d/*.conf 2>/dev/null", timeout=10)
out = o.read().decode()
print(out[:2000] if out.strip() else '  (no ScriptAlias found)')

print()
print('=== 3. 检查 config.dev ===')
i, o, e = c.exec_command('ls -la /Agent/data/config* 2>/dev/null', timeout=10)
print(o.read().decode().strip())

print()
print('=== 4. 检查 tsensor.conf ===')
i, o, e = c.exec_command('cat /Agent/etc/tsensor.conf 2>/dev/null', timeout=10)
print(o.read().decode().strip()[:500] or '  NOT FOUND')

print()
print('=== 5. 检查 actl HTTP 访问 ===')
python_script = '''
import urllib.request
req = urllib.request.Request("http://127.0.0.1:10081/actl",
    data=b"node: NODE_PROBE\\nsrv: SRV_ALL\\nop: STATUS\\nid: \\"1\\"\\n",
    method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=10)
    print("HTTP:", resp.status)
except Exception as ex:
    print("ERROR:", str(ex)[:200])
'''
# Write script to remote
c.exec_command("cat > /tmp/check_actl.py << 'EOFSCRIPT'\n" + python_script + "\nEOFSCRIPT", timeout=10)
time.sleep(1)
i, o, e = c.exec_command("python3 /tmp/check_actl.py 2>&1", timeout=30)
print('  ' + o.read().decode().strip())

print()
print('=== 6. Apache 错误日志最近 10 行 ===')
i, o, e = c.exec_command('tail -10 /var/log/httpd/ly_error_log 2>/dev/null', timeout=10)
print(o.read().decode().strip()[:1000] or '  (no log)')

print()
print('=== 7. 检查当前 tsensor 进程 ===')
i, o, e = c.exec_command('ps -ef | grep -E "tsensor|probe" | grep -v grep', timeout=10)
print(o.read().decode().strip()[:500] or '  (no tsensor/probe running)')

c.close()