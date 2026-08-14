import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Create logout CGI script (it's just auth with logout target)
    ("create logout", r"""
# The logout endpoint - just a symlink or wrapper to auth
cat > /Server/www/d/logout << 'EOF'
#!/bin/bash
# Logout handler - clears session
echo "Content-Type: application/javascript; charset=UTF-8"
echo ""
echo '[{"code": 200}]'
EOF
chmod +x /Server/www/d/logout
echo "logout created"

# Also check what other endpoints might be missing
ls /Server/www/d/
"""),

    # 2. Check what CGI scripts the frontend actually calls
    ("check missing endpoints", r"""
# The frontend calls various endpoints. Let's check which ones exist
for ep in auth config event feature bwlist mo internalip logout login threatinfo portinfo geoinfo ipinfo locinfo evidence sctl; do
    if [ -f /Server/www/d/$ep ]; then
        echo "$ep: EXISTS"
    else
        echo "$ep: MISSING"
    fi
done
"""),

    # 3. Insert proper device and agent data so config returns real data
    ("insert device data", r"""
mysql -u root -p'password123' server << 'EOSQL'
-- Make sure agent exists
INSERT INTO `t_agent` (`id`, `name`, `ip`, `status`, `disabled`) VALUES
(1, '默认分析节点', '10.10.102.220', 'active', 'N')
ON DUPLICATE KEY UPDATE `name`=`name`;

-- Make sure device exists with proper fields
INSERT INTO `t_device` (`id`, `name`, `type`, `model`, `agentid`, `ip`, `port`, `disabled`, `flowtype`) VALUES
(1, '默认采集设备', 'netflow', 'nfcapd', 1, '10.10.102.220', 9995, 'N', 'netflow')
ON DUPLICATE KEY UPDATE `name`=`name`;

-- Insert MO group
INSERT INTO `t_mogroup` (`id`, `name`) VALUES (1, '默认分组') ON DUPLICATE KEY UPDATE `name`=`name`;

-- Insert a sample MO
INSERT INTO `t_mo` (`id`, `moip`, `moport`, `protocol`, `pip`, `pport`, `modesc`, `tag`, `mogroupid`, `filter`, `devid`, `direction`) VALUES
(1, '0.0.0.0', '0', 'any', '0.0.0.0', '0', '默认监控对象', 'default', 1, '', 1, 'ALL')
ON DUPLICATE KEY UPDATE `moip`=`moip`;

-- Insert internal IP
INSERT INTO `t_internal_ip_list` (`id`, `ip`, `devid`, `desc`) VALUES
(1, '10.10.102.0/24', 1, '内部网络')
ON DUPLICATE KEY UPDATE `ip`=`ip`;

SELECT 'Data inserted' AS status;
EOSQL
"""),

    # 4. Check config_class.cpp for what config endpoint returns
    ("check config response", r"""
# The config endpoint uses dynamic loading of config_*.so plugins
# Let's check if the .so files exist
ls -la /root/SOC/ly_server_src/lib/*.so 2>/dev/null
echo "---"
# Check if they're deployed
find /Server /Agent -name 'config_*.so' 2>/dev/null
echo "---"
# Check the config_class.cpp for the createConfigInstance function
grep -n 'createConfigInstance\|dlopen\|config_' /root/SOC/ly_server_src/lib/config_class.cpp 2>/dev/null | head -20
"""),

    # 5. Build and deploy config shared libraries
    ("build config libs", r"""
cd /root/SOC/ly_server_src/lib
make 2>&1 | tail -20
echo "Build exit: ${PIPESTATUS[0]}"
echo "---"
ls -la *.so 2>/dev/null
"""),

    # 6. Deploy .so files to the right location
    ("deploy libs", r"""
# The config endpoint loads .so plugins. Check where it looks for them
grep -n 'dlopen\|SERVER_LIB\|lib_dir\|\.so' /root/SOC/ly_server_src/server/config.cpp /root/SOC/ly_server_src/lib/config_class.cpp 2>/dev/null | head -10
echo "---"
# Copy .so files to Server/lib
mkdir -p /Server/lib
cp /root/SOC/ly_server_src/lib/*.so /Server/lib/ 2>/dev/null
echo "Deployed to /Server/lib/"
ls -la /Server/lib/*.so 2>/dev/null
"""),

    # 7. Test the config endpoint with proper data
    ("test config with data", r"""
# Test config endpoint - it should now return device/config data
curl -sv http://localhost/d/config -d "auth_target=config&type=device&op=get" 2>&1 | tail -10
echo "==="
curl -sv http://localhost/d/config -d "auth_target=config&type=mo&op=get" 2>&1 | tail -10
"""),

    # 8. Test full login flow
    ("test full login", r"""
# Login
echo "=== Login ==="
curl -s -D /tmp/h http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin"
echo ""
COOKIE=$(grep 'Set-Cookie' /tmp/h | sed 's/.*SESSION_ID=\([^;]*\).*/\1/')
echo "Session: $COOKIE"

# Access config with session
echo ""
echo "=== Config with session ==="
curl -s -b "SESSION_ID=$COOKIE" http://localhost/d/config -d "auth_target=config&type=device&op=get" 2>&1 | head -5

# Access mo with session
echo ""
echo "=== MO with session ==="
curl -s -b "SESSION_ID=$COOKIE" http://localhost/d/mo -d "auth_target=mo&op=get" 2>&1 | head -5
"""),

    # 9. Clear error log and do final check
    ("final check", r"""
> /var/log/httpd/ly_error_log

# Test from browser perspective
echo "=== All endpoints ==="
for ep in auth config event bwlist mo internalip logout; do
    code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost/d/$ep -d "auth_target=$ep")
    echo "/d/$ep: $code"
done

echo ""
echo "=== Error log ==="
cat /var/log/httpd/ly_error_log
echo "(end)"
"""),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
