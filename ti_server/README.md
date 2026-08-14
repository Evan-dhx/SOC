# 天鯨威胁情报服务器（ti_server）v2

独立的威胁情报数据服务端，可部署到任意 Linux 主机，与流影/天鯨 SOC 平台
`threatinfo` / `threatinfopro` 接口协议兼容，作为其威胁情报数据后端。

## 特性（v2）

- **数据库：MySQL/MariaDB**（pymysql），使用独立数据库实例（默认 `ti_server`），与 SOC 平台完全隔离
- **双端口隔离**：
  - **管理端口**（默认 8090）：Web 管理界面 + 管理 API（登录、情报 CRUD、配置、证书管理）
  - **查询端口**（默认 8091）：对外情报查询协议（JWT 签发 + 情报查询），仅暴露查询能力
- **HTTPS（管理界面）**：支持上传 **PFX（PKCS#12）证书** + 密码，一键启用 HTTPS 访问管理界面；查询端口保持 HTTP（内网对接场景）
- 独立 Web 管理界面：登录认证 + 仪表盘 + 情报管理 + **情报源管理** + 系统配置 + HTTPS 证书管理（深色科技风）
- 多类型威胁情报：IP / 域名 / URL / 文件哈希，含威胁类型、评分、标签、来源、置信度、过期时间
- **开源情报源对接**：支持多情报源（ThreatFox / 通用 CSV），后台定时自动拉取入库，按源配置保留天数自动清理旧数据
- 兼容流影协议：
  - JWT 签发：`POST /apisix/plugin/jwt/sign?key=服务KEY`，**响应体即 token（纯文本）**——与流影 threatinfo 客户端行为一致
  - 情报查询：`GET|POST /query?ip=1.2.3.4&jwt=令牌`；根路径 `GET /`（带 jwt）与 `POST /` 亦兼容
- 安全：管理员密码加盐哈希、会话令牌过期、查询令牌 HMAC-SHA256 签名 + 过期校验、私钥文件权限 600

## 目录结构

```
ti_server/
├── server.py           # 主程序（双端口 HTTP + MySQL + JWT + HTTPS 证书管理）
├── static/
│   └── index.html      # Web 管理界面（单文件，无需构建）
├── install.sh          # Linux 一键部署脚本（初始化 + systemd 自启动）
├── db.env              # 数据库连接配置（install.sh 生成，权限 600）
├── certs/              # 上传的 PFX 证书与转换产物（运行时生成）
└── README.md           # 本文档
```

## 部署（Linux，需要 MySQL/MariaDB）

```bash
# 1. 安装 pymysql（install.sh 会自动尝试安装）
yum install -y python3-PyMySQL

# 2. 一键部署（管理端口 8090 / 查询端口 8091）
TI_DB_PASS=<MySQL密码> ./install.sh            # 使用默认端口
TI_DB_PASS=<MySQL密码> ./install.sh 8443 8091  # 自定义端口

# 手动方式
TI_DB_PASS=<MySQL密码> python3 server.py --init
TI_DB_PASS=<MySQL密码> python3 server.py --manage-port 8090 --query-port 8091
```

环境变量：`TI_DB_HOST`（默认 127.0.0.1）/ `TI_DB_USER`（默认 root）/ `TI_DB_PASS`（必填）/ `TI_DB_NAME`（默认 ti_server）。
首次部署自动创建数据库与表，默认管理员 **admin / admin**（请立即修改密码）。

## 使用

1. 浏览器访问 `http://<服务器IP>:8090/`（启用 HTTPS 后为 `https://...`）
2. 页签功能：
   - **仪表盘**：类型统计、流影对接说明
   - **客户端管理**：多客户端（客户名称/单号/联系人、Key/Token 管理、启用禁用、允许更新截止日期、来源 IP 白名单、更新记录）
   - **情报管理**：增删改查、类型/威胁/关键字筛选、批量导入、导出 JSON
   - **情报源管理**：对接开源情报源，配置拉取周期自动入库（详见下文）
   - **系统配置**：JWT 密钥/有效期、查询路径、**HTTPS 证书管理**（上传 PFX + 密码 → 启用/停用）、修改密码
3. HTTPS 启用流程：系统配置 → HTTPS 证书管理 → 选择 .pfx 文件 + 输入密码 → 上传证书 → 启用 HTTPS → **重启服务生效**（`systemctl restart ti-server`）

## 情报源管理

「情报源管理」页签支持对接多个开源情报源，启用后由后台调度线程按设定周期自动拉取入库：

| 字段 | 说明 |
|---|---|
| 名称 / 类型 | 情报源名称；类型支持 **ThreatFox / URLhaus / Feodo Tracker / IP 列表 / 通用 CSV** |
| 拉取地址 | 留空使用所选类型默认地址；IP 列表与通用 CSV 必填 |
| API Key | 可选，需认证的源填入后以 `Authorization: Bearer <key>` 请求 |
| 拉取周期 | 分钟，最小 10；到期后调度线程自动拉取 |
| 保留天数 | 0=永久保留；>0 时拉取时自动清理该源超过保留天数的旧条目并设情报过期时间 |
| 字段映射 | IP 列表：配置默认威胁/评分/标签/置信度（`{"threat":"恶意IP","score":70,"tags":"blocklist"}`）；通用 CSV：JSON 指定列（`{"skip_header":true,"cols":{"ioc":0,"type":1,"threat":2,"tags":3,"confidence":4,"score":5}}`），列从 0 开始，-1 表示无，type 列留空自动识别 |

