import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Fix the config file: use "passwd=" instead of "password="
    ("fix config", r"""
cat > /etc/my.cnf.d/gl.server.cnf << 'EOF'
[client]
user=root
passwd=password123

[gl.server]
user=root
passwd=password123
EOF
chmod 644 /etc/my.cnf.d/gl.server.cnf
echo "Fixed config:"
cat /etc/my.cnf.d/gl.server.cnf
"""),
    
    # Also rebuild dbc.cpp without debug logging (clean version)
    ("clean dbc", r"""
cat > /root/SOC/ly_server_src/server/dbc.cpp << 'CPPEOF'
#include "dbc.h"

cppdb::session* start_db_session() {

  string user = SERVER_DB_USER;
  string dbdatabase = SERVER_DB_NAME;
  string mysql_group = SERVER_DB_GROUP;
  string line;
  string str, pass;
  size_t pos;
  ifstream ifs(DB_CONF);
  while(getline(ifs, line)) {
    trim(line);
    if (line.empty() || line[0] == '#') continue;
    pos = line.find("=");
    if (pos != std::string::npos) {
      str = line.substr(0,pos);
      if (str == "passwd") {
        pass = line.substr(pos + 1);
        break;
      }
    } 
  }
  string conn = "mysql:database=" + dbdatabase + ";read_default_group=" + mysql_group + ";user=" + user;
  if (!pass.empty()) {
    conn += ";password=" + pass;
  }
  session* sql = new session(conn);
  return sql;
}
CPPEOF

cd /root/SOC/ly_server_src/server
make auth 2>&1 | tail -3
cp auth /Server/www/d/auth
echo "Clean rebuild done"
"""),
    
    # Test
    ("test", r"""
rm -f /Server/log/dbc_debug.log
curl -s http://localhost/d/auth 2>&1
echo "---"
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost/d/auth
echo "---"
tail -3 /var/log/httpd/ly_error_log
"""),
]

for label, cmd in cmds:
    print(f"\n=== {label} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")

client.close()
