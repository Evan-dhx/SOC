import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    # 1. Write a small test program to check file reading
    ("write test prog", r"""
cat > /tmp/test_dbconf.cpp << 'CPPEOF'
#include <fstream>
#include <iostream>
#include <string>
using namespace std;

int main() {
    const char* DB_CONF = "/etc/my.cnf.d/gl.server.cnf";
    string pass;
    string line;
    ifstream ifs(DB_CONF);
    if (!ifs.is_open()) {
        cerr << "FAILED to open: " << DB_CONF << endl;
        return 1;
    }
    cerr << "File opened OK" << endl;
    while(getline(ifs, line)) {
        cerr << "Line: [" << line << "]" << endl;
        if (line.empty() || line[0] == '#') continue;
        size_t pos = line.find("=");
        if (pos != string::npos) {
            string str = line.substr(0, pos);
            cerr << "Key: [" << str << "]" << endl;
            if (str == "passwd") {
                pass = line.substr(pos + 1);
                cerr << "Password found: [" << pass << "]" << endl;
                break;
            }
        }
    }
    if (pass.empty()) {
        cerr << "Password is EMPTY!" << endl;
    }
    // Try to construct connection string
    string dbdatabase = "server";
    string mysql_group = "gl.server";
    string user = "root";
    string conn = "mysql:database=" + dbdatabase + ";read_default_group=" + mysql_group + ";user=" + user + ";password=" + pass;
    cerr << "Connection string: " << conn << endl;
    return 0;
}
CPPEOF
g++ -o /tmp/test_dbconf /tmp/test_dbconf.cpp -std=c++11 2>&1
echo "Compile exit: $?"
"""),
    
    # 2. Run test as root
    ("test as root", r"""
/tmp/test_dbconf 2>&1
"""),
    
    # 3. Run test as apache
    ("test as apache", r"""
su -s /bin/bash apache -c "/tmp/test_dbconf" 2>&1
"""),
    
    # 4. Check if the issue is the trim function
    ("check trim", r"""
grep -n 'trim' /root/SOC/ly_server_src/common/ly_strings.h 2>/dev/null | head -10
echo "---"
grep -rn 'void trim\|string trim\|inline.*trim' /root/SOC/ly_server_src/common/ 2>/dev/null | head -10
"""),
    
    # 5. The real issue might be that the binary was compiled on CentOS 7
    # and has ABI issues on AlmaLinux 9
    # Let's check the binary's linked libraries
    ("check binary libs", r"""
ldd /Server/www/d/auth 2>&1 | head -20
echo "---"
file /Server/www/d/auth
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
