import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check INSTALL.md for configuration guidance
    "echo '=== INSTALL.md ==='",
    "cat /root/SOC/ly_analyser_src/INSTALL.md 2>/dev/null | head -80",
    
    "echo '=== Server INSTALL.md ==='",
    "cat /root/SOC/ly_server_src/INSTALL.md 2>/dev/null | head -80",
    
    # Check existing httpd config
    "echo '=== Current httpd status ==='",
    "systemctl status httpd 2>&1 | head -5",
    
    "echo '=== httpd config dir ==='",
    "ls /etc/httpd/conf.d/ 2>/dev/null",
    
    # Check MariaDB status
    "echo '=== MariaDB status ==='",
    "systemctl status mariadb 2>&1 | head -5",
    
    # Check Server directory structure
    "echo '=== Server directory ==='",
    "ls -la /Server/ 2>/dev/null",
    "ls -la /Server/www/ 2>/dev/null",
    "ls -la /Server/www/d/ 2>/dev/null",
    "ls -la /Server/bin/ 2>/dev/null",
    
    # Check data directory
    "echo '=== Data directory ==='",
    "ls -la /data/ 2>/dev/null",
    
    # Check if there are any config templates
    "echo '=== Config templates ==='",
    "find /root/SOC -name '*.conf' -o -name 'httpd*' -o -name 'cron*' 2>/dev/null | head -20",
    
    # Check existing cron
    "echo '=== Current crontab ==='",
    "crontab -l 2>/dev/null",
]

for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out)
    if err and 'warning' not in err.lower() and 'no crontab' not in err.lower():
        print(f"STDERR: {err}")
    print()

client.close()
