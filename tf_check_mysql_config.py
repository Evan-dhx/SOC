import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Check MySQL device
i, o, e = c.exec_command("mysql -uroot -pP@ssw0rd server -e 'SELECT id,name,ip,port,interface,filter,template,pcap_level,tls_psk FROM t_device' 2>&1", timeout=30)
print('DB:', o.read().decode()[:500])

# Check pushed config dev section
i, o, e = c.exec_command("sed -n '/^dev {/,/^}/p' /Agent/data/config | head -20", timeout=30)
print('Config dev:', o.read().decode()[:500])

# Check tsensor.conf
i, o, e = c.exec_command("cat /Agent/etc/tsensor.conf 2>/dev/null", timeout=30)
print('tsensor.conf:', o.read().decode()[:500])

c.close()