import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check MySQL device - try different auth methods
i, o, e = c.exec_command("mysql -u admin -pP@ssw0rd -e 'SELECT id,name,port,interface,filter,tls_psk FROM server.t_device' 2>&1", timeout=30)
print('MySQL admin:', o.read().decode()[:500])

i, o, e = c.exec_command("mysql -u root -e \"SELECT id,name,port,interface,filter,tls_psk FROM server.t_device\" 2>&1", timeout=30)
print('MySQL root:', o.read().decode()[:500])

c.close()