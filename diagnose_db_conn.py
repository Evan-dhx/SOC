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

# ===== 1. 旧库 SONAME =====
run('objdump -p /usr/local/lib/libprotobuf.so.19.0.0.bak.old 2>/dev/null | grep SONAME', "旧库 SONAME")
run('objdump -p /usr/local/lib/libprotobuf.so.19.0.0 2>/dev/null | grep SONAME', "新库 SONAME")

# ===== 2. config_pusher 数据库连接配置 =====
run('cat /etc/my.cnf.d/gl.server.cnf 2>/dev/null || echo "(文件不存在)"', "gl.server.cnf 配置")
run('cat /etc/my.cnf 2>/dev/null', "/etc/my.cnf")
run('find /etc/my.cnf.d -type f 2>/dev/null', "my.cnf.d 文件列表")

# ===== 3. config_pusher 链接的库 =====
run('ldd /Server/bin/config_pusher 2>/dev/null | head -20', "config_pusher ldd")
run('ldd /Agent/bin/nfdump 2>/dev/null | head -20', "nfdump ldd")
run('ldd /Agent/bin/extractor 2>/dev/null | head -20', "extractor ldd")

# ===== 4. config_pusher 需要的 protobuf 符号 =====
run('nm -D /Server/bin/config_pusher 2>/dev/null | grep "U.*protobuf.*Add" | head -10', "config_pusher 未定义的 protobuf Add 符号")
run('nm -D /Agent/bin/nfdump 2>/dev/null | grep "U.*protobuf.*Add" | head -10', "nfdump 未定义的 protobuf Add 符号")

# ===== 5. httpd error_log =====
run('cat /etc/httpd/logs/ly_error_log 2>/dev/null | tail -30', "httpd ly_error_log 最近30行")

# ===== 6. config_pusher 当前 crontab =====
run('crontab -l 2>/dev/null', "当前 crontab")

c.close()
print("\n诊断完成!")
