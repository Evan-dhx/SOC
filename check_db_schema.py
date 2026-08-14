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

# ===== 1. t_event_config_dnstunnel 表结构 =====
run('mysql -u root -e "USE server; DESCRIBE t_event_config_dnstunnel;" 2>&1', "server.t_event_config_dnstunnel 表结构")

# ===== 2. t_config 表确认 =====
run('mysql -u root -e "USE server; DESCRIBE t_config;" 2>&1', "server.t_config 表结构")

# ===== 3. config_pusher 最近的 syslog (15:10 之后) =====
run('journalctl -t config_pusher --no-pager --since "15:10" 2>/dev/null | tail -20', "config_pusher 15:10 后 syslog")

# ===== 4. config_pusher 最近运行状态 =====
run('ls -lt /data/log/config_pusher.log 2>/dev/null', "config_pusher.log 文件信息")
run('tail -5 /data/log/config_pusher.log 2>/dev/null', "config_pusher.log 最后5行")

# ===== 5. nfdump 依赖检查 =====
run('ldd /Agent/bin/nfdump 2>/dev/null | grep -i "protobuf\\|proto"', "nfdump protobuf 依赖")
run('ldd /Agent/bin/indexer 2>/dev/null | grep -i "protobuf\\|proto"', "indexer protobuf 依赖")
run('ls -la /Agent/lib/libproto* 2>/dev/null || ls -la /usr/local/lib/libproto* 2>/dev/null || echo "(无 protobuf 库)"', "protobuf 库文件")

# ===== 6. EventDB 确认 =====
run('ls -la /Agent/data/eventdb/ 2>/dev/null', "EventDB 目录")
run('ls -laR /Agent/data/eventdb/ 2>/dev/null', "EventDB 递归列表")

# ===== 7. httpd error_log 路径 =====
run('ls -la /etc/httpd/logs/error_log 2>/dev/null || ls -la /var/log/httpd/error_log 2>/dev/null || echo "(error_log 不存在)"', "httpd error_log 文件")

c.close()
print("\n检查完成!")
