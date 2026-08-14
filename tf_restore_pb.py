import paramiko, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Upload config.pb.h and config.pb.cc from local workspace (pregenerated)
sftp = c.open_sftp()
for f in ['config.pb.h', 'config.pb.cc']:
    local = rf'd:\QorderProject\SOC\ly_analyser\src\common\{f}'
    if os.path.isfile(local):
        sftp.put(local, f'/root/SOC/ly_analyser_src/common/{f}')
        print(f'Uploaded {f} ({os.path.getsize(local)} bytes)')
    else:
        print(f'Local {f} not found!')
sftp.close()

# Rebuild config.a
i, o, e = c.exec_command('cd /root/SOC/ly_analyser_src/agent/config && make 2>&1 | tail -3', timeout=120)
print('config.a:', o.read().decode()[:300])
c.close()