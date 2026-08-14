# -*- coding: utf-8 -*-
"""部署 ti_server「允许更新截止日期」改造并端到端验证。
覆盖: API 日期格式校验 / export 截止限制 / 旧数据兼容 / 列表返回。
"""
import paramiko
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HOST = "10.10.102.220"
USER = "root"
PWD = "PP@ssw0rd"
LOCAL = r"d:\QorderProject\SOC\ti_server"
REMOTE = "/opt/ti_server"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PWD, timeout=30)


def put_dir(sftp, local, remote):
    if not os.path.isdir(local):
        sftp.put(local, remote)
        return
    try:
        sftp.stat(remote)
    except FileNotFoundError:
        sftp.mkdir(remote)
    for name in os.listdir(local):
        if name.startswith("__pycache__") or name.endswith(".pyc"):
            continue
        put_dir(sftp, os.path.join(local, name), f"{remote}/{name}")


sftp = client.open_sftp()
put_dir(sftp, LOCAL, REMOTE)
sftp.close()
print("== 已上传 ti_server 到", REMOTE)

cmds = [
    ("重启服务", r"""
cd /opt/ti_server
systemctl restart ti-server
sleep 3
systemctl is-active ti-server
echo "--- t_client 现状 ---"
mysql -uroot -ppassword123 ti_server -e "SELECT id,name,update_window,enabled FROM t_client;" 2>/dev/null
"""),
    ("API 验证", r'''
cd /opt/ti_server
B=https://127.0.0.1:8090
TOKEN=$(curl -sk -X POST $B/api/login -H 'Content-Type: application/json' -d '{"user":"admin","pass":"admin"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
echo "TOKEN=${TOKEN:0:12}..."

echo "=== 1. 新增客户端 截止日期=2028-10-10（应 200） ==="
curl -sk -X POST $B/api/clients -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"验收-截止日期演示","order_no":"TI-DEMO-2026","contact":"改造验收","allowed_ips":"127.0.0.1","update_window":"2028-10-10","enabled":1}'
echo ""
echo "=== 2. 非法日期 2028-13-40（应 400 拒绝） ==="
curl -sk -X POST $B/api/clients -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"非法日期","update_window":"2028-13-40"}' -w " [HTTP %{http_code}]"
echo ""
echo "=== 3. 旧格式 00:00-23:59 提交（应 400 拒绝，提示新格式） ==="
curl -sk -X POST $B/api/clients -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"旧格式","update_window":"00:00-23:59"}' -w " [HTTP %{http_code}]"
echo ""
echo "=== 4. 定位演示客户端并取 token ==="
DEMO=$(mysql -uroot -ppassword123 ti_server -N -e "SELECT id,cli_token FROM t_client WHERE name='验收-截止日期演示' ORDER BY id DESC LIMIT 1;" 2>/dev/null)
DEMO_ID=$(echo $DEMO | awk '{print $1}')
DEMO_TK=$(echo $DEMO | awk '{print $2}')
echo "demo id=$DEMO_ID token=${DEMO_TK:0:8}..."
echo "--- 4a. 截止 2028-10-10 导出（应 200） ---"
curl -sk "http://127.0.0.1:8091/export?token=$DEMO_TK" | head -c 120; echo ""
echo "--- 4b. 改成已过期 2020-01-01 再导出（应 403 拒绝） ---"
curl -sk -X PUT $B/api/clients/$DEMO_ID -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"验收-截止日期演示","order_no":"TI-DEMO-2026","contact":"改造验收","allowed_ips":"127.0.0.1","update_window":"2020-01-01","enabled":1}' > /dev/null
curl -sk "http://127.0.0.1:8091/export?token=$DEMO_TK" -w " [HTTP %{http_code}]"; echo ""
echo "--- 4c. 改为今天 2026-08-14 再导出（应 200，当天含在内） ---"
curl -sk -X PUT $B/api/clients/$DEMO_ID -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"验收-截止日期演示","order_no":"TI-DEMO-2026","contact":"改造验收","allowed_ips":"127.0.0.1","update_window":"2026-08-14","enabled":1}' > /dev/null
curl -sk "http://127.0.0.1:8091/export?token=$DEMO_TK" | head -c 120; echo ""
echo "=== 5. 旧数据兼容：SQL 写入旧格式 00:00-23:59 再导出（应 200 视为不限） ==="
mysql -uroot -ppassword123 ti_server -e "UPDATE t_client SET update_window='00:00-23:59' WHERE id=$DEMO_ID;" 2>/dev/null
curl -sk "http://127.0.0.1:8091/export?token=$DEMO_TK" | head -c 120; echo ""
echo "--- 清理演示客户端（同时覆盖兼容性展示的旧格式数据） ---"
curl -sk -X DELETE $B/api/clients/$DEMO_ID -H "Authorization: Bearer $TOKEN" -w " [HTTP %{http_code}]"
echo ""
echo "=== 6. 最终列表 ==="
curl -sk $B/api/clients -H "Authorization: Bearer $TOKEN" | python3 -c 'import sys,json;d=json.load(sys.stdin);print("count:",len(d["data"]));[print(c["id"],c["name"],"| window=",repr(c["update_window"]),"| enabled=",c["enabled"]) for c in d["data"]]'
'''),
]

for label, cmd in cmds:
    print(f"\n========== [{label}] ==========")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()
print("\n== 部署验证完成 ==")
