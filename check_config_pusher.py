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

# ===== 1. config_pusher 最近日志 =====
run('journalctl -t config_pusher --no-pager -n 30 2>/dev/null', "config_pusher 最近30条 syslog")

# ===== 2. config_pusher 日志文件 =====
run('tail -30 /data/log/config_pusher.log 2>/dev/null || echo "(config_pusher.log 不存在)"', "config_pusher.log 最近30行")

# ===== 3. 检查 t_config 表 =====
run('mysql -u root -e "USE server; SHOW TABLES;" 2>/dev/null || echo "(server 数据库不存在)"', "server 数据库表列表")
run('mysql -u root -e "USE ly_server; SHOW TABLES LIKE \'t_config%\';" 2>/dev/null', "ly_server 数据库 t_config 表")

# ===== 4. 检查 t_event_config_dns_tunnel 表结构 =====
run('mysql -u root -e "USE server; DESCRIBE t_event_config_dns_tunnel;" 2>/dev/null || mysql -u root -e "USE ly_server; DESCRIBE t_event_config_dns_tunnel;" 2>/dev/null || echo "(t_event_config_dns_tunnel 表不存在)"', "t_event_config_dns_tunnel 表结构")

# ===== 5. 查看 config_pusher 源码中的 SQL 查询 =====
run('grep -n "dns_tunnel" /Server/bin/config_pusher 2>/dev/null | head -5 || echo "(非文本文件)"', "config_pusher 二进制中 dns_tunnel")

# ===== 6. tsensor 最近日志 =====
run('journalctl -t tsensor --no-pager -n 20 2>/dev/null', "tsensor 最近20条 syslog")
run('journalctl -t tsensor --no-pager --since "10 min ago" 2>/dev/null', "tsensor 最近10分钟日志")

# ===== 7. tsensor crash 检查 =====
run('journalctl --no-pager --since "1 hour ago" 2>/dev/null | grep -i "tsensor.*segfault\\|tsensor.*crash\\|tsensor.*killed" | tail -10', "tsensor segfault (最近1小时)")
run('journalctl --no-pager --since "1 hour ago" 2>/dev/null | grep -i "extractor.*fault\\|locinfo.*segfault" | tail -10', "extractor/locinfo crash (最近1小时)")

# ===== 8. httpd error log 查找 =====
run('find /var/log -name "error_log" -o -name "error.log" 2>/dev/null | head -5', "查找 error log 文件")
run('httpd -v 2>/dev/null', "httpd 版本")
run('cat /etc/httpd/conf/httpd.conf 2>/dev/null | grep -i "ErrorLog\\|error_log" | head -5', "httpd ErrorLog 配置")

# ===== 9. /Agent/flow/ 数据文件 =====
run('ls -lt /Agent/flow/1/ 2>/dev/null | head -10 || echo "(/Agent/flow/1/ 不存在)"', "flow 数据文件 (/Agent/flow/1/)")

# ===== 10. indexer.log =====
run('tail -20 /data/log/indexer.log 2>/dev/null || echo "(indexer.log 不存在)"', "indexer.log 最近20行")

c.close()
print("\n检查完成!")
