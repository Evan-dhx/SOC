# 流影 SOC 平台 — 遗留待办事项

> 生成时间：2026-08-13
> 远程主机：10.10.102.220 (root / PP@ssw0rd)
> 本次修复已完成并验证通过，以下为日后需人工处理的待办事项。

---

## 待办 1：配置 tisrs.conf 威胁情报 API（高优先级）

**现状**：tisrs.conf 已创建，但 KEY/HOST/PORT 均为空，威胁情报查询功能处于禁用状态。

**待办**：填入实际的威胁情报 API 地址和密钥，启用威胁情报查询。

**涉及文件**：
- 远程：`/Server/etc/tisrs.conf`
- 源码参考：`d:\QorderProject\SOC\ly_server\src\server\threatinfo.cpp`（第79-106行读取此配置）
- 源码参考：`d:\QorderProject\SOC\ly_server\src\server\define.h`（第22行定义路径常量 `TISRS_CONF`）

**操作方法**：
```
# SSH 登录后编辑
vi /Server/etc/tisrs.conf

# 填入实际值：
KEY=你的API密钥
HOST=威胁情报API地址
PORT=端口号
```

---

## 待办 2：EventDB 为空，indexer 未生成事件（中优先级）

**现状**：indexer 日志持续显示 "Generated 0 events"，所有流量处理未触发威胁检测规则。

**待办**：检查 indexer 的流量处理链路，确认是否有实际 NetFlow 数据流入、威胁检测规则是否生效。

**涉及文件**：
- 远程日志：`/data/log/indexer.log`
- 远程配置：`/Agent/data/indexer_feature`（端口扫描/服务扫描 pattern 配置）
- 远程配置：`/Agent/data/indexer_cache`（TopN 缓存配置）
- 源码参考：`d:\QorderProject\SOC\ly_analyser\src\agent\flow\service_filter.cpp`（第234-270行，加载 pattern）
- 源码参考：`d:\QorderProject\SOC\ly_analyser\src\agent\indexing\cache_generator.cpp`（第28-40行，加载缓存配置）
- 源码参考：`d:\QorderProject\SOC\ly_analyser\src\agent\define.h`（定义 AGENT_PAT_FILE、AGENT_CACHE_CONFIG_FILE 等路径常量）

**排查方向**：
1. 确认 nfcapd 正在接收 NetFlow 数据：`ls -la /Agent/flow/1/nfcapd.*`
2. 确认 indexer 进程正常运行：`ps aux | grep extractor`
3. 检查 indexer_feature 中的 pattern 阈值是否合理
4. 查看 indexer 详细日志中是否有 flow 处理记录

---

## 待办 3：CGI 程序重新编译的持久化（✅ 已完成）

**现状**：已从源码重新编译并部署全部 19 个程序（nfdump + config_pusher + gen_event + 15 个 CGI + sctl + evidence），全部验证通过 (19/19 OK)。protobuf 版本不匹配问题已解决。

**验证结果**（2026-08-13）：
- nfdump: Version 1.6.8p1，运行正常
- config_pusher: EXIT=0，crontab 每 5 分钟正常运行
- gen_event: 编译成功，部署正常
- auth/topn/mo/event/bwlist/feature/event_feature/locinfo/geoinfo/portinfo/ipinfo/config/threatinfo/threatinfopro/sctl/evidence: 全部 ldd 依赖正常，无 symbol lookup error

**日后注意**：如果更新系统库或重新部署，需重复此编译操作。编译方法见下方。

**涉及文件（远程源码路径）**：
- nfdump 源码：`/root/SOC/ly_analyser_src/nfdump/bin/`
- Server CGI 源码：`/root/SOC/ly_server_src/server/`
- Agent 源码：`/root/SOC/ly_analyser_src/agent/`
- 共享 protobuf 定义：`/root/SOC/ly_analyser_src/common/config.pb.cc`（使用 protobuf 3.19 风格 AddDescriptorsRunner）

**涉及文件（远程部署路径）**：

