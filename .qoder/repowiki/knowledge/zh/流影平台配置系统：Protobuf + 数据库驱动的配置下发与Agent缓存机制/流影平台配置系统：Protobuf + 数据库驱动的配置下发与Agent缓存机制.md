---
kind: configuration_system
name: 流影平台配置系统：Protobuf + 数据库驱动的配置下发与Agent缓存机制
category: configuration_system
scope:
    - '**'
source_files:
    - ly_analyser/src/common/config.h
    - ly_analyser/src/agent/config/cached_config.h
    - ly_analyser/src/agent/config/local_disk_config.h
    - ly_analyser/src/agent/config/redis_config.h
    - ly_server/src/lib/config_class.h
    - ly_server/src/lib/config_agent.h
    - ly_server/src/server/config.cpp
    - ly_server/src/server/config_pusher.cpp
---

## 1. 使用的系统与框架

- **协议定义**：使用 Google Protobuf（`config.proto`、`event.proto`、`policy.proto` 等）作为跨进程/跨模块的共享配置契约，所有组件通过 `.proto` 文件生成 C++ 代码访问配置结构。
- **持久化存储**：配置数据统一存储在 MySQL（通过 `cppdb` 连接），包括设备、Agent、策略、黑白名单、事件阈值等；同时存在 `t_config` 键值表存放全局参数（如 `controller_host`、`controller_port`）。
- **运行时分发**：通过独立的 `config_pusher` 进程从数据库组装完整的 `Config` protobuf 消息，再推送给各 Agent。
- **Agent 侧缓存**：Agent 端实现 `CachedConfig` 抽象接口，支持两种后端：本地磁盘文件（`LocalDiskConfig`）和 Redis（`RedisConfig`），用于热更新与高性能读取。
- **动态加载插件**：`ly_server/src/server/config.cpp` 是 CGI 入口，根据 HTTP 请求中的 `type` 参数通过 `dlopen/dlsym` 动态加载 `lib/config_<type>.so` 插件（导出 `CreateConfigInstance` / `FreeConfigInstance`），实现对不同配置类型的扩展。

## 2. 关键文件与包

- `ly_analyser/src/common/config.h`：`ConfigReader` / `ConfigWriter`，负责将 protobuf 文本格式读写到本地配置文件。
- `ly_analyser/src/agent/config/cached_config.h`：`CachedConfig` 抽象基类，定义 `Update()` / `config()` / `FetchMOFilters()` 接口。
- `ly_analyser/src/agent/config/local_disk_config.{h,cpp}`：基于本地文件的 `CachedConfig` 实现，启动时由 `ConfigReader` 加载。
- `ly_analyser/src/agent/config/redis_config.{h,cpp}`：基于 Redis 的 `CachedConfig` 实现，维护 `redisContext` 并批量执行命令。
- `ly_server/src/lib/config_class.h`：服务端 `config::Config` 基类，提供 CIDR/端口校验、SQL session 持有、以及 `extern "C" CreateConfigInstance/FreeConfigInstance` 插件接口约定。
- `ly_server/src/lib/config_agent.{h,cpp}`：具体配置类型处理器，继承 `config::Config`，实现 `ParseReq` / `ValidateRequest` / `Add/Del/Mod/Get` 等 CRUD。
- `ly_server/src/server/config.cpp`：CGI 主程序，检测 `REMOTE_ADDR` 环境变量判断是否 HTTP 模式，动态加载对应 `.so` 处理请求，并在增删改后调用 `/Server/bin/config_pusher` 触发推送。
- `ly_server/src/server/config_pusher.cpp`：核心配置聚合器，从 `t_device`、`t_agent`、`t_mo`、`t_event_config_*`、`t_blacklist`、`t_whitelist`、`t_internal_ip_list`、`t_config` 等表组装出每个 Agent 的完整 `Config` protobuf 消息，并按设备维度拆分推送。
- `ly_server/src/lib/config_*.proto`：各配置子域（`config_agent`、`config_bwlist`、`config_event`、`config_user` 等）的 protobuf 定义。

