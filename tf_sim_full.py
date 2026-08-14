import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmd = r'''
# ========== 单会话全链路测试 ==========
echo "===== 1. 启动模拟威胁情报服务 ====="
fuser -k 18090/tcp 2>/dev/null; sleep 1
(setsid python3 /tmp/sim_ti_server.py >/tmp/sim_ti_server.log 2>&1 </dev/null &) >/dev/null 2>&1
sleep 2
echo -n "端口监听: "; ss -tlnp 2>/dev/null | grep -c 18090
echo -n "JWT正常key: "; curl -s -X POST "http://127.0.0.1:18090/apisix/plugin/jwt/sign?key=sim_key_2026" -d "key=sim_key_2026" --max-time 5
echo ""
echo -n "JWT错误key状态码: "; curl -s -X POST "http://127.0.0.1:18090/apisix/plugin/jwt/sign?key=wrong_key" -d "key=wrong_key" --max-time 5 -o /dev/null -w "%{http_code}"
echo ""

echo ""
echo "===== 2. 登录 ====="
COOKIE=/tmp/ly_cookie_sim.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30
echo ""

echo ""
echo "===== 3. 模拟前未配置状态 ====="
echo -n "threatconf get: "; curl -s "http://127.0.0.1/d/threatconf?op=get" -b $COOKIE --max-time 30
echo ""
echo -n "threatinfo: "; curl -s "http://127.0.0.1/d/threatinfo?ip=1.2.3.4" -b $COOKIE --max-time 30
echo ""

echo ""
echo "===== 4. 模拟 UI 保存（threatconf op=save） ====="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=sim_key_2026&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=18090" -b $COOKIE --max-time 30
echo ""

echo ""
echo "===== 5. 保存后 get 回显 ====="
curl -s "http://127.0.0.1/d/threatconf?op=get" -b $COOKIE --max-time 30
echo ""

echo ""
echo "===== 6. 测试按钮 op=test（期望 200 连通正常） ====="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE --max-time 30
echo ""

echo ""
echo "===== 7. 核心：threatinfo 走通模拟服务（期望返回模拟情报） ====="
curl -s "http://127.0.0.1/d/threatinfo?ip=1.2.3.4" -b $COOKIE --max-time 30
echo ""

echo ""
echo "===== 8. 错误 key 场景（改错后 test） ====="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=wrong_key&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=18090" -b $COOKIE --max-time 30 > /dev/null
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE --max-time 30
echo ""
echo -n "threatinfo(错误key): "; curl -s "http://127.0.0.1/d/threatinfo?ip=1.2.3.4" -b $COOKIE --max-time 30
echo ""

echo ""
echo "===== 9. 恢复正确配置再验证 + 清理 ====="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=sim_key_2026&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=18090" -b $COOKIE --max-time 30 > /dev/null
echo -n "threatinfo(8.8.8.8): "; curl -s "http://127.0.0.1/d/threatinfo?ip=8.8.8.8" -b $COOKIE --max-time 30
echo ""
fuser -k 18090/tcp 2>/dev/null
sleep 1
echo -n "模拟服务已停止(端口监听数): "; ss -tlnp 2>/dev/null | grep -c 18090
'''

stdin, stdout, stderr = client.exec_command(cmd, timeout=400)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(out)
if err:
    print(f"STDERR: {err[:2000]}")

client.close()