**内置情报源类型与默认地址**：

| 类型 | 数据内容 | 默认地址 | 是否需要 Key |
|---|---|---|---|
| ThreatFox | 恶意 IP/域名/URL/哈希（abuse.ch） | `https://threatfox.abuse.ch/export/csv/recent/` | 否 |
| URLhaus | 恶意 URL（abuse.ch） | `https://urlhaus.abuse.ch/downloads/csv_recent/` | 否 |
| Feodo Tracker | 僵尸网络 C2 IP（abuse.ch） | `https://feodotracker.abuse.ch/downloads/ipblocklist.csv` | 否 |
| IP 列表 | 纯文本每行一个 IP/CIDR，兼容 IPsum、Blocklist.de、ET compromised-ips 等 | 自定义 | 否 |
| 通用 CSV | 任意 CSV，列映射可配 | 自定义 | 可选 |

操作：**立即拉取**（手动触发一次）、**编辑**、**日志**（最近 20 次拉取记录）、**删除**（已入库情报保留）。
拉取到的 IOC 写入情报库，来源标记为情报源名称，可通过「情报管理」页签按来源筛选查看。

> 说明：abuse.ch 系列公开数据无需 API Key；IP 列表类型可通过字段映射为源配置默认威胁类型与评分（如 IPsum 12 万+ IP、Blocklist.de 2.7 万+ IP）。

## 客户端管理

每个接入方（流影平台/第三方系统）对应一个客户端，管理界面「客户端管理」页签：

| 字段 | 说明 |
|---|---|
| 客户名称 / 单号 / 联系人 | 客户信息与业务单号 |
| **Key** | JWT 签发凭据（流影 tisrs.conf 的 KEY 字段）；可重置（旧值立即失效） |
| **Token** | 长期令牌：直接查询 `/query?token=` 与全量更新 `/export?token=`；可重置 |
| 启用 / 禁用 | 禁用后该客户端 Key/Token 全部拒绝（`client disabled`） |
| 更新时间窗口 | `YYYY-MM-DD`，超过该截止日期后禁止 `/export` 全量更新，留空不限 |
| 允许来源 IP | 逗号分隔，支持 CIDR（如 `10.0.0.0/8, 10.10.2.5`），留空不限；Key 换 JWT、Token 查询/更新均校验来源 IP（`ip not allowed`） |
| 更新记录 | 自动记录每次全量更新（时间 + 来源 IP + 导出条数） |

> 兼容：首次部署自动创建「默认客户端」，其 Key 与旧 `service_key` 一致，存量对接不受影响。

## 与流影 SOC 平台对接

流影登录后顶部导航「情报」按钮（或编辑 `/Server/etc/tisrs.conf`）：

```
KEY=<ti_server 系统配置中的服务 KEY>
HOST=<ti_server 所在服务器 IP>
PORT=<查询端口，默认 8091>
URL=/query
```

保存后点「测试」验证连通；之后流影的威胁情报查询将从 ti_server 返回
`[{"ip":"...","threat":"...","score":..,"tag":"...","source":"...","confidence":..}]`，
未命中返回 `[]`（前端静默降级）。

## API 一览

### 查询端口（默认 8091，无需登录，需 Key/Token）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/apisix/plugin/jwt/sign?key=客户端Key` | 换取查询令牌（校验客户端启用 + 来源 IP；响应体即 token） |
| GET/POST | `/query?ip=&domain=&url=&hash=&jwt=` | 情报查询（根路径 `/` 兼容）；也可 `token=客户端Token` 直查 |
| GET/POST | `/export?token=客户端Token` | 全量情报导出（校验启用 + IP + 更新时间窗口，记录更新日志） |

### 管理端口（默认 8090）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/login` | 登录（Bearer token） |
| GET | `/api/stats` | 类型统计 |
| GET/POST | `/api/iocs` | 情报列表（分页/筛选）/ 新增 |
| PUT/DELETE | `/api/iocs/{id}` | 修改 / 删除 |
| POST | `/api/iocs/batch` | 批量导入 |
| GET/POST | `/api/sources` | 情报源列表 / 新增 |
| PUT/DELETE | `/api/sources/{id}` | 修改 / 删除 |
| POST | `/api/sources/{id}/pull` | 立即拉取该情报源（同步返回结果） |
| GET | `/api/sources/{id}/log` | 拉取日志 |
| GET/POST | `/api/clients` | 客户端列表 / 新增 |
| PUT/DELETE | `/api/clients/{id}` | 修改（含启用禁用、IP 白名单、时间窗口）/ 删除 |
| POST | `/api/clients/{id}/regen` | 重新生成 Key 或 Token（`{"kind":"key"|"token"}`） |
| GET | `/api/clients/{id}/log` | 更新记录 |
| GET/POST | `/api/config` | 读取 / 保存服务配置 |
| GET | `/api/cert` | 证书状态（无需登录） |
| POST | `/api/cert` | `action=upload/enable/disable`：上传 PFX / 启用 / 停用 HTTPS |
| POST | `/api/password` | 修改管理员密码 |

## 安全说明

- 默认管理员 `admin/admin`，**首次部署后务必修改**
- 管理端口建议仅内网可访问（或启用 HTTPS + 防火墙限制）；查询端口按需放行给流影服务器
- 服务 KEY 与 JWT 密钥初始化时自动随机生成，可在管理界面重新生成（旧 key 立即失效）
- PFX 密码经临时文件传给 openssl，不落命令行；私钥文件权限 600
