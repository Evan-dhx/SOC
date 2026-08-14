import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Find indexer DB config in source code
    ('indexer DB config', 'grep -rn "dbc\|mysql\|database\|host.*127.0.0.1\|password\|username" /root/SOC/ly_analyser_src/agent/indexing/*.cpp /root/SOC/ly_analyser_src/agent/indexing/*.h 2>/dev/null | head -15'),
    # Check dbc.h or dbc.cpp for connection details
    ('find dbc', 'find /root/SOC/ly_analyser_src -name "dbc*" 2>/dev/null'),
    ('check define.h for DB', 'cat /root/SOC/ly_analyser_src/agent/define.h 2>/dev/null | grep -i "db\|mysql\|host\|port\|user\|pass" | head -10'),
    # Check if indexer produces any stderr
    ('run indexer with stderr', 'cd /Agent/bin && sudo -u apache ./extractor -v 1 -t 1786669500 -i ./indexer 2>&1 | head -20'),
]

for label, cmd in cmds:
    print(f'\n[ {label} ]')
    i, o, e = c.exec_command(cmd, timeout=60)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    if out: print(out[:1000])
    if err: print(f'ERR: {err[:200]}')
c.close()