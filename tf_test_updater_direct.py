import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Direct test: Check if config_updater works with proper content
i, o, e = c.exec_command("CONTENT_LENGTH=$(echo -n 'dev { id: 1 port: 9995 interface: \"ens192\" }' | wc -c) REQUEST_METHOD=POST REMOTE_ADDR=127.0.0.1 /Agent/cmd/config_updater < /tmp/pt.txt 2>&1; echo; cat /Agent/data/config", timeout=30)
print('CGI test:', o.read().decode()[:500])

# Restore the config with config_updater
i, o, e = c.exec_command("printf 'dev { id: 1 port: 9995 interface: \"ens192\" }' > /tmp/pt.txt; CONTENT_LENGTH=$(wc -c < /tmp/pt.txt) REQUEST_METHOD=POST REMOTE_ADDR=127.0.0.1 /Agent/cmd/config_updater < /tmp/pt.txt 2>&1; echo; wc -c /Agent/data/config; head -3 /Agent/data/config", timeout=30)
print('CGI restore:', o.read().decode()[:500])

c.close()