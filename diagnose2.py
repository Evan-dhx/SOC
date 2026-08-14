import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check app-config/config.js content
    ("config.js", "cat /Server/www/ui/app-config/config.js"),
    
    # Check static resources accessible
    ("static js", "curl -s -o /dev/null -w '%{http_code}' http://10.10.102.220/ui/static/js/main.bff3bffb.chunk.js"),
    ("static css", "curl -s -o /dev/null -w '%{http_code}' http://10.10.102.220/ui/static/css/main.c025dfb1.chunk.css"),
    
    # Check if iptables has any DROP rules
    ("iptables", "iptables -L -n 2>/dev/null | head -30"),
    
    # Check ip address binding
    ("ip addr", "ip addr show ens192 | head -5"),
    
    # Check if there's a network-level firewall (iptables INPUT chain)
    ("iptables INPUT", "iptables -L INPUT -n 2>/dev/null"),
    
    # Check the welcome.conf - it might override our config
    ("welcome.conf", "cat /etc/httpd/conf.d/welcome.conf"),
    
    # Check if httpd has any deny rules
    ("httpd deny", "grep -r 'Require all denied\\|Deny from' /etc/httpd/conf/ /etc/httpd/conf.d/ 2>/dev/null"),
    
    # Check the /Server symlink
    ("Server symlink", "ls -la / | grep Server"),
    
    # Test full page load with all resources
    ("full test", "curl -s http://10.10.102.220/ui/static/js/2.2db6edf7.chunk.js 2>/dev/null | wc -c"),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err and 'warning' not in err.lower():
        print(f"STDERR: {err}")

client.close()
