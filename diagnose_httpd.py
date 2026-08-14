import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Check httpd listening address
    ("httpd listening", "ss -tlnp | grep httpd"),
    
    # 2. Check httpd full config
    ("httpd conf", "cat /etc/httpd/conf/httpd.conf | grep -E 'Listen|ServerName|DocumentRoot|Directory' | head -20"),
    
    # 3. Check our custom config
    ("ly config", "cat /etc/httpd/conf.d/ly_server.conf"),
    
    # 4. Check httpd error log
    ("error log", "tail -30 /var/log/httpd/ly_error_log 2>/dev/null || tail -30 /var/log/httpd/error_log 2>/dev/null"),
    
    # 5. Test from localhost with full URL
    ("curl ui", "curl -v http://localhost/ui/ 2>&1 | head -30"),
    
    # 6. Test from external IP
    ("curl external", "curl -v http://10.10.102.220/ui/ 2>&1 | head -30"),
    
    # 7. Check firewall rules in detail
    ("firewall", "firewall-cmd --list-all"),
    
    # 8. Check if httpd can read files
    ("file perms", "namei -l /Server/www/ui/index.html"),
    
    # 9. Check httpd user
    ("httpd user", "grep -E '^User|^Group' /etc/httpd/conf/httpd.conf"),
    
    # 10. Check SELinux
    ("selinux", "getenforce 2>/dev/null"),
    
    # 11. Check httpd main config for welcome page override
    ("welcome", "ls /etc/httpd/conf.d/"),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(err)

client.close()
