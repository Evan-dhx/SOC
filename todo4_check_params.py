import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

def run(cmd, label=None, timeout=60):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if label:
        print(f"[{label}]")
    if out.strip():
        print(out.strip()[:5000])
    if err.strip():
        print(f"  STDERR: {err.strip()[:3000]}")
    return out, err

print("=" * 70)
print("检查 ipinfo data_file 和 feature 参数验证")
print("=" * 70)

# ---- 1. 检查 ipinfo 的 data_file 定义 ----
print("\n--- [1] ipinfo data_file 定义 ---")
run('sed -n "1,50p" /root/SOC/ly_server_src/server/ipinfo.cpp 2>/dev/null', "ipinfo 源码前50行")

# ---- 2. 检查 ipinfo main 函数 ----
print("\n--- [2] ipinfo main 函数 ---")
run('sed -n "100,180p" /root/SOC/ly_server_src/server/ipinfo.cpp 2>/dev/null', "ipinfo main 函数")

# ---- 3. 检查 define.h 中 IP 数据文件路径 ----
print("\n--- [3] define.h 中 IP 相关路径 ---")
run('grep -n "IP\\|ip\\|data\\|DATA\\|DB\\|GEO\\|geo" /root/SOC/ly_server_src/server/define.h 2>/dev/null | head -20', "define.h IP 路径")

# ---- 4. 检查 feature main 函数参数验证 ----
print("\n--- [4] feature main 函数 ---")
run('sed -n "496,560p" /root/SOC/ly_server_src/server/feature.cpp 2>/dev/null', "feature main 函数")

# ---- 5. 检查 feature_req.h 了解必需参数 ----
print("\n--- [5] feature_req.h 参数定义 ---")
run('cat /root/SOC/ly_analyser_src/common/feature_req.h 2>/dev/null | head -60', "feature_req.h")

# ---- 6. 检查 ipinfo 需要的数据文件是否存在 ----
print("\n--- [6] 检查 IP 数据文件 ---")
run('ls -la /Server/data/ 2>/dev/null || echo "无 /Server/data/"', "/Server/data/ 目录")
run('ls -la /Agent/data/ip* 2>/dev/null || echo "无 /Agent/data/ip*"', "/Agent/data/ip*")
run('find /Server -name "*.dat" -o -name "*.db" -o -name "ip*" 2>/dev/null | head -20', "Server 下的数据文件")
run('find /Agent -name "*.dat" -o -name "*.db" -o -name "ip*" 2>/dev/null | head -20', "Agent 下的数据文件")

# ---- 7. 用正确参数测试 feature ----
print("\n--- [7] 用正确参数测试 feature ---")
run('curl -s -c /tmp/cookies.txt -X POST -d "auth_user=admin&auth_pass=admin&auth_target=login" http://127.0.0.1/d/auth 2>&1', "登录")
# feature 需要 devid, starttime, endtime, interval
run('curl -s -b /tmp/cookies.txt -w "\\nHTTP_CODE=%{http_code}" -X POST -d "auth_target=feature&op=get&devid=1&starttime=0&endtime=0&interval=3600" http://127.0.0.1/d/auth 2>&1 | head -10', "POST feature with params")

# ---- 8. 检查 t_device 表是否有设备 ----
print("\n--- [8] 检查 t_device 表 ---")
run('mysql -u root -ppassword123 -e "SELECT id,ip,agentid,disabled FROM t_device LIMIT 5;" server 2>/dev/null', "t_device 表")
run('mysql -u root -ppassword123 -e "SELECT id,ip,disabled FROM t_agent LIMIT 5;" server 2>/dev/null', "t_agent 表")

# ---- 9. 检查 httpd 配置中 feature 是否有特殊处理 ----
print("\n--- [9] httpd 配置 ---")
run('cat /etc/httpd/conf.d/ly_server.conf 2>/dev/null', "完整 httpd 配置")

c.close()
print("\n" + "=" * 70)
print("检查完成!")
print("=" * 70)