| 程序 | 部署路径 | 源码路径 |
|------|---------|---------|
| nfdump | `/Agent/bin/nfdump` | `/root/SOC/ly_analyser_src/nfdump/bin/` |
| config_pusher | `/Server/bin/config_pusher` | `/root/SOC/ly_server_src/server/` |
| gen_event | `/Server/bin/gen_event` | `/root/SOC/ly_server_src/server/` |
| auth | `/Server/www/d/auth` | `/root/SOC/ly_server_src/server/` |
| topn | `/Server/www/d/topn` | `/root/SOC/ly_server_src/server/` |
| mo | `/Server/www/d/mo` | `/root/SOC/ly_server_src/server/` |
| event | `/Server/www/d/event` | `/root/SOC/ly_server_src/server/` |
| bwlist | `/Server/www/d/bwlist` | `/root/SOC/ly_server_src/server/` |
| feature | `/Server/www/d/feature` | `/root/SOC/ly_server_src/server/` |
| event_feature | `/Server/www/d/event_feature` | `/root/SOC/ly_server_src/server/` |
| locinfo | `/Server/www/d/locinfo` | `/root/SOC/ly_server_src/server/` |
| geoinfo | `/Server/www/d/geoinfo` | `/root/SOC/ly_server_src/server/` |
| portinfo | `/Server/www/d/portinfo` | `/root/SOC/ly_server_src/server/` |
| ipinfo | `/Server/www/d/ipinfo` | `/root/SOC/ly_server_src/server/` |
| config | `/Server/www/d/config` | `/root/SOC/ly_server_src/server/` |
| threatinfo | `/Server/www/d/threatinfo` | `/root/SOC/ly_server_src/server/` |
| threatinfopro | `/Server/www/d/threatinfopro` | `/root/SOC/ly_server_src/server/` |

**重新编译命令**：
```bash
# nfdump
cd /root/SOC/ly_analyser_src/nfdump/bin
make clean && make nfdump
cp nfdump /Agent/bin/nfdump
chmod +x /Agent/bin/nfdump

# Server CGI 全部
cd /root/SOC/ly_server_src/server
make clean && make
cp auth topn mo event bwlist feature event_feature \
   locinfo geoinfo portinfo ipinfo config threatinfo threatinfopro \
   /Server/www/d/
cp config_pusher gen_event /Server/bin/
chmod +x /Server/www/d/* /Server/bin/config_pusher /Server/bin/gen_event
```

---

## 待办 4：httpd auth CGI 运行环境检查（✅ 已完成）

**现状**：auth CGI 运行环境完全正常。POST 登录成功，前端页面正常加载，POST API 查询正常返回数据。

**验证结果**（2026-08-13）：
- ✅ POST 登录：返回 `[{"code": 200}]` + SESSION_ID cookie
- ✅ 前端首页：HTTP 200，React 应用正常加载（标题"流影"）
- ✅ POST mo get：返回 5 条监控对象数据（Port 0, SSH, RDP, VNC 等）
- ✅ POST feature with params（devid=1&starttime=0&endtime=0&interval=3600）：HTTP 200
- ✅ POST geoinfo op=get：HTTP 200
- ✅ GET auth_status：返回 `[{"code": 200}]`
- ✅ httpd 配置正确：ScriptAlias /d/ → /Server/www/d/，RewriteRule 路由正常，LD_LIBRARY_PATH 设置正确
- ✅ 数据库连接正常：t_device (id=1, ip=127.0.0.1), t_agent (id=1, ip=127.0.0.1)

**已知非环境问题（不影响核心功能）**：
1. feature/event_feature GET 无参数返回 500：源码在参数不足时直接输出 `HTTP/1.1 400 Invalid Params` 而非有效 CGI 头，httpd 报 "malformed header"。前端使用时会附带正确参数（devid, starttime, endtime, interval），实际不会有问题。
2. ipinfo 返回 "open error!"：缺少 IP 数据文件 `/Server/data/ip_data`（CSV 格式），`/Server/data/` 目录不存在。详见待办 6。
3. mo/bwlist/internalip GET 返回 `{failed}`：这些是 POST API，GET 方式返回失败是正常设计行为。

