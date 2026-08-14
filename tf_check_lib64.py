import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

print('=== 1. Find ALL libcommon.so on system ===')
i, o, e = c.exec_command("find / -name 'libcommon.so' -type f 2>/dev/null", timeout=30)
result = o.read().decode().strip()
print(result)

print()
print('=== 2. Check ldd for all relevant binaries ===')
for binpath in ['/Agent/cmd/actl', '/Agent/bin/config_updater', '/Server/bin/config_pusher', '/Agent/cmd/fsd']:
    i, o, e = c.exec_command(f"ldd {binpath} 2>/dev/null | grep -i common", timeout=10)
    out = o.read().decode().strip()
    print(f'  {binpath}: {out}')

print()
print('=== 3. Check LD_LIBRARY_PATH in Apache env ===')
i, o, e = c.exec_command("grep -i 'LD_LIBRARY_PATH\|libcommon' /etc/httpd/conf.d/ly_server.conf 2>/dev/null", timeout=10)
print(o.read().decode().strip()[:1000])

print()
print('=== 4. Compare md5sum of all libcommon.so ===')
instances = result.split('\n')
for p in instances:
    if p:
        i, o, e = c.exec_command(f"md5sum {p}", timeout=10)
        print(o.read().decode().strip())

c.close()