## 3. 架构与设计决策

- **集中式配置源**：所有可运行配置最终来源于 MySQL。`config_pusher` 是唯一把数据库内容转换为 Agent 可消费 protobuf 的通道。
- **按 Agent 分片**：`push()` 中构建 `map<u32, Config>`，以 `agentid` 为键，为每个 Agent 生成独立配置对象，并通过 `dev_to_agent` 映射将设备级配置归属到对应 Agent。
- **通用策略 + 设备专属策略**：对 MO、Event、PolicyIndex 等，先写入 `common_cfg`，再合并到各 Agent 的 `cfg[agentid]`，实现“全局默认 + 设备覆盖”的分层。
- **Agent 侧双后端缓存**：`CachedConfig` 抽象屏蔽了数据来源差异——`LocalDiskConfig` 适合单机部署或离线场景，`RedisConfig` 适合集群热更新；两者都暴露相同的 `Update(config)` 接口供上层刷新。
- **插件化配置处理器**：服务端通过 `dlopen("config_<type>.so")` 按需加载配置类型实现，新增配置类型只需编译新 `.so` 并放置到 `SERVER_LIB_DIR`，无需重启 CGI 主程序。
- **HTTP 与 CLI 双入口**：`config::Config` 同时实现 `Process(cgicc::Cgicc&)`（HTTP CGI）和 `Process(int argc, char** argv)`（命令行），便于调试与自动化。

## 4. 约定与约束

- **配置结构契约**：所有组件必须遵循 `config.proto` 定义的 `Config` 消息结构，新增字段需同步更新 `config_pusher` 的赋值逻辑。
- **插件 ABI 约定**：每个 `config_<type>.so` 必须导出 `extern "C" config::Config* CreateConfigInstance(const std::string&, cppdb::session*)` 和 `void FreeConfigInstance(config::Config*)`，否则 CGI 会 `dlerror` 退出。
- **CIDR 与端口校验**：通过 `config::Config::is_valid_cidr`（正则匹配）和 `is_valid_port`（范围 0–65535）强制输入合法性，子类应复用这些工具方法。
- **设备禁用过滤**：`config_pusher` 在读取 `t_device` 时跳过 `disabled == 'Y'` 的设备，确保被禁用的设备不会收到配置推送。
- **状态过滤**：事件相关配置仅加载 `status = 'ON'` 的记录（查询中均带 `AND t3.status='ON'`），关闭的策略不会被下发。
- **时间窗口解析**：`weekday`、`stime`、`etime` 采用 CSV 风格字符串（逗号分隔星期、冒号分隔时分秒），由 `set_weekday` / `set_stime` / `set_etime` 统一解析。
- **缓存失效标记**：`RedisConfig` 与 `LocalDiskConfig` 的 `config()` / `mutable_config()` 标注 `Do not use method. TODO: fix it`，表明当前设计下读路径应通过 `FetchMOFilters` 等专用接口而非直接取内部 `config_` 成员。
- **推送触发时机**：任何 `op==add|mod|del` 的配置变更都会通过 `system("/Server/bin/config_pusher")` 拉起一次全量重推，保证 Agent 与数据库最终一致。
- **前端文档站点配置**：`ly_docs/config/_default/`、`development/`、`production/` 下的 `config.toml`、`params.toml`、`security.toml` 等 Hugo 配置文件用于文档站点的多环境构建，与业务配置系统相互独立。

总体而言，该仓库的配置系统围绕 **Protobuf 契约 + MySQL 持久化 + config_pusher 聚合分发 + Agent 端 CachedConfig 缓存** 这一主线展开，通过动态加载插件扩展新的配置类型，形成一套面向 NetFlow 分析引擎的可热更新配置体系。