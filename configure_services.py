import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# ============================================================
# Step 1: Configure httpd for CGI
# ============================================================
print("=== Step 1: Configuring httpd for CGI ===")
cmd = r"""
# Install CGI module if not present
yum install -y httpd 2>&1 | tail -5

# Create httpd config for ly_server CGI
cat > /etc/httpd/conf.d/ly_server.conf << 'EOF'
# LiuYing SOC Platform - CGI Configuration
ServerName 10.10.102.220

# Set document root to Server/www
DocumentRoot "/Server/www"

<Directory "/Server/www">
    Options +ExecCGI +FollowSymLinks +Indexes
    AllowOverride None
    Require all granted
    DirectoryIndex index.html
</Directory>

# CGI script alias for /d/ path
ScriptAlias /d/ "/Server/www/d/"

<Directory "/Server/www/d">
    Options +ExecCGI
    AllowOverride None
    Require all granted
    AddHandler cgi-script .cgi .pl
    SetHandler cgi-script
</Directory>

# UI static files
Alias /ui/ "/Server/www/ui/"
<Directory "/Server/www/ui">
    Options +FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>

# Set LD_LIBRARY_PATH for CGI scripts
SetEnv LD_LIBRARY_PATH "/Agent/lib:/Server/lib:/usr/local/lib"

# Error and access logs
ErrorLog "/var/log/httpd/ly_error_log"
CustomLog "/var/log/httpd/ly_access_log" combined
EOF

echo "httpd config created"

# Fix SELinux context for CGI directories (if SELinux is enforcing)
if [ "$(getenforce 2>/dev/null)" != "Disabled" ]; then
    setsebool -P httpd_enable_cgi 1
    chcon -Rt httpd_sys_script_exec_t /Server/www/d/
    chcon -Rt httpd_sys_content_t /Server/www/
    echo "SELinux contexts set"
else
    echo "SELinux is disabled"
fi

# Set proper permissions
chmod 755 /Server/www/d/*
chmod 755 /Server
chmod 755 /Server/www

echo "httpd configured"
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# ============================================================
# Step 2: Start MariaDB and create database
# ============================================================
print("\n=== Step 2: Starting MariaDB ===")
cmd2 = r"""
# Start and enable MariaDB
systemctl start mariadb
systemctl enable mariadb
systemctl status mariadb | head -5

# Create database and user for ly_server
mysql -u root << 'SQLEOF'
CREATE DATABASE IF NOT EXISTS ly_server DEFAULT CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS ly_agent DEFAULT CHARACTER SET utf8mb4;

-- Create user for the application
CREATE USER IF NOT EXISTS 'ly_user'@'localhost' IDENTIFIED BY 'ly_pass_2024';
GRANT ALL PRIVILEGES ON ly_server.* TO 'ly_user'@'localhost';
GRANT ALL PRIVILEGES ON ly_agent.* TO 'ly_user'@'localhost';
FLUSH PRIVILEGES;

-- Show databases
SHOW DATABASES;
SQLEOF

echo "MariaDB configured"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# ============================================================
# Step 3: Configure firewall
# ============================================================
print("\n=== Step 3: Configuring firewall ===")
cmd3 = r"""
# Start and enable firewalld
systemctl start firewalld 2>/dev/null
systemctl enable firewalld 2>/dev/null

# Open HTTP port (80)
firewall-cmd --permanent --add-service=http 2>/dev/null
# Open HTTPS port (443)
firewall-cmd --permanent --add-service=https 2>/dev/null
# Open netflow port (9995 typical for nfcapd)
firewall-cmd --permanent --add-port=9995/udp 2>/dev/null
# Open sflow port (6343)
firewall-cmd --permanent --add-port=6343/udp 2>/dev/null

# Reload firewall
firewall-cmd --reload 2>/dev/null

# Show active rules
firewall-cmd --list-all 2>/dev/null

echo "Firewall configured"
"""
stdin, stdout, stderr = client.exec_command(cmd3, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# ============================================================
# Step 4: Set up cron jobs
# ============================================================
print("\n=== Step 4: Setting up cron jobs ===")
cmd4 = r"""
# Create cron jobs for ly_agent
cat > /etc/cron.d/ly_agent << 'EOF'
# LiuYing Agent scheduled tasks
# Run config_pusher every 5 minutes
*/5 * * * * root /Server/bin/config_pusher >> /data/log/config_pusher.log 2>&1

# Run indexer process check every minute
* * * * * root /Agent/bin/launch_indexer.sh >> /data/log/indexer.log 2>&1

# Clean old flow data daily at 2am
0 2 * * * root find /data/flow -name "*.old" -delete >> /data/log/cleanup.log 2>&1
EOF

# Create log directory
mkdir -p /data/log

# Start and enable crond
systemctl start crond
systemctl enable crond

echo "Cron jobs configured"
"""
stdin, stdout, stderr = client.exec_command(cmd4, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

# ============================================================
# Step 5: Start httpd
# ============================================================
print("\n=== Step 5: Starting httpd ===")
cmd5 = r"""
# Test httpd config first
httpd -t 2>&1

# Start httpd
systemctl start httpd
systemctl enable httpd
systemctl status httpd | head -5

echo ""
echo "=== Service status summary ==="
echo "httpd: $(systemctl is-active httpd)"
echo "mariadb: $(systemctl is-active mariadb)"
echo "crond: $(systemctl is-active crond)"
echo "firewalld: $(systemctl is-active firewalld)"
"""
stdin, stdout, stderr = client.exec_command(cmd5, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print(f"STDERR: {err}")

client.close()