**涉及文件**：
- 远程 CGI：`/Server/www/d/auth`
- 远程配置：`/etc/httpd/conf.d/ly_server.conf`（httpd CGI 配置）
- 远程日志：`/var/log/httpd/ly_error_log`
- 远程数据库配置：`/etc/my.cnf.d/gl.server.cnf`
- 源码参考：`d:\QorderProject\SOC\ly_server\src\server\auth.cpp`（main 函数第557行，API 路由器）

---

## 待办 6：部署 ipinfo IP 数据文件（中优先级）

**现状**：ipinfo CGI 运行时输出 "open error!"，因为缺少 IP 数据文件 `/Server/data/ip_data`（CSV 格式），且 `/Server/data/` 目录不存在。

**待办**：创建 `/Server/data/` 目录并部署 IP 地理位置数据文件 `ip_data`（CSV 格式）。

**涉及文件**：
- 远程缺失文件：`/Server/data/ip_data`（CSV 格式 IP 地理位置数据）
- 远程 CGI：`/Server/www/d/ipinfo`
- 源码参考：`d:\QorderProject\SOC\ly_server\src\server\ipinfo.cpp`（第17行 `const char data_file[] = SERVER_DATA_DIR "/ip_data"`，第33行 `fopen(data_file, "rb")`）
- 源码参考：`d:\QorderProject\SOC\ly_server\src\server\define.h`（`SERVER_DATA_DIR` 定义）

**操作方法**：
```bash
# SSH 登录后
mkdir -p /Server/data
# 部署 IP 地理位置数据文件（CSV 格式）
# 格式参考 ipinfo.cpp 源码中的 CSV 解析逻辑
vi /Server/data/ip_data
```

---

## 待办 5：crontab config_pusher 日志监控（低优先级）

**现状**：config_pusher 日志已清理，当前运行正常 (EXIT=0)。crontab 每 5 分钟运行一次。

**待办**：定期检查日志确保持续正常。

**涉及文件**：
- 远程日志：`/data/log/config_pusher.log`
- 远程 crontab：`crontab -l`（config_pusher 每 5 分钟运行）

**监控命令**：
```bash
tail -20 /data/log/config_pusher.log
# 如果出现 "symbol lookup error" 或 "command not found" 则需要重新编译
```

---

## 本次修复涉及的本地脚本文件

| 脚本 | 用途 |
|------|------|
| `d:\QorderProject\SOC\fix_nfdump_final.py` | 从源码重新编译 nfdump 并部署 |
| `d:\QorderProject\SOC\fix_pusher_tisrs.py` | 重新编译 config_pusher + 修复 tisrs.conf |
| `d:\QorderProject\SOC\fix_cgi_verify.py` | 重新编译全部 Server CGI + 验证 |
| `d:\QorderProject\SOC\verify_all_final.py` | 最终全面验证脚本 |
| `d:\QorderProject\SOC\fix_remaining_all.py` | 综合诊断脚本 |
| `d:\QorderProject\SOC\fix_nfdump_rebuild.py` | nfdump 源码检查脚本 |

---

## 本次修复涉及的远程配置文件

| 文件 | 操作 |
|------|------|
| `/Agent/data/indexer_feature` | 新建（CSV 格式 pattern 配置） |
| `/Agent/data/indexer_cache` | 新建（INI 格式 TopN 缓存配置） |
| `/Agent/data/ti_dns` | 部署（威胁情报 DNS 数据） |
| `/Agent/data/sus_threat` | 部署（可疑威胁数据） |
| `/Agent/data/mining_domain` | 部署（挖矿域名数据） |
| `/Agent/data/mining_ip` | 部署（挖矿 IP 数据） |
| `/Server/etc/tisrs.conf` | 新建（威胁情报配置，待填入实际值） |
| `/etc/my.cnf.d/gl.server.cnf` | 已有（数据库连接配置 user=root/password=password123） |
| `/etc/httpd/logs/` | 权限修复（chmod 755） |
| `/data/log/config_pusher.log` | 日志清理 |
