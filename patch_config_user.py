import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Patch config_user.cpp to handle missing env vars
print("=== Patching config_user.cpp ===")
cmd = r"""
cd /root/SOC/ly_server_src/lib

# Backup
cp config_user.cpp config_user.cpp.orig

# Fix the getenv calls
sed -i 's|id = atoi(getenv("UID"));|const char* uid_env = getenv("UID"); id = uid_env ? atoi(uid_env) : 0;|' config_user.cpp
sed -i 's|level_ = getenv("LEVEL");|const char* lvl_env = getenv("LEVEL"); level_ = lvl_env ? lvl_env : "";|' config_user.cpp

echo "Patched. Showing diff:"
diff config_user.cpp.orig config_user.cpp | head -20

# Rebuild
make config_user.so 2>&1 | tail -5
echo "Build: ${PIPESTATUS[0]}"

# Deploy
cp config_user.so /Server/lib/
echo "Deployed"
"""
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))

# Test
print("\n=== Test user endpoint ===")
cmd2 = r"""
> /var/log/httpd/ly_error_log
curl -s -c /tmp/cookies http://localhost/d/auth -d "auth_target=login&auth_user=admin&auth_pass=admin" > /dev/null

echo "User response:"
curl -s -b /tmp/cookies http://localhost/d/config -d "op=get&type=user" 2>&1 | head -c 500
echo ""

echo ""
echo "Errors:"
cat /var/log/httpd/ly_error_log
echo "(end)"
"""
stdin, stdout, stderr = client.exec_command(cmd2, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
