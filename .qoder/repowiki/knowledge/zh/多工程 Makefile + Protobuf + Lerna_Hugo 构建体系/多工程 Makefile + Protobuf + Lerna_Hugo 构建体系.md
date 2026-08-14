---
kind: build_system
name: 多工程 Makefile + Protobuf + Lerna/Hugo 构建体系
category: build_system
scope:
    - '**'
source_files:
    - ly_analyser/src/agent/Makefile
    - ly_analyser/src/agent/config/Makefile
    - ly_analyser/src/agent/data/Makefile
    - ly_analyser/src/agent/flow/Makefile
    - ly_analyser/src/common/Makefile
    - ly_server/src/common/Makefile
    - ly_server/src/server/Makefile
    - ly_server/src/lib/Makefile
    - ly_server/src/common/baseline/Makefile
    - ly_vis/package.json
    - ly_vis/lerna.json
    - ly_docs/hugo.work
    - ly_docs/netlify.toml
    - ly_docs/hugoreleaser.toml
    - ly_analyser/INSTALL.md
    - ly_server/INSTALL.md
---

## 1. 整体方案

本项目由四个子工程组成，每个子工程使用各自独立的构建系统，没有顶层统一的 CI/Makefile：
- `ly_analyser`（C++ 分析引擎）：手写 Makefile + Google Protocol Buffers，依赖 Boost、protobuf、TensorFlow C++ API、unqlite、nfdump。
- `ly_server`（C++ 管理后端）：手写 Makefile + protobuf，依赖 MySQL、cppdb、cgicc、curl、Boost。
- `ly_vis`（React 前端）：Lerna + Yarn Workspaces + create-react-app（react-scripts），ESLint/Prettier/Stylelint 代码检查，Husky + commitlint 提交规范。
- `ly_docs`（文档站）：Hugo 静态站点生成器，通过 `hugo work` 与 Hugo 主题模块构建。

部署产物以 tar.gz 包形式发布（如 `ly_analyser_release.v1.0.0.221226.tar.gz`、`ly_server_release.v1.0.0.221229.tar.gz`），配合 `agent_deploy_new.sh` / `server_deploy_new.sh` 脚本在 CentOS 7 上安装。仓库中未包含打包脚本源码，仅保留依赖包（`dependence/` 下的 `cgicc-3.2.16.tar.gz`、`protobuf-3.8.0.tar.gz`、`tf.tar.gz`、`tf_lib.tar.gz`、`db.server.v1.1.231123.tar.gz`）。未发现 Dockerfile、Docker Compose、GitHub Actions/GitLab CI 等容器化或 CI 配置。

## 2. 关键文件

- `ly_analyser/src/agent/Makefile`：递归调用 `dump/utils/config/model/data/flow/indexing/handlers` 子目录的 make。
- `ly_analyser/src/agent/{config,data,flow,handlers,...}/Makefile`：各模块独立编译为 `.a`/`.so`，并通过 `protoc --cpp_out=.` 生成 protobuf 代码。
- `ly_analyser/src/common/Makefile`：构建共享库 `libcommon.so`（同时产出 `libcommon.a`），供 agent/server 共用；定义 `SERVER_INSTALL_DIR=/Server/lib`、`AGENT_INSTALL_DIR=/Agent/lib`。
- `ly_server/src/common/Makefile`：与 ly_analyser 同名的共享库构建入口，同样生成 `libcommon.so` 并安装到 `/Server/lib`、`/Agent/lib`、`/lib64`。
- `ly_server/src/server/Makefile`：编译 CGI/命令行二进制（`event`、`feature`、`auth`、`config_pusher`、`gen_event` 等），安装到 `/Server/www/d`、`/Server/bin`。
- `ly_server/src/lib/Makefile`：将各配置模块编译为动态插件（`config_event.so`、`config_mo.so`、`config_agent.so`、`config_bwlist.so`、`config_user.so` 等），安装到 `/Server/lib`。
- `ly_vis/package.json`、`ly_vis/lerna.json`：Lerna monorepo 根配置，workspaces 指向 `packages/*`，scripts 提供 `lerna`、`std`、`asset` 等命令。
- `ly_docs/hugo.work`、`ly_docs/config/_default/config.toml`、`ly_docs/netlify.toml`、`ly_docs/hugoreleaser.toml`：Hugo 站点构建与发布配置。
- `ly_analyser/INSTALL.md`、`ly_server/INSTALL.md`：官方安装说明，描述依赖安装、tar.gz 包解压、部署脚本执行流程。

