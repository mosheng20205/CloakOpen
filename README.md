# Cloak 开放示例（BitBrowser 风格 HTTP API）

[Cloak](https://bcloak.com/) 是一款支持 **API 与自动化集成** 的指纹浏览器管理系统。本仓库提供 **README 说明** 与 **多语言最小可运行示例**，便于在 GitHub 上快速了解产品能力并接入本地 HTTP 接口。

- **官网**：<https://bcloak.com/>
- **默认本机 API 基址**：`http://127.0.0.1:54381`（需先启动 Cloak 桌面端）
- **协议约定**：接口均为 **POST**，请求与响应一般为 **JSON**；比特浏览器兼容路径（如 `/browser/update`、`/browser/open` 等）使用 **camelCase** 字段名（如 `groupId`、`browserFingerPrint`）。

## 功能概览（面向集成方）

- **环境管理**：多浏览器配置、指纹参数、分组与标签。
- **比特风格 API**：创建/更新窗口、列表、打开（返回 CDP 相关信息）、关闭、批量操作等。
- **代理**：代理列表与检测等（具体字段以当前服务端 Swagger 为准）。
- **自动化**：打开窗口后可通过 CDP / 自有 RPA 流程继续控制（详见 Cloak 客户端与文档）。

完整 Python 参考实现见本仓库根目录：`cloak_api_example.py`（与 bitfbro 主项目 `docs/ApiDemo/cloak_api_example.py` 同步复制，覆盖分组/代理/窗口/批量等接口示例）。安装依赖：`pip install -r requirements.txt`，再运行 `python cloak_api_example.py`（可加 `--cleanup`）。

## skill/ 目录（CDP 自动化技能与参考文档）

`skill/` 下放的是面向 **AI 编码助手（如 Cursor、Claude Code）** 的 **Skill 包**，也可作为普通文档阅读；与根目录 `demos/` 互补：`demos/` 侧重各语言 **最小 HTTP 调用**，`skill/` 侧重 **CDP 自动化、本地 API 与 OpenAPI 对齐说明、工作流与排错**。

### 用途

- 指导智能体：在已启动 Cloak 的前提下，通过 **`POST http://127.0.0.1:54381`** 获取窗口列表与调试端口，再结合 **Chrome DevTools Protocol** 或 **Chrome DevTools MCP** 做导航、点击、填表、截图、执行 JS 等。
- 覆盖 **单窗口与批量群控**、代理列表/检测、以及比特风格接口与 **Swagger**（`http://127.0.0.1:54381/swagger-ui`）的字段约定说明。

### 文件说明

| 文件 | 内容 |
|------|------|
| `skill/SKILL.md` | 主入口：YAML 元数据、快速开始、Cloak HTTP API 速查、MCP 工具表、常用场景与最佳实践 |
| `skill/API_REFERENCE.md` | HTTP 与 CDP 相关端点、请求/响应示例；并注明以本机 **OpenAPI / Swagger** 为准 |
| `skill/WORKFLOWS.md` | 分场景步骤：单浏览器操作、自动登录、批量打开、代理配置、AI 对话接口等 |
| `skill/TROUBLESHOOTING.md` | 无法连 API、CDP、元素定位、批量与性能等问题的排查思路 |

### 使用方式

- **当文档读**：直接在仓库中打开上述 Markdown。
- **当 Cursor / Claude Skill 用**：将 `skill/` 整目录复制到对应客户端要求的 **skills 目录**（或打包为 zip 后按该工具说明导入）；主文件为 `SKILL.md`（frontmatter 中含 `name`、`description`、触发词等）。

## 多语言示例

| 语言 | 路径 | 运行方式 |
|------|------|----------|
| Python 3 | `demos/python/cloak_demo.py` | `python cloak_demo.py` |
| Node.js 18+ | `demos/nodejs/cloak_demo.mjs` | `node cloak_demo.mjs` |
| Go 1.21+ | `demos/go` | `go run .` |
| .NET 8+ | `demos/csharp` | `dotnet run` |
| Java 11+ | `demos/java` | `javac CloakDemo.java && java CloakDemo` |

各示例默认执行：**列分组 → 创建演示分组 → 创建窗口 → 列表 → 打开 → 关闭**；设置环境变量 `CLOAK_CLEANUP=1` 可在结束时尝试删除本次创建的窗口与分组（失败时仅打印提示）。

### 环境变量

| 变量 | 含义 | 默认 |
|------|------|------|
| `CLOAK_BASE_URL` | API 根地址 | `http://127.0.0.1:54381` |
| `CLOAK_CLEANUP` | 非空则在演示末尾清理创建的资源 | 空（不清理） |

## 许可证

示例代码按仓库根目录许可证文件执行（若未指定，以你方在 GitHub 上声明的仓库许可为准）。
