---
kind: error_handling
name: C++ 进程级 try/catch + syslog 日志的错误处理模式
category: error_handling
scope:
    - '**'
source_files:
    - ly_analyser/src/common/log.h
    - ly_server/src/common/log.h
    - ly_analyser/src/agent/handlers/extractor.cpp
    - ly_analyser/src/agent/handlers/actl.cpp
    - ly_analyser/src/agent/handlers/config_updater.cpp
    - ly_analyser/src/agent/handlers/extract_event.cpp
    - ly_analyser/src/agent/handlers/extract_feature.cpp
    - ly_analyser/src/agent/handlers/extract_pcap.cpp
    - ly_analyser/src/agent/handlers/flow_scan.cpp
    - ly_analyser/src/common/mo_req.cpp
    - ly_analyser/src/common/file.cpp
    - ly_analyser/src/agent/flow/dns_filter.cpp
    - ly_analyser/src/agent/flow/ip_set_filter.cpp
    - ly_analyser/src/agent/flow/mining_filter.cpp
    - ly_analyser/src/agent/indexing/flow_indexer.cpp
    - ly_server/src/lib/config_agent.cpp
---

## 1. 整体方案

该仓库是一个 C/C++ 为主（ly_analyser、ly_server）+ Go/JS 前端（ly_vis、ly_docs）的网络安全分析平台。错误处理在 C++ 侧采用**进程级 try/catch + syslog 日志**的模式，没有统一的异常类型体系或错误码枚举；Go/JS 子工程在本分支中未发现显式的错误处理代码片段。

## 2. 关键文件与位置

- `ly_analyser/src/common/log.h`：定义 `log_err` / `log_warning` / `log_info` 三个内联函数，统一通过 `vsyslog(LOG_ERR|LOG_WARNING|LOG_INFO, ...)` 输出到系统日志；提供 `is_debugging()` 和 `DEBUG` 宏用于条件调试。
- `ly_server/src/common/log.h`：与 analyser 完全相同的日志头文件，两套后端共享同一套日志约定。
- `ly_analyser/src/agent/handlers/*.cpp`：所有 handler 入口（`extractor.cpp`、`actl.cpp`、`config_updater.cpp`、`extract_event.cpp`、`extract_feature.cpp`、`extract_pcap.cpp`、`flow_scan.cpp`）都在 `main()` 顶层用 `try { process(); } catch (std::exception const &e) { log_err(...); }` 包裹，捕获未处理的 `std::exception` 并记录后返回 0。
- `ly_analyser/src/agent/flow/*_filter.cpp`、`indexing/flow_indexer.cpp`、`common/{asset.cpp,file.cpp}`：对 I/O 等易失败操作使用 `catch (...)` 兜底，仅记录警告日志而不向上抛出。
- `ly_analyser/src/common/mo_req.cpp`、`ly_server/src/lib/config_agent.cpp`：数据库访问层捕获 `cppdb::cppdb_error`，调用 `log_err` 后以空结果/默认值继续执行。

## 3. 架构与约定

- **无自定义异常类型**：代码直接使用 `std::exception`（及其子类如 `cppdb::cppdb_error`），没有定义业务异常类或错误码结构体。
- **进程级安全网**：每个可执行程序的主入口都包裹一层 `try/catch(std::exception)`，确保任何未捕获异常都会转化为一条 `LOG_ERR` 日志，并以退出码 0 优雅退出，避免进程崩溃。
- **局部容错**：对非致命 I/O（如加载域名白名单、读取配置）使用 `catch (...)` 吞掉异常，仅 `log_warning` 并返回空集合，保证主流程不被单个文件损坏阻断。
- **DB 层静默降级**：数据库查询异常被捕获后记录错误日志并返回空容器，上层调用方按“无数据”语义继续。
- **HTTP CGI 错误**：参数解析失败时直接写回 `HTTP/1.1 400 Invalid Params\r\n\r\n` 响应头，不经过日志框架。
- **日志级别**：`log_err` → `LOG_ERR`，`log_warning` → `LOG_WARNING`，`log_info` → `LOG_INFO`；是否打印 DEBUG 信息受环境变量 `DEBUG` 控制（值为 `ALL` 或包含源文件名）。

## 4. 约束与规则

- 所有 C++ 进程的 `main()` 必须用 `try { process(); } catch (std::exception const &e) { log_err(...); }` 包裹（当前所有 handler 均遵循此模式）。
- 非致命资源加载（文件、缓存）应使用 `catch (...)` 并记录 `log_warning`，不得让异常向上传播。
- 数据库访问必须捕获 `cppdb::cppdb_error`，记录 `log_err` 后返回空结果，禁止将 DB 异常抛给调用方。
- 新增的 C++ 模块如需对外暴露错误，应优先返回空容器/默认值并通过 `log_err` 记录，而非抛出异常；需要中断流程时才允许异常冒泡至进程级 catch。
- 前端 ly_vis 与本分支的 ly_docs 为静态文档站点，未发现运行时错误处理逻辑，因此本模式仅适用于 C++ 后端组件。

## 5. 适用性说明

本仓库的 error_handling 集中在 C++ 后端，采用轻量级的进程级异常捕获 + syslog 日志方式，没有统一的错误码体系、中间件或结构化错误对象；Go/JS 子工程在本分支中未见相关实现。