## 3. 架构与约定

- **分层构建**：`ly_analyser` 采用 `dump → model → data → config → flow → handlers → indexing` 的链式依赖，上层 Makefile 通过 `LIBS=../dump/libnfdump.a ../model/model.a ../data/data.a ../config/config.a` 链接下层产物。
- **共享库契约**：`src/common` 是 ly_analyser 与 ly_server 共用的基础库，通过 `libcommon.so`（同时归档为 `libcommon.a`）暴露公共接口；两个工程的 Makefile 都 `-I../../common` 并链接 `-lcommon`。
- **Protobuf 协议驱动**：所有跨进程通信结构体（`cache.proto`、`config.proto`、`event.proto`、`policy.proto`、`ctl.proto`、`domaininfo.proto`、`evidence.proto`、`topn.proto`、`mo.proto`、`feature.proto`、`event_feature.proto`、`dbctx.proto`、`baseline.proto`、`config_agent.proto`、`config_bwlist.proto`、`config_user.proto` 等）统一通过 `protoc --cpp_out=.` 生成 `.pb.cc/.pb.h`，再由各模块 Makefile 参与编译。
- **CGI 部署模式**：ly_server 将可执行程序直接输出到 `/Server/www/d/`，由 Apache httpd 以 CGI 方式调用；ly_analyser 将程序输出到 `/Agent/cmd`、`/Agent/bin`，通过 stunnel + httpd 暴露端口 10081。
- **插件式配置模块**：ly_server 的 `src/lib` 将每种配置类型编译为独立 `.so` 插件，运行时由主进程动态加载。
- **前端 Monorepo**：`ly_vis` 使用 Lerna + Yarn Workspaces，`@shadowflow/std`、`@shadowflow/asset` 等包通过 workspace 引用，统一 lint（eslint/prettier/stylelint）和提交钩子（husky + commitlint）。
- **文档站点**：`ly_docs` 使用 Hugo，通过 `hugo work` 启动开发服务器，生产构建由 hugoreleaser/netlify 触发。

## 4. 约定与约束

- **目标平台**：CentOS 7 x86_64 Minimal，要求 `boost`、`httpd`、`stunnel`、`mariadb-server`、`MySQL-python`、`sysstat`、`net-tools`、`ntpdate` 等 yum 包已安装（见 INSTALL.md）。
- **编译器与标准**：C++ 源统一使用 `g++`，核心库使用 `-std=c++1y`（即 C++14），部分旧模块使用 `-std=c++11`/`c++0x`；启用 `-Wall -g -fPIC -O2`。
- **安装路径固定**：服务端安装到 `/Server/{bin,www,d,lib}`，分析引擎安装到 `/Agent/{bin,cmd,lib,data}`，共享库额外复制到 `/lib64` 并执行 `ldconfig`。
- **Protobuf 必须先行**：任何 `.proto` 变更需先运行 `protoc` 生成 `.pb.cc/.pb.h`，否则对应 target 无法编译（各 Makefile 均显式声明 `$(PB_SRCS):$(PBS)` 规则）。
- **本地调试开关**：多个 Makefile 通过 `-include ../local_debug.mk` / `local_debug.mk` 引入可选覆盖变量，用于开发时调整编译选项。
- **版本命名**：发布包采用 `ly_{component}_release.v{major}.{minor}.{patch}{yyyymmdd}.tar.gz` 格式（如 `v1.0.0.221226`），依赖包也带版本号（如 `db.server.v1.1.231123.tar.gz`）。
- **无容器化/CI**：仓库未包含 Dockerfile、docker-compose、GitHub Actions、GitLab CI 等自动化构建/部署配置，构建与发布目前依赖手工执行 tar.gz 包与部署脚本。
- **前端质量门禁**：`ly_vis` 通过 Husky 在 pre-commit 阶段运行 lint-staged（eslint/prettier），commit-msg 阶段运行 commitlint（`@commitlint/config-conventional`），强制提交信息遵循 conventional commits 规范。
- **Hugo 环境**：`ly_docs` 通过 `go.mod`/`go.sum` 锁定 Hugo 版本，使用 hugoreleaser 进行发布，Netlify 通过 `netlify.toml` 配置构建命令。