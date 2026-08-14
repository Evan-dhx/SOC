---
kind: frontend_style
name: ShadowFlow 前端样式体系：基于 Ant Design + Less 的多包组件化主题方案
category: frontend_style
scope:
    - '**'
source_files:
    - ly_vis/package.json
    - ly_vis/.eslintrc.js
    - ly_vis/.prettierrc.js
    - ly_vis/.stylelintrc.js
    - ly_vis/packages/components/style/index.less
    - ly_vis/packages/components/style/reset/index.less
    - ly_vis/packages/components/charts/charts.less
    - ly_vis/packages/std/package.json
    - ly_docs/static/css/style.css
    - ly_docs/src/css/_chroma.css
---

## 1. 系统与方法

本项目的前端样式体系集中在 `ly_vis`（ShadowFlow 可视化分析前端）与 `ly_docs`（Hugo 文档站点）两个子工程中，采用不同的技术栈：

- **ly_vis**：基于 React + Ant Design 4.x 的可视化分析界面，使用 Lerna + Yarn Workspaces 多包架构（`packages/components`、`packages/std`），通过 `react-app-rewired` 扩展 Create React App。样式语言为 **Less**，配合 `less-loader` 编译。
- **ly_docs**：基于 Hugo 静态文档站，使用 Hugo 内置主题 `gohugoio/gohugoioTheme`（位于 `ly_docs/_vendor/...`），并通过 `static/css/style.css` 与 `src/css/_chroma.css` 进行覆盖式定制。

代码质量与风格由以下工具链统一约束：ESLint（Airbnb 规则 + react-app）、Prettier、Stylelint（stylelint-config-standard）、Husky + lint-staged（pre-commit 钩子）。提交信息遵循 conventional commit（commitlint + cz-conventional-changelog）。

## 2. 关键文件与包

| 路径 | 作用 |
|---|---|
| `ly_vis/package.json` | 顶层依赖声明（antd、@ant-design/pro-table、d3、echarts、mobx、i18next、less 等）及工作区脚本 |
| `ly_vis/.eslintrc.js` | ESLint 配置，继承 react-app + airbnb + prettier/recommended |
| `ly_vis/.prettierrc.js` | Prettier 格式化规则（单引号、无分号、tabWidth 4、arrowParens avoid） |
| `ly_vis/.stylelintrc.js` | Stylelint 配置，继承 stylelint-config-standard，自定义缩进 4、忽略 pseudo-class global/local |
| `ly_vis/packages/components/style/index.less` | 全局样式入口，引入 antd default.less 主题变量、tooltip.less、reset 目录、charts.less |
| `ly_vis/packages/components/style/reset/*.less` | 对 Ant Design 各组件（btn、form、table、modal、select、tag 等）的局部覆盖 |
| `ly_vis/packages/components/charts/charts.less` | 图表容器通用样式（chart-container、chart-withpage） |
| `ly_vis/packages/components/ui/*` | 业务 UI 组件（container、form、layout、modal、table、tag、tooltips、icon 等） |
| `ly_vis/packages/std/package.json` | 主应用包，依赖 @shadowflow/components、echarts、d3-voronoi-treemap 等 |
| `ly_docs/static/css/style.css` | Hugo 文档站全局样式（字体、侧边栏、链接下划线动画、body 背景色 #edece4） |
| `ly_docs/src/css/_chroma.css` | 代码高亮 Chroma 主题样式 |

## 3. 架构与约定

### 3.1 多包组件化结构
`ly_vis` 采用 Lerna monorepo：
- `@shadowflow/components`：共享 UI 组件库与样式层，暴露 `index.js` 作为入口，内部按功能划分 `ui/`、`charts/`、`config-store/`、`locale/`、`request-config/`、`utils/`、`style/` 等子目录。
- `@shadowflow/std`：主应用，通过 `react-app-rewired` 启动，依赖 `@shadowflow/components` 提供的组件与样式。

### 3.2 主题与 CSS 变量
全局样式入口 `packages/components/style/index.less` 通过 `@import '~antd/es/style/themes/default.less'` 引入 Ant Design 默认主题变量，并在此基础上定义 CSS 变量用于业务层：
- `--bg-body`、`--bg-default`、`--bg-hover`、`--bg-desc`：背景色变量
- `--text-main`、`--text-link`、`--text-disabled`：文本色变量
- `--bg-default-rgb`：用于半透明遮罩
这些变量在 body、滚动条、菜单、loading 等全局样式中被引用，形成统一的视觉基线。

### 3.3 Ant Design 组件覆盖策略
通过 `packages/components/style/reset/` 下的独立 less 文件对 Ant Design 各组件进行细粒度覆盖（如 btn.less、form.less、table.less、modal.less、select.less、tag.less、pagination.less、steps.less、tab.less、checkbox.less、datepicker.less、dropdown.less、empty.less、input.less、list.less、radio.less、other.less），集中管理组件级样式差异，避免散落在业务组件中。

### 3.4 图表样式规范
`charts/charts.less` 定义了统一的图表容器类 `.chart-container`（宽高 100%、font-size 9px、tooltip 绝对定位防遮挡）和分页容器 `.chart-withpage`，所有图表组件复用该样式。

### 3.5 文档站样式
`ly_docs` 使用 Hugo 官方主题，通过 `static/css/style.css` 覆盖默认样式：Lato 字体、#edece4 背景色、侧边栏固定布局、链接 hover 下划线动画（#ff4088 强调色）、代码块使用 Menlo/Consolas 等等宽字体。`_chroma.css` 提供代码高亮配色。

## 4. 约定与约束

### 4.1 强制的代码风格（通过 CI/Hook 执行）
- **ESLint**：继承 `react-app`、`airbnb`、`plugin:prettier/recommended`，在 pre-commit 阶段对 `*.{js,jsx,ts,tsx}` 执行。
- **Prettier**：单引号、无分号、tabWidth 4、JSX 单引号、arrowParens avoid，作用于 JS/TS/Less/CSS。
- **Stylelint**：继承 `stylelint-config-standard`，缩进 4 空格，允许 `:global`、`:local` pseudo-class，作用于 `*.{css,less}`。
- **Commitlint**：遵循 `@commitlint/config-conventional`，通过 Husky 的 `commit-msg` 钩子强制执行。
- **lint-staged**：仅对暂存文件执行上述检查，提升提交效率。

### 4.2 样式组织约定
- 全局样式集中于 `packages/components/style/index.less`，业务组件样式放在对应组件目录或 `reset/` 下的覆盖文件。
- 图表相关样式统一放在 `packages/components/charts/` 下，通过 `.chart-container` 类名复用。
- Ant Design 组件覆盖按组件类型拆分到 `style/reset/` 下的独立 less 文件，便于维护。
- 文档站样式直接写在 `static/css/style.css`，不引入第三方 CSS 框架。

### 4.3 浏览器兼容
通过 `browserslist` 配置：生产环境支持 ">0.2%, not dead, not op_mini all"，开发环境支持最近版本的 Chrome/Firefox/Safari。