---
kind: dependency_management
name: 多语言混合项目的依赖管理：源码级内联 + 预编译二进制归档 + Go/Node 包管理器
category: dependency_management
scope:
    - '**'
source_files:
    - ly_analyser/dependence/
    - ly_server/dependence/
    - ly_server/src/server/Makefile
    - ly_analyser/src/agent/Makefile
    - ly_vis/package.json
    - ly_vis/yarn.lock
    - ly_docs/go.mod
    - ly_docs/go.sum
---

## 1. 整体方案

本项目由四个子工程组成，每个子工程采用与其语言生态匹配的依赖管理方式，不存在统一的跨语言依赖管理系统：

- **ly_analyser / ly_server（C++）**：不通过任何包管理器声明第三方库，而是将第三方源码压缩包直接放入 `dependence/` 目录，并在构建时链接系统路径下的已安装库。
- **ly_vis（JavaScript/TypeScript）**：使用 Yarn Workspaces + Lerna 的多包架构，通过 `package.json` 声明依赖、`yarn.lock` 锁定版本。
- **ly_docs（Hugo/Go）**：使用 Go Modules（`go.mod` + `go.sum`）管理 Hugo 主题依赖。

## 2. C++ 部分：源码归档 + 系统路径链接

### 2.1 源码归档位置
- `ly_analyser/dependence/`：存放 `cgicc-3.2.16.tar.gz`、`cppdb-0.3.1.tar.bz2`、`protobuf-3.8.0.tar.gz`、`tf.tar.gz`、`tf_lib.tar.gz`。
- `ly_server/dependence/`：存放 `cgicc-3.2.16.tar.gz`、`cppdb-0.3.1.tar.bz2`、`protobuf-3.8.0.tar.gz`、`db.server.v1.1.231123.tar.gz`。

这些是**预打包的第三方源码/二进制归档**，以固定版本号命名并随仓库一起提交，属于“源码级 vendoring”的变体——但实际构建并不从这些 tar 包解压编译，而是假定依赖已在目标机器上安装到 `/usr/include`、`/usr/lib*`、`/usr/local/lib` 等标准路径。

### 2.2 构建期依赖声明
- `ly_server/src/server/Makefile` 中通过 `INCS` 指定头文件搜索路径（`/usr/include/mysql`、`/usr/include/cppdb`、`/usr/include/cgicc`），通过 `LDLIBS` 链接库（`-lcppdb -lcgicc -lcurl -lprotobuf -lmysqlclient -lpthread -ljson-c -lboost_regex`）。
- `ly_analyser/src/agent/Makefile` 仅做子目录递归构建，具体依赖由各子目录 Makefile 决定。
- 两个工程均**没有** `configure.ac`、`CMakeLists.txt`、`vcpkg.json`、`conanfile.py` 等可复现的依赖解析文件；依赖来源与版本完全依赖部署环境的系统包管理器或手动安装步骤。

### 2.3 内联第三方源码
除了 `dependence/` 中的归档外，项目还将部分第三方库源码直接内联到代码树中：
- `ly_analyser/src/common/rapidjson/`：RapidJSON 完整源码。
- `ly_analyser/src/nfdump/`：完整的 nfdump 源码树（含 autotools 生成文件）。
- `ly_server/src/common/rapidjson/`：同上。
- `ly_analyser/src/agent/dump/` 中包含 libnfdump、minilzo、fts_compat 等内联实现。

这些内联源码随仓库版本化，无需外部依赖即可编译对应模块，但与 `dependence/` 中的 tar 包所指向的库版本之间没有显式校验关系。

## 3. JavaScript/TypeScript 部分：Yarn Workspaces + Lerna

- `ly_vis/package.json` 定义工作区根，声明 `workspaces: ["packages/*"]`，并通过 Lerna 组织 `@shadowflow/std`、`@shadowflow/components` 等子包。
- `ly_vis/yarn.lock` 锁定所有依赖的确切版本与下载源，其中大量条目来自 `registry.npm.taobao.org`（淘宝镜像），表明构建环境配置了 npm 镜像源。
- 依赖版本策略以 `^` 主版本兼容为主（如 `antd: ^4.15.3`、`react: ^16.14`），由 yarn.lock 固化最终解析结果。
- 无 `.npmrc` 或 `package-lock.json`，统一使用 Yarn v1 锁文件。

## 4. Go/Hugo 文档部分：Go Modules

- `ly_docs/go.mod` 声明 module 为 `github.com/gohugoio/hugoDocs`，Go 版本 `1.16`。
- 唯一依赖是 Hugo 官方主题 `github.com/gohugoio/gohugoioTheme`，标记为 `// indirect`，说明主题通过 Hugo 的模块机制引入而非直接作为 Go 代码依赖。
- `ly_docs/go.sum` 记录了该主题的多个历史版本的哈希，用于校验。
- 无 GOPROXY、GOPRIVATE 等代理/私有仓库配置。

## 5. 约定与约束

| 领域 | 约定 | 证据 |
|---|---|---|
| C++ 第三方库 | 以固定版本 tar 包形式随仓库存放于 `dependence/`，但构建时假设已安装至系统标准路径 | `ly_server/Makefile` 的 INCS/LDLIBS 指向 `/usr/include`、`/usr/lib*` |
| 关键第三方源码 | RapidJSON、nfdump 等直接内联到 `src/common/` 或 `src/nfdump/`，随仓库版本化 | 目录结构可见 |
| Node.js 前端 | 使用 Yarn Workspaces + Lerna，依赖版本由 `yarn.lock` 锁定 | `ly_vis/package.json`、`ly_vis/yarn.lock` |
| Hugo 文档 | 使用 Go Modules，主题依赖通过 `go.mod` + `go.sum` 管理 | `ly_docs/go.mod`、`ly_docs/go.sum` |
| 包源 | 前端依赖通过淘宝镜像（taobao.org）拉取 | `yarn.lock` 中 `resolved` 字段包含 `registry.npm.taobao.org` |
| 无统一依赖管理 | 不存在跨语言的依赖清单、无 vendor 目录、无 lockfile 统一管理 | 各子工程各自为政 |

## 6. 风险点

- C++ 部分的 `dependence/` 归档与 `Makefile` 中链接的系统库版本之间缺乏自动化校验，存在“归档版本与运行时库版本不一致”的风险。
- 缺少 `vcpkg`、`Conan`、`CMake` 等现代 C++ 包管理工具，构建环境依赖度较高，可移植性受限。
- 前端依赖通过淘宝镜像拉取，若镜像不可用需切换回官方源。
- 未使用 `npm ci`/`yarn install --frozen-lockfile` 等严格模式脚本，CI 中可能允许锁文件漂移。