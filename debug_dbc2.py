import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # Check if httpd has PrivateTmp
    ("check PrivateTmp", r"""
systemctl show httpd | grep -i 'private\|tmp\|namespace'
echo "---"
grep -i 'PrivateTmp' /usr/lib/systemd/system/httpd.service 2>/dev/null
"""),
    
    # Check httpd private tmp
    ("check private tmp", r"""
ls -la /tmp/systemd-private-*/tmp/ 2>/dev/null | head -5
echo "---"
# Also check if there's a dbc_debug.log anywhere
find / -name 'dbc_debug.log' 2>/dev/null
"""),
    
    # Patch to use /Server/log/ instead of /tmp
    ("patch log path", r"""
mkdir -p /Server/log
chmod 777 /Server/log

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
  
  FILE* dbg = fopen("/Server/log/dbc_debug.log", "w");
  if (dbg) {
    fprintf(dbg, "DB_CONF=%s\n", DB_CONF);
    fprintf(dbg, "user=%s db=%s group=%s\n", user.c_str(), dbdatabase.c_str(), mysql_group.c_str());
    fflush(dbg);
  }
  
  ifstream ifs(DB_CONF);
  if (dbg) { fprintf(dbg, "ifs.is_open()=%d\n", ifs.is_open() ? 1 : 0); fflush(dbg); }
  
  while(getline(ifs, line)) {
    if (dbg) { fprintf(dbg, "RAW line=[%s] len=%zu\n", line.c_str(), line.size()); fflush(dbg); }
    trim(line);
    if (dbg) { fprintf(dbg, "TRIM line=[%s] len=%zu\n", line.c_str(), line.size()); fflush(dbg); }
    if (line.empty() || line[0] == '#') continue;
    pos = line.find("=");
    if (pos != std::string::npos) {
      str = line.substr(0,pos);
      if (dbg) { fprintf(dbg, "KEY=[%s]\n", str.c_str()); fflush(dbg); }
      if (str == "passwd") {
        pass = line.substr(pos + 1);
        if (dbg) { fprintf(dbg, "PASS=[%s] len=%zu\n", pass.c_str(), pass.size()); fflush(dbg); }
        break;
      }
    } 
  }
  
  if (dbg) { fprintf(dbg, "FINAL pass=[%s] empty=%d\n", pass.c_str(), pass.empty() ? 1 : 0); fflush(dbg); }
  
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

cd /root/SOC/ly_server_src/server
make auth 2>&1 | tail -3
cp auth /Server/www/d/auth
echo "Rebuilt and installed"
"""),
    
    # Test
    ("test", r"""
rm -f /Server/log/dbc_debug.log
curl -s http://localhost/d/auth 2>&1 | head -3
echo "==="
echo "Debug log:"
cat /Server/log/dbc_debug.log 2>/dev/null || echo "No debug log!"
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
