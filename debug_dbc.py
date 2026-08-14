import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Add debug logging to dbc.cpp to see what's happening
cmds = [
    ("patch dbc debug", r"""
cat > /root/SOC/ly_server_src/server/dbc.cpp << 'CPPEOF'
#include "dbc.h"
#include <fstream>
#include <sstream>

cppdb::session* start_db_session() {

  string user = SERVER_DB_USER;
  string dbdatabase = SERVER_DB_NAME;
  string mysql_group = SERVER_DB_GROUP;
  string line;
  string str, pass;
  size_t pos;
  
  // Debug: log what we're doing
  FILE* dbg = fopen("/tmp/dbc_debug.log", "w");
  if (dbg) {
    fprintf(dbg, "DB_CONF=%s\n", DB_CONF);
    fprintf(dbg, "user=%s db=%s group=%s\n", user.c_str(), dbdatabase.c_str(), mysql_group.c_str());
  }
  
  ifstream ifs(DB_CONF);
  if (dbg) fprintf(dbg, "ifs.is_open()=%d\n", ifs.is_open() ? 1 : 0);
  
  while(getline(ifs, line)) {
    if (dbg) fprintf(dbg, "RAW line=[%s] len=%zu\n", line.c_str(), line.size());
    trim(line);
    if (dbg) fprintf(dbg, "TRIM line=[%s] len=%zu\n", line.c_str(), line.size());
    if (line.empty() || line[0] == '#') continue;
    pos = line.find("=");
    if (pos != std::string::npos) {
      str = line.substr(0,pos);
      if (dbg) fprintf(dbg, "KEY=[%s]\n", str.c_str());
      if (str == "passwd") {
        pass = line.substr(pos + 1);
        if (dbg) fprintf(dbg, "PASS=[%s] len=%zu\n", pass.c_str(), pass.size());
        break;
      }
    } 
  }
  
  if (dbg) fprintf(dbg, "FINAL pass=[%s] empty=%d\n", pass.c_str(), pass.empty() ? 1 : 0);
  
  string conn = "mysql:database=" + dbdatabase + ";read_default_group=" + mysql_group + ";user=" + user;
  if (!pass.empty()) {
    conn += ";password=" + pass;
  }
  
  if (dbg) {
    fprintf(dbg, "CONN=[%s]\n", conn.c_str());
    fclose(dbg);
  }
  
  session* sql = new session(conn);
  return sql;
}
CPPEOF
echo "Patched with debug"
"""),
    
    ("rebuild", r"""
cd /root/SOC/ly_server_src/server
make auth 2>&1 | tail -5
cp auth /Server/www/d/auth
echo "Installed"
"""),
    
    ("test and check debug", r"""
# Clear old debug log
rm -f /tmp/dbc_debug.log
# Make sure apache can write to /tmp
chmod 1777 /tmp
# Test
curl -s http://localhost/d/auth 2>&1 | head -3
echo "---"
# Check debug log
echo "Debug log:"
cat /tmp/dbc_debug.log 2>/dev/null || echo "No debug log!"
echo "---"
# Check permissions
ls -la /tmp/dbc_debug.log 2>/dev/null
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
