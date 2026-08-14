import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label):
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(f"\n{'='*60}")
    print(f"[{label}]")
    print(f"{'='*60}")
    print(out.strip() if out.strip() else "(无输出)")
    if err.strip():
        print(f"STDERR: {err.strip()[:500]}")

# ===== 1. 检查新旧 protobuf 库符号差异 =====
run('nm -D /usr/local/lib/libprotobuf.so.19.0.0 2>/dev/null | grep AddDescriptors | head -5', "新库 (4.2MB) AddDescriptors 符号")
run('nm -D /usr/local/lib/libprotobuf.so.19.0.0.bak.old 2>/dev/null | grep AddDescriptors | head -5', "旧库 (9.9MB) AddDescriptors 符号")
run('nm -D /usr/local/lib/libprotobuf.so.19.0.0.bak.old 2>/dev/null | grep "Device.*default_type" | head -3', "旧库 config::Device 符号")
run('nm -D /usr/local/lib/libprotobuf.so.19.0.0 2>/dev/null | grep "Device.*default_type" | head -3', "新库 config::Device 符号")

# ===== 2. config_pusher 数据库连接配置 =====
run('strings /Server/bin/config_pusher | grep -i "database\\|mysql\\|server\\|db:" | head -10', "config_pusher 数据库连接字符串")
run('cat /Server/etc/dbc.conf 2>/dev/null || cat /Server/etc/dbc.cfg 2>/dev/null || echo "(dbc.conf 不存在)"', "dbc.conf 配置")

# ===== 3. 查找 dbc 配置文件 =====
run('find /Server -name "dbc*" -o -name "*.conf" 2>/dev/null | head -20', "Server 配置文件")
run('strings /Server/bin/config_pusher | grep -E "mysql://|tcp://|host=|user=|password=" | head -5', "config_pusher MySQL 连接串")

# ===== 4. t_event_list 和 t_event_status 表结构 =====
run('mysql -u root -e "USE server; DESCRIBE t_event_list;" 2>&1', "t_event_list 表结构")
run('mysql -u root -e "USE server; DESCRIBE t_event_status;" 2>&1', "t_event_status 表结构")

# ===== 5. 检查 config_pusher 需要的 protobuf 版本 =====
run('strings /Server/bin/config_pusher | grep -i "protobuf" | head -5', "config_pusher protobuf 版本信息")
run('strings /Agent/bin/nfdump | grep -i "protobuf" | head -5', "nfdump protobuf 版本信息")

# ===== 6. 检查 LD_LIBRARY_PATH =====
run('cat /etc/ld.so.conf.d/*.conf 2>/dev/null | head -10', "ld.so.conf.d 配置")
run('ldconfig -p 2>/dev/null | grep protobuf | head -10', "ldconfig protobuf")

# ===== 7. launch_indexer.sh 脚本内容 =====
run('cat /Agent/bin/launch_indexer.sh 2>/dev/null', "launch_indexer.sh 脚本")

# ===== 8. httpd ServerRoot =====
run('grep -i "ServerRoot" /etc/httpd/conf/httpd.conf 2>/dev/null', "httpd ServerRoot")
run('ls -la /etc/httpd/logs/ 2>/dev/null || echo "(/etc/httpd/logs/ 不存在)"', "httpd logs 目录")

c.close()
print("\n诊断完成!")
