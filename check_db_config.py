import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check how CGI scripts get DB config
    ("strings auth db", "strings /Server/www/d/auth | grep -i 'mysql\\|database\\|db_\\|cppdb\\|connect\\|ly_server\\|ly_user\\|root@' | head -20"),
    
    # Check for config files
    ("etc dir", "ls -la /Server/etc/"),
    
    # Check environment variables in httpd
    ("env vars", "cat /etc/httpd/conf.d/ly_server.conf | grep -i 'SetEnv\\|db\\|mysql\\|database'"),
    
    # Check if there's a default DB connection string pattern
    ("auth source", "strings /Server/www/d/auth | grep -E 'mysql://|sqlite|cppdb|connection' | head -10"),
    
    # Check common config locations
    ("config files", "find /Server /Agent /data -name '*.ini' -o -name '*.conf' -o -name '*.cfg' -o -name '*.properties' 2>/dev/null | head -20"),
    
    # Check the ly_server source for DB connection pattern
    ("server source", "grep -r 'cppdb\\|mysql\\|connection' /root/SOC/ly_server_src/server/*.cpp 2>/dev/null | grep -v '.o:' | head -20"),
    
    # Check common config source
    ("common config", "grep -r 'mysql\\|cppdb\\|connection_string\\|db_url' /root/SOC/ly_server_src/common/config.cpp 2>/dev/null | head -20"),
    
    # Check if there's a config.proto that defines DB settings
    ("config proto", "grep -i 'mysql\\|database\\|db_' /root/SOC/ly_server_src/common/config.proto 2>/dev/null | head -10"),
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
