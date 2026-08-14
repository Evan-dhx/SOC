---
kind: logging_system
name: 基于 syslog 与 DEBUG 开关的轻量级日志系统
category: logging_system
scope:
    - '**'
source_files:
    - ly_analyser/src/common/log.h
    - ly_analyser/src/common/log.cpp
    - ly_server/src/common/log.h
    - ly_server/src/common/log.cpp
    - ly_server/src/server/syslog_sender.h
    - ly_server/src/server/syslog_sender.cpp
    - ly_server/src/server/gen_event.cpp
---

## 1. 使用的系统与框架

流影（Flow Shadow）平台在 C++ 后端（ly_analyser、ly_server）采用**极简自定义日志方案**，未引入第三方日志库：
- 核心输出通过 POSIX `syslog` 接口（`vsyslog`）写入系统日志。
- 调试信息通过环境变量 `DEBUG` 控制开关，配合 `is_debugging(__FILE__)` 实现按源文件粒度启用。
- 事件告警通过自实现的 UDP/TCP `syslog_sender` 模块以 RFC 3164 风格 `<pri>timestamp host FsEvent: ...` 格式外发至远端 syslog 服务器。

前端 ly_vis 为 React/Node 工程，不涉及 C/C++ 日志体系；文档站点 ly_docs 为 Hugo 静态站点，无运行时日志需求。因此本仓库的“日志系统”实质集中在两个 C++ 子工程的 `src/common/log.*` 与 `ly_server/src/server/syslog_sender.*`。

## 2. 关键文件

- `ly_analyser/src/common/log.h`：定义 `log_err` / `log_warning` / `log_info` 三个 inline 函数，均调用 `vsyslog(LOG_ERR|LOG_WARNING|LOG_INFO, fmt, args)`；定义 `is_debugging(const char* source_file)` 与宏 `#define DEBUG is_debugging(__FILE__)`。
- `ly_analyser/src/common/log.cpp`：仅包含头文件，无额外实现。
- `ly_server/src/common/log.h` / `log.cpp`：与 analyser 完全相同的副本，保证双进程共用同一日志 API。
- `ly_server/src/server/syslog_sender.h`：声明 `send_event_syslog_process(u32 level_id, const string& event_str)`。
- `ly_server/src/server/syslog_sender.cpp`：解析配置文件 `SYSLOGSENDER_CONF`，将事件以 `<facility.level>` 优先级 + 时间戳 + 主机名 + `FsEvent:` 前缀的字符串经 UDP(`@`) 或 TCP(`@@`) 发送至远端 syslog 服务器。

## 3. 架构与约定

### 3.1 日志级别
- 固定三级：`LOG_ERR`、`LOG_WARNING`、`LOG_INFO`，分别对应 `log_err`、`log_warning`、`log_info`。
- 没有 `LOG_DEBUG` 级别的 syslog 输出；调试信息走 `DEBUG` 宏分支，由调用方自行决定是否打印。

### 3.2 调试开关策略
- 通过环境变量 `DEBUG` 控制：当值为 `ALL` 时所有源文件开启调试；否则需匹配当前 `__FILE__` 路径片段才启用。
- 典型用法：`if (DEBUG && log_count++ < N) { ... }`，用于限制高频调试输出次数（如 `mdb.cpp` 中 `log_count < 50`、`mo_filter.cpp` 中 `MAX_LOG_FLOW=10` 限流）。

### 3.3 结构化字段与消息格式
- 应用层日志（`log_*`）使用 printf 风格的格式化字符串，不强制结构化字段。
- 外发事件（syslog sender）采用半结构化格式：`<facility.level> Mmm dd hh:mm:ss hostname FsEvent: <event_json_or_text>`，其中 facility/level 来自配置映射表（`Level`、`Facility` 两个 map），支持 `EXTRA_HIGH/HIGH/MIDDLE/LOW/EXTRA_LOW` 五级及 `KERN/USER/.../LOCAL7` 等 facility。

### 3.4 远端 syslog 路由
- 配置文件 `SYSLOGSENDER_CONF` 每行形如 `*.level @ip:port` 或 `*.level @@ip:port`，用正则 `^(.*)\.(.*)\s+(@{1,2})((IP))(:(PORT))?$` 解析。
- 事件生成处（如 `gen_event.cpp`）调用 `send_event_syslog_process(level_id, event_str)`，内部根据配置的最低级别阈值过滤后发送。

## 4. 约定与约束

- **统一入口**：所有 C++ 模块通过 `#include "../common/log.h"`（或相对路径等价形式）使用 `log_err/warning/info`，禁止直接调用 `syslog()` 或 `fprintf(stderr, ...)`。
- **调试输出必须包裹 `DEBUG`**：仓库中所有调试日志均以 `if (DEBUG && ...)` 形式出现，避免生产环境产生无用开销。
- **高频日志必须限流**：在 `mdb.cpp`、`mo_filter.cpp` 等热点路径中，通过计数器（`log_count`、`log_matched`、`log_unmatched`）限制最大输出条数，防止日志风暴。
- **事件外发遵循配置驱动**：`syslog_sender` 每次发送都重新读取并解析 `SYSLOGSENDER_CONF`，不支持热更新；若文件不可读则静默返回。
- **协议约定**：外发消息严格遵循 `RFC 3164` 风格 PRI + 时间 + 主机 + `FsEvent:` 前缀，便于下游 SIEM/Syslog 聚合解析。
- **跨进程一致性**：ly_analyser 与 ly_server 各自维护一份完全相同的 `log.h`，确保双组件行为一致，不存在共享库形式的集中式 logger。

## 5. 适用性说明

该仓库存在明确的日志子系统（C++ 后端），但规模较小、无结构化日志框架、无集中式日志采集器集成，属于“手写 syslog 封装 + 环境变量调试开关”的轻量实现。