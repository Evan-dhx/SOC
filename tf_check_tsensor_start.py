import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check how tsensor is started
items = [
    ('tsensor.service', 'cat /etc/systemd/system/tsensor.service 2>/dev/null'),
    ('tsensor_start.sh', 'cat /Agent/etc/tsensor_start.sh 2>/dev/null'),
    ('interface', 'cat /sys/class/net/ens192/address 2>/dev/null; echo; cat /sys/class/net/ens224/address 2>/dev/null'),
    ('running tsensor cmdline', "cat /proc/26355/cmdline 2>/dev/null | tr '\\0' ' '"),
]
for l, cmd in items:
    print(f'\n[{l}]')
    i, o, e = c.exec_command(cmd, timeout=30)
    out = o.read().decode()[:500]
    if out: print(out)
c.close()