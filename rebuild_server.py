import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# The fix: modify dbc.cpp to NOT pass password= in the connection string
# cppdb mysql backend reads password from MySQL config files via read_default_group
# The password= parameter is ignored or causes issues

cmds = [
    # 1. Check the current dbc.cpp
    ("current dbc", "cat /root/SOC/ly_server_src/server/dbc.cpp"),
    
    # 2. Patch dbc.cpp to remove password= from connection string
    ("patch dbc", r"""
cat > /root/SOC/ly_server_src/server/dbc.cpp << 'CPPEOF'
#include "dbc.h"

cppdb::session* start_db_session() {

  string user = SERVER_DB_USER;
  string dbdatabase = SERVER_DB_NAME;
  string mysql_group = SERVER_DB_GROUP;
  // Password is read from MySQL config file via read_default_group
  // cppdb mysql backend does not support password= in connection string
  session* sql = new session("mysql:database=" + dbdatabase + ";read_default_group=" + mysql_group + ";user=" + user);
  return sql;
}
CPPEOF
echo "Patched dbc.cpp:"
cat /root/SOC/ly_server_src/server/dbc.cpp
"""),
    
    # 3. Rebuild all CGI scripts
    ("rebuild cgi", r"""
cd /root/SOC/ly_server_src/server
make clean 2>/dev/null
make 2>&1 | tail -20
echo "Build exit: ${PIPESTATUS[0]}"
"""),
    
    # 4. Install new binaries
    ("install", r"""
# Copy new binaries to /Server/www/d/
cp /root/SOC/ly_server_src/server/auth /Server/www/d/auth
cp /root/SOC/ly_server_src/server/bwlist /Server/www/d/bwlist 2>/dev/null
cp /root/SOC/ly_server_src/server/config /Server/www/d/config 2>/dev/null
cp /root/SOC/ly_server_src/server/event /Server/www/d/event 2>/dev/null
cp /root/SOC/ly_server_src/server/feature /Server/www/d/feature 2>/dev/null
cp /root/SOC/ly_server_src/server/event_feature /Server/www/d/event_feature 2>/dev/null
cp /root/SOC/ly_server_src/server/mo /Server/www/d/mo 2>/dev/null
cp /root/SOC/ly_server_src/server/internalip /Server/www/d/internalip 2>/dev/null
echo "Installed. Checking:"
ls -la /Server/www/d/
"""),
    
    # 5. Test
    ("test CGI", r"""
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost/d/auth
curl -s http://localhost/d/auth 2>&1
"""),
    
    # 6. Check error log
    ("error log", "tail -5 /var/log/httpd/ly_error_log"),
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
