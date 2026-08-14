#!/bin/bash
# ============================================================
# 天鯨威胁情报服务器 (ti_server) 一键部署脚本（Linux）
# 用法: ./install.sh [管理端口] [查询端口]
#       TI_DB_HOST / TI_DB_USER / TI_DB_PASS / TI_DB_NAME 环境变量指定 MySQL 连接
# 功能: 初始化数据库 + 安装 systemd 自启动服务（双端口）
# ============================================================
set -e

MANAGE_PORT="${1:-8090}"
QUERY_PORT="${2:-8091}"
DIR="$(cd "$(dirname "$0")" && pwd)"

DB_HOST="${TI_DB_HOST:-127.0.0.1}"
DB_USER="${TI_DB_USER:-root}"
DB_PASS="${TI_DB_PASS:-}"
DB_NAME="${TI_DB_NAME:-ti_server}"

if [ -z "$DB_PASS" ]; then
    echo "[ERROR] 请设置 TI_DB_PASS 环境变量指定 MySQL 密码"
    echo "       例: TI_DB_PASS=xxx ./install.sh"
    exit 1
fi

echo "==> [ti_server] 目录: $DIR  管理端口: $MANAGE_PORT  查询端口: $QUERY_PORT"
echo "==> MySQL: $DB_USER@$DB_HOST/$DB_NAME"

# 1. 检查 python3 与 pymysql
if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] 未找到 python3"
    exit 1
fi
if ! python3 -c "import pymysql" >/dev/null 2>&1; then
    echo "==> 安装 pymysql..."
    yum install -y python3-PyMySQL >/dev/null 2>&1 || pip3 install pymysql >/dev/null 2>&1 || {
        echo "[ERROR] pymysql 安装失败，请手动安装"; exit 1; }
fi
echo "==> python3: $(python3 --version)"

# 2. 初始化数据库
echo "==> 初始化数据库..."
TI_DB_HOST="$DB_HOST" TI_DB_USER="$DB_USER" TI_DB_PASS="$DB_PASS" TI_DB_NAME="$DB_NAME" \
    python3 "$DIR/server.py" --init

# 3. 写入数据库连接配置（systemd EnvironmentFile，权限 600）
ENV_FILE="$DIR/db.env"
cat > "$ENV_FILE" <<EOF
TI_DB_HOST=$DB_HOST
TI_DB_USER=$DB_USER
TI_DB_PASS=$DB_PASS
TI_DB_NAME=$DB_NAME
EOF
chmod 600 "$ENV_FILE"

# 4. 写入 systemd 服务
SVC="/etc/systemd/system/ti-server.service"
cat > "$SVC" <<EOF
[Unit]
Description=TianJing Threat Intelligence Server
After=network.target mysqld.service mariadb.service

[Service]
Type=simple
WorkingDirectory=$DIR
EnvironmentFile=$ENV_FILE
ExecStart=/usr/bin/python3 $DIR/server.py --manage-port $MANAGE_PORT --query-port $QUERY_PORT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 5. 启动服务
echo "==> 启动服务..."
systemctl daemon-reload
systemctl enable ti-server >/dev/null 2>&1 || true
systemctl restart ti-server

sleep 2
if systemctl is-active ti-server >/dev/null 2>&1; then
    echo ""
    echo "============================================================"
    echo " 天鯨威胁情报服务器部署完成"
    echo " 管理界面:  http://<本机IP>:$MANAGE_PORT/   (启用HTTPS后为 https)"
    echo " 查询端口:  http://<本机IP>:$QUERY_PORT/query"
    echo " 默认账号:  admin / admin（请登录后立即修改密码）"
    echo " 常用命令:  systemctl status ti-server"
    echo "            journalctl -u ti-server -f"
    echo "============================================================"
else
    echo "[ERROR] 服务启动失败，请查看日志: journalctl -u ti-server"
    exit 1
fi
