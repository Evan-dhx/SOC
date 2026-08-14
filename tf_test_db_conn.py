import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Test config_pusher exit code", r"""
echo "=== 1. 直接运行看退出码 ==="
cd /Server/bin
./config_pusher d
echo "EXIT:$?"
echo ""
echo "=== 2. journal 中 config_pusher 日志 ==="
journalctl --no-pager --since '10 minutes ago' 2>/dev/null | grep -iE "config_pusher|pusher" | tail -10
echo ""
echo "=== 3. 测试 cppdb 连接（最小程序） ==="
cat > /tmp/test_db.cpp << 'EOF'
#include <cppdb/frontend.h>
#include <fstream>
#include <iostream>
#include <string>
using namespace std;
int main() {
    string user = "root";
    string db = "server";
    string group = "gl.server";
    string line, str, pass;
    size_t pos;
    ifstream ifs("/etc/my.cnf.d/gl.server.cnf");
    while(getline(ifs, line)) {
        if (line.empty() || line[0] == '#') continue;
        pos = line.find("=");
        if (pos != string::npos) {
            str = line.substr(0,pos);
            if (str == "passwd") { pass = line.substr(pos+1); break; }
        }
    }
    string conn = "mysql:database=" + db + ";read_default_group=" + group + ";user=" + user;
    if (!pass.empty()) conn += ";password=" + pass;
    cout << "conn: " << conn << endl;
    try {
        cppdb::session sql(conn);
        cppdb::result r = sql << "SELECT COUNT(*) FROM t_device";
        long long cnt = 0;
        if (r.next()) r >> cnt;
        cout << "t_device count: " << cnt << endl;
        return 0;
    } catch (std::exception const &e) {
        cout << "ERROR: " << e.what() << endl;
        return 1;
    }
}
EOF
g++ -o /tmp/test_db /tmp/test_db.cpp -I/usr/include/cppdb -lcppdb
/tmp/test_db
echo "Test exit: $?"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
