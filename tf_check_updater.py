import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

for label, cmd in [
    ('config_updater 二进制信息', 'ls -la /home/Agent/cmd/config_updater; file /home/Agent/cmd/config_updater; md5sum /home/Agent/cmd/config_updater'),
    ('源码尺寸', 'ls -la /root/SOC/ly_analyser_src/handlers/config_updater.cpp 2>/dev/null; wc -l /root/SOC/ly_analyser_src/handlers/config_updater.cpp 2>/dev/null'),
    ('httpd 错误日志', 'tail -20 /var/log/httpd/error_log 2>/dev/null || tail -20 /etc/httpd/logs/error_log 2>/dev/null || echo "no httpd logs"'),
    ('httpd 访问日志最后5条', 'tail -5 /var/log/httpd/access_log 2>/dev/null || tail -5 /etc/httpd/logs/access_log 2>/dev/null'),
    ('CGI 模拟 POST', 'cd /Agent/data; echo "controller { host: \"127.0.0.1\" port: \"10081\" } dev { id:1 name:\"test\" psk:\"abc123\" }" > /tmp/test_post.txt; REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=POST CONTENT_LENGTH=$(wc -c < /tmp/test_post.txt) /home/Agent/cmd/config_updater < /tmp/test_post.txt 2>&1; echo; echo CGI_EXIT=$?'),
    ('CGI 后配置', 'echo === config ===; cat /Agent/data/config; echo; wc -c /Agent/data/config'),
]:
    print(f'\n=== {label} ===')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(out[:1500])
    if err: print(f'STDERR: {err[:500]}')
client.close()