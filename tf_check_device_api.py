import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Use config CGI to get device list
i, o, e = c.exec_command("curl -s 'http://127.0.0.1/d/device?op=get' 2>/dev/null | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(f'id={x[\\\"id\\\"]} name={x[\\\"name\\\"]} ip={x.get(\\\"ip\\\",\\\"\\\")} port={x.get(\\\"port\\\",\\\"\\\")} interface={x.get(\\\"interface\\\",\\\"\\\")} filter={x.get(\\\"filter\\\",\\\"\\\")} psk={x.get(\\\"tls_psk\\\",\\\"\\\")} ') for x in d]\" 2>&1 | head -20", timeout=30)
print('Device list:', o.read().decode()[:1000])

# Check config file directly
i, o, e = c.exec_command("cat /Agent/data/config | head -30", timeout=30)
print('\nConfig top:', o.read().decode()[:500])

c.close()