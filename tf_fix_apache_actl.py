import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Add ScriptAlias for actl
i, o, e = c.exec_command(
    r"""sed -i '/^ScriptAlias \/extract_pcap/a\ScriptAlias /actl "/Agent/cmd/actl"' /etc/httpd/conf.d/ly_server.conf && echo OK || echo FAIL""",
    timeout=30)
print('Add actl alias:', o.read().decode()[:100])

# Verify
i, o, e = c.exec_command('grep actl /etc/httpd/conf.d/ly_server.conf', timeout=30)
print('Verify:', o.read().decode()[:200])

# Restart httpd
i, o, e = c.exec_command('apachectl restart 2>&1; sleep 2; systemctl is-active httpd', timeout=30)
print('Apache restart:', o.read().decode()[:200])

# Test actl
i, o, e = c.exec_command('curl -s -o /dev/null -w "%{http_code}" -X POST -d "test" http://127.0.0.1:10081/actl', timeout=30)
print('actl HTTP:', o.read().decode()[:100])

c.close()
print('\nDone')