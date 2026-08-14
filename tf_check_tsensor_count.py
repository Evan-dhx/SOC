import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check all tsensor processes and their PIDs
i, o, e = c.exec_command("ps -ef | grep -E 'sensor|probe' | grep -v grep; echo ---; pidof tsensor", timeout=30)
print('TSensor processes:', o.read().decode()[:500])

# Check if there are 2 tsensor processes
i, o, e = c.exec_command("ps -ef | grep tsensor | grep -v grep | wc -l", timeout=30)
print('Count:', o.read().decode()[:50])

# The problem: actl looks for "probe" but binary is "tsensor"
# Fix: modify actl's get_probe_status to also check for "tsensor"
i, o, e = c.exec_command("grep -n 'grep probe' /Agent/cmd/actl 2>/dev/null | head -5; echo ---; strings /Agent/cmd/actl | grep 'grep probe' | head -3", timeout=30)
print('Current probe detection:', o.read().decode()[:500])

c.close()