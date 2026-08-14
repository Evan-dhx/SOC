import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)
    print('SSH connected OK')
    
    stdin, stdout, stderr = client.exec_command('hostname; echo "---"; ls /root/SOC/ly_server_src/bin/ 2>/dev/null', timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(f'hostname+ls output: [{out}]')
    if err: print(f'STDERR: [{err}]')
    
    stdin, stdout, stderr = client.exec_command('which config_pusher; ls -la /home/Server/bin/config_pusher 2>/dev/null; file /home/Server/bin/config_pusher 2>/dev/null', timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(f'config_pusher: [{out}]')
    if err: print(f'STDERR: [{err}]')
    
    client.close()
except Exception as e:
    print(f'ERROR: {e}')