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
    if out.strip():
        print(out.strip()[-3000:] if len(out) > 3000 else out)
    else:
        print("(无输出)")
    if err.strip():
        print(f"STDERR: {err.strip()[-1000:]}")

# ===== 1. Systemd 服务状态 =====
print("\n" + "#"*60)
print("# 第一部分：Systemd 服务状态")
print("#"*60)

# 列出所有相关服务
run('systemctl list-units --type=service --all 2>/dev/null | grep -iE "httpd|nginx|nfcapd|lyprobe|tsensor|config_pusher|indexer|flow_capd" || echo "(无匹配服务)"', "相关服务列表")

# 逐个检查关键服务
for svc in ['httpd', 'nginx', 'mariadb', 'nfcapd', 'lyprobe', 'tsensor']:
    run(f'systemctl status {svc} 2>/dev/null | head -15 || echo "({svc} 服务不存在)"', f"{svc} 服务状态")

# ===== 2. Indexer (ly_analyser) 日志 =====
print("\n" + "#"*60)
print("# 第二部分：Indexer (ly_analyser) 日志")
print("#"*60)

run('journalctl -t indexer --no-pager -n 30 2>/dev/null', "Indexer 最近30条 syslog")
run('journalctl -t indexer --no-pager --since "10 min ago" 2>/dev/null | grep -i "error\\|fail\\|warning\\|denied\\|missing\\|not found\\|cannot" | tail -20', "Indexer 最近10分钟错误/警告")
run('journalctl -t indexer --no-pager --since "10 min ago" 2>/dev/null | grep -iv "devid:\\|Generated" | tail -20', "Indexer 最近10分钟非常规日志")

# ===== 3. Httpd / CGI (ly_server) 日志 =====
print("\n" + "#"*60)
print("# 第三部分：Httpd / CGI (ly_server) 日志")
print("#"*60)

run('tail -30 /var/log/httpd/error_log 2>/dev/null || tail -30 /var/log/apache2/error.log 2>/dev/null || echo "(httpd error log 不存在)"', "Httpd error log 最近30行")
run('tail -20 /var/log/httpd/access_log 2>/dev/null || tail -20 /var/log/apache2/access.log 2>/dev/null || echo "(httpd access log 不存在)"', "Httpd access log 最近20行")
run('grep -i "error\\|fail\\|500\\|502\\|503" /var/log/httpd/error_log 2>/dev/null | tail -20 || echo "(无错误或日志不存在)"', "Httpd error log 错误行")

# ===== 4. Nfcapd / Nfdump 日志 =====
print("\n" + "#"*60)
print("# 第四部分：Nfcapd / Nfdump 日志")
print("#"*60)

run('journalctl -t nfcapd --no-pager -n 20 2>/dev/null || echo "(无 nfcapd syslog)"', "nfcapd syslog")
run('journalctl -t nfcapd --no-pager --since "10 min ago" 2>/dev/null | grep -i "error\\|fail\\|warn" | tail -10 || echo "(无 nfcapd 错误)"', "nfcapd 错误")
run('journalctl -t flow_capd_launcher --no-pager -n 20 2>/dev/null || echo "(无 flow_capd_launcher syslog)"', "flow_capd_launcher syslog")
run('ls -lt /Agent/data/flows/ 2>/dev/null | head -10 || echo "(flows 目录不存在)"', "flow 数据文件")

# ===== 5. Config Pusher 日志 =====
print("\n" + "#"*60)
print("# 第五部分：Config Pusher 日志")
print("#"*60)

run('journalctl -t config_pusher --no-pager -n 20 2>/dev/null || echo "(无 config_pusher syslog)"', "config_pusher syslog")
run('journalctl -t config_pusher --no-pager --since "10 min ago" 2>/dev/null | grep -i "error\\|fail\\|warn" | tail -10 || echo "(无 config_pusher 错误)"', "config_pusher 错误")
run('crontab -l 2>/dev/null | grep -i "config_pusher\\|pusher" || echo "(crontab 中无 config_pusher)"', "config_pusher crontab")
run('cat /Server/etc/tisrs.conf 2>/dev/null || echo "(tisrs.conf 不存在)"', "tisrs.conf 配置")

# ===== 6. 前端 (ly_vis) 日志 =====
print("\n" + "#"*60)
print("# 第六部分：前端 (ly_vis) 日志")
print("#"*60)

run('tail -20 /var/log/nginx/error.log 2>/dev/null || echo "(nginx error log 不存在)"', "nginx error log")
run('tail -10 /var/log/nginx/access.log 2>/dev/null || echo "(nginx access log 不存在)"', "nginx access log")

# ===== 7. 数据库状态 =====
print("\n" + "#"*60)
print("# 第七部分：数据库状态")
print("#"*60)

run('mysql -u root -e "SHOW DATABASES;" 2>/dev/null || mysql -u root -p"PP@ssw0rd" -e "SHOW DATABASES;" 2>/dev/null || echo "(MySQL 连接失败)"', "数据库列表")
run('systemctl status mariadb 2>/dev/null | head -10 || systemctl status mysqld 2>/dev/null | head -10 || echo "(数据库服务不存在)"', "数据库服务状态")

# ===== 8. 系统 dmesg / messages =====
print("\n" + "#"*60)
print("# 第八部分：系统日志")
print("#"*60)

run('dmesg 2>/dev/null | grep -i "error\\|fail\\|segfault\\|oom\\|killed" | tail -10 || echo "(dmesg 无错误)"', "dmesg 错误")
run('journalctl --no-pager --since "10 min ago" -p err 2>/dev/null | tail -20 || echo "(无系统级错误)"', "系统级错误日志 (最近10分钟)")

# ===== 9. TSDB 文件 & eventdb =====
print("\n" + "#"*60)
print("# 第九部分：TSDB & EventDB")
print("#"*60)

run('ls -lt /Agent/data/db/20260813/ 2>/dev/null | head -20', "今日 TSDB 文件")
run('ls -lt /Agent/data/eventdb/ 2>/dev/null | head -10 || echo "(eventdb 目录为空或不存在)"', "EventDB 文件")
run('ls -la /Agent/data/config 2>/dev/null', "Agent config 文件")

# ===== 10. 进程状态 =====
print("\n" + "#"*60)
print("# 第十部分：进程状态")
print("#"*60)

run('ps aux | grep -E "indexer|nfcapd|httpd|nginx|config_pusher|flow_capd|tsensor" | grep -v grep', "关键进程列表")

c.close()
print("\n\n" + "="*60)
print("全模块日志检查完成!")
print("="*60)
