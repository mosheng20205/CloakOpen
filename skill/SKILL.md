---
name: cdp
description: Cloak 指纹浏览器 CDP 自动化控制。通过 Chrome DevTools Protocol 对单个或多个浏览器窗口进行自动化操作，支持导航、点击、输入、截图、执行 JS 等操作，以及批量群控。
disable-model-invocation: false
allowed-tools: mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__fill_form, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__hover, mcp__chrome-devtools__press_key, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__select_page, mcp__chrome-devtools__get_network_request, mcp__chrome-devtools__list_network_requests, mcp__chrome-devtools__handle_dialog, Bash, ToolSearch
license: MIT
metadata:
  version: 1.0.1
  author: Cloak Team
  category: browser-automation
  framework: CDP (Chrome DevTools Protocol)
  examples:
    - "列出所有运行中的浏览器"
    - "打开浏览器并导航到百度"
    - "批量打开多个浏览器执行相同操作"
    - "自动登录网站"
    - "截取所有浏览器屏幕"
    - "创建代理并应用到浏览器"
    - "批量设置代理"
    - "检测代理连通性"
  triggers:
    - "CDP"
    - "浏览器自动化"
    - "群控"
    - "批量操作"
    - "指纹浏览器"
    - "代理管理"
    - "代理IP"
---

# Cloak CDP 浏览器自动化 Skill

通过 Chrome DevTools Protocol (CDP) 对 Cloak 指纹浏览器进行自动化控制。支持单窗口和批量群控操作。

## 目录

- [快速开始](#快速开始)
- [工作流程](#工作流程)
- [API 参考](#api-参考)
- [常用场景](#常用场景)
- [批量操作](#批量操作)
- [故障排除](#故障排除)

## 快速开始

### 文档来源（与源码 OpenAPI 一致）

集成时请以本机服务导出的规范为准（你更新 `openapi.rs` 后，下列页面会同步变化）：

- **Swagger UI**：`http://127.0.0.1:54381/swagger-ui`
- **OpenAPI JSON**：`http://127.0.0.1:54381/api-docs/openapi.json`
- **Markdown 导出**：`http://127.0.0.1:54381/api-docs/markdown`

比特浏览器兼容接口的请求体字段一般为 **camelCase**（如 `groupId`、`browserFingerPrint`、`homepageUrl`，默认地址亦可用顶层 `url` 与 `homepageUrl` 同义）。

### 前提条件

1. **Cloak 客户端必须运行中**
   - HTTP API: `http://127.0.0.1:54381`
   - WebSocket: `ws://127.0.0.1:54382`

2. **至少有一个浏览器窗口已打开**
   - 通过 Cloak UI 打开，或
   - 调用 `POST /browser/open` API

### 基本操作流程

```
1. 获取浏览器列表 → 2. 连接到 CDP 端口 → 3. 执行自动化操作
```

### 第一步：获取浏览器列表

```bash
# 获取所有运行中的浏览器及其 CDP 端口
curl -X POST http://127.0.0.1:54381/browser/ports

# 返回示例
{
  "success": true,
  "data": {
    "profile-id-1": 9222,
    "profile-id-2": 9223,
    "profile-id-3": 9224
  }
}
```

### 第二步：连接 Chrome DevTools

使用 Chrome DevTools MCP 工具连接到 CDP 端口：

```
# 在 Chrome 中打开 CDP 调试页面
chrome://inspect/#devices

# 配置 Discover network targets
# 添加 localhost:9222, localhost:9223, etc.
```

或者直接使用 MCP 工具操作（推荐）：

```javascript
// 使用 mcp__chrome-devtools__navigate_page
// Chrome DevTools MCP 会自动连接到当前选中的页面
```

### 第三步：执行操作

使用 Chrome DevTools MCP 工具执行自动化：

| 操作 | MCP 工具 | 说明 |
|------|----------|------|
| 导航 | `mcp__chrome-devtools__navigate_page` | 打开 URL |
| 点击 | `mcp__chrome-devtools__click` | 点击元素 |
| 输入 | `mcp__chrome-devtools__fill` | 填写表单 |
| 截图 | `mcp__chrome-devtools__take_screenshot` | 截取屏幕 |
| 快照 | `mcp__chrome-devtools__take_snapshot` | 获取页面结构 |
| 执行 JS | `mcp__chrome-devtools__evaluate_script` | 运行 JavaScript |
| 等待 | `mcp__chrome-devtools__wait_for` | 等待文本出现 |

## 工作流程

### 工作流程 1：单浏览器自动化

```
用户请求 → 检查 Cloak 状态 → 获取浏览器端口 → 使用 MCP 工具操作 → 返回结果
```

**示例：自动登录网站**

1. 确认浏览器已打开
2. 导航到登录页面
3. 获取页面快照，找到选择器
4. 填写用户名和密码
5. 点击登录按钮
6. 等待登录成功

### 工作流程 2：批量群控

```
用户请求 → 获取所有浏览器 → 遍历每个浏览器 → 执行相同操作 → 汇总结果
```

**示例：批量打开网页**

1. 调用 `/browser/ports` 获取所有端口
2. 逐个连接并导航到目标 URL
3. 返回操作结果汇总

### 工作流程 3：基于 Profile ID 操作

```
用户提供 Profile ID → 查询 CDP 端口 → 连接并操作
```

## API 参考

### Cloak HTTP API (端口 54381)

#### 浏览器管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/browser/list` | POST | 获取浏览器列表 |
| `/browser/ports` | POST | 获取所有 CDP 端口 |
| `/browser/open` | POST | 打开浏览器 |
| `/browser/close` | POST | 关闭浏览器 |
| `/browser/detail` | POST | 获取浏览器详情 |
| `/browser/pids/all` | POST | 获取所有进程 PID |
| `/browser/update` | POST | 创建浏览器窗口（比特风格，含 `browserFingerPrint` 等） |
| `/browser/update/partial` | POST | 部分更新窗口（单条或批量 `ids`） |
| `/browser/create/batch` | POST | 批量创建窗口 |
| `/browser/delete`、`/browser/delete/batch`、`/browser/delete/all` | POST | 删除相关 |
| `/browser/close/batch` | POST | 批量关闭 |

#### 代理管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/proxy/list` | POST | 获取代理列表 |
| `/proxy/add` | POST | 创建代理 |
| `/proxy/delete` | POST | 删除代理 |
| `/proxy/check` | POST | 检测代理 |

#### 分组管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/group/list` | POST | 获取分组列表（支持分页等，见 Swagger） |
| `/group/add` | POST | 添加分组（请求体字段为 `groupName`，可选 `sortNum`） |
| `/group/edit` | POST | 编辑分组（`id`、`groupName`、可选 `sortNum`） |
| `/group/delete` | POST | 删除分组 |
| `/group/detail` | POST | 获取分组详情 |

### 请求/响应示例

#### POST /browser/list

```bash
curl -X POST http://127.0.0.1:54381/browser/list \
  -H "Content-Type: application/json" \
  -d '{"page": 0, "pageSize": 100}'

# 响应
{
  "success": true,
  "data": {
    "list": [
      {
        "id": "profile-uuid",
        "name": "账号1",
        "group": "默认分组",
        "proxy": "",
        "status": "运行中",
        "debugPort": 9222
      }
    ]
  }
}
```

#### POST /browser/open

```bash
curl -X POST http://127.0.0.1:54381/browser/open \
  -H "Content-Type: application/json" \
  -d '{"id": "profile-uuid"}'

# 响应
{
  "success": true,
  "data": {
    "ws": "127.0.0.1:9222/devtools/browser/...",
    "http": "127.0.0.1:9222",
    "debugPort": 9222,
    "pid": 12345,
    "name": "账号1",
    "profileId": "profile-uuid"
  }
}
```

#### POST /browser/ports

```bash
curl -X POST http://127.0.0.1:54381/browser/ports

# 响应
{
  "success": true,
  "data": {
    "profile-id-1": 9222,
    "profile-id-2": 9223
  }
}
```

### CDP WebSocket 接口

连接到 `ws://127.0.0.1:{port}/devtools/page/{target-id}`

#### 常用 CDP 命令

```javascript
// 导航
{"id": 1, "method": "Page.navigate", "params": {"url": "https://example.com"}}

// 执行 JavaScript
{"id": 2, "method": "Runtime.evaluate", "params": {"expression": "document.title"}}

// 截图
{"id": 3, "method": "Page.captureScreenshot", "params": {"format": "png"}}

// 点击 (通过 JS)
{"id": 4, "method": "Runtime.evaluate", "params": {"expression": "document.querySelector('#btn').click()"}}
```

## 常用场景

### 场景 1：检查浏览器状态

```bash
# 获取所有运行中的浏览器
curl -X POST http://127.0.0.1:54381/browser/ports

# 如果返回空对象，说明没有浏览器在运行
# 需要先打开浏览器
```

### 场景 2：打开浏览器并导航

1. 调用 Cloak API 打开浏览器：
```bash
curl -X POST http://127.0.0.1:54381/browser/open \
  -H "Content-Type: application/json" \
  -d '{"id": "profile-uuid"}'
```

2. 使用 MCP 工具导航：
```
mcp__chrome-devtools__navigate_page
参数: type="url", url="https://example.com"
```

### 场景 3：自动填写表单

1. 获取页面快照：
```
mcp__chrome-devtools__take_snapshot
```

2. 根据快照找到元素 uid

3. 填写表单：
```
mcp__chrome-devtools__fill_form
参数: elements=[{"uid": "input-uid", "value": "填写内容"}]
```

### 场景 4：执行 JavaScript

```
mcp__chrome-devtools__evaluate_script
参数: function="() => { return document.title; }"
```

### 场景 5：截图

```
mcp__chrome-devtools__take_screenshot
参数: format="png", fullPage=true
```

### 场景 6：创建和使用代理

#### 创建自定义代理

```bash
curl -X POST http://127.0.0.1:54381/proxy/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "香港代理",
    "type": "SOCKS5",
    "host": "45.12.33.1",
    "port": "1080",
    "username": "user",
    "password": "pass"
  }'
```

#### 创建 API 提取代理

```bash
curl -X POST http://127.0.0.1:54381/proxy/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "动态代理",
    "type": "SOCKS5",
    "host": "https://api.proxy.com/get?key=xxx",
    "port": "0"
  }'
```

**API 提取代理说明:**
- host 填写 API 提取链接（以 http:// 或 https:// 开头）
- port 固定填 "0" 作为标识
- 每次启动浏览器时自动从 API 获取新的代理 IP

#### 检测代理

```bash
curl -X POST http://127.0.0.1:54381/proxy/check \
  -H "Content-Type: application/json" \
  -d '{"id": "p1"}'
```

#### 为浏览器设置代理

**说明**：比特风格 `POST /browser/update` 当前实现以指纹与分组等为主；**已保存代理池中的代理 ID** 绑定到档案时，更稳妥的方式是使用 **REST** `PUT /api/v1/profiles/{id}` 传入 `proxyId`（需请求头 `X-Api-Key`），或在 Cloak 客户端内绑定。若使用比特文档中的 **内联代理** 字段（`proxyMethod`、`proxyType`、`host`、`port` 等），请以 Swagger 中 `BrowserUpdateRequest` 为准。

```bash
# 示例：创建窗口并带内联代理字段（字段以 Swagger 为准）
curl -X POST http://127.0.0.1:54381/browser/update \
  -H "Content-Type: application/json" \
  -d '{
    "name": "账号1",
    "groupId": "your-group-id",
    "randomFingerprint": true,
    "homepageUrl": "https://www.example.com"
  }'
```

### 场景 7：批量代理管理

```bash
# 获取所有代理
curl -X POST http://127.0.0.1:54381/proxy/list

# 批量为浏览器设置代理
# (需要逐个调用 /browser/update)
```

## 批量操作

### 代理管理

Cloak 支持两种代理模式：

#### 1. 自定义代理

手动配置代理服务器信息：
- 代理类型：HTTP/HTTPS/SOCKS5
- 服务器地址和端口
- 认证信息（可选）

```bash
curl -X POST http://127.0.0.1:54381/proxy/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "香港代理",
    "type": "SOCKS5",
    "host": "45.12.33.1",
    "port": "1080",
    "username": "user",
    "password": "pass"
  }'
```

#### 2. API 提取代理

通过 API 自动获取代理 IP：
- host 填写 API 提取链接
- port 固定填 "0" 作为标识
- 每次启动浏览器时自动从 API 获取新 IP

```bash
curl -X POST http://127.0.0.1:54381/proxy/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "动态代理",
    "type": "SOCKS5",
    "host": "https://api.proxy.com/get?key=xxx",
    "port": "0"
  }'
```

#### 代理检测

检测代理的连通性、延迟和地理位置：

```bash
curl -X POST http://127.0.0.1:54381/proxy/check \
  -H "Content-Type: application/json" \
  -d '{"id": "p1"}'
```

返回信息包括：
- 状态（有效/失效）
- 延迟（毫秒）
- 公网 IP 地址
- 地理位置（国家/地区/城市）
- ISP 运营商
- 时区

#### 为浏览器配置代理

绑定**代理池里已保存的代理**时，请使用 **REST** `PUT /api/v1/profiles/{id}`，请求体支持 `proxyId`（或 `proxy_id`）；需请求头 **`X-Api-Key`**（见 Swagger 中「RESTful API」说明）。修改代理后通常需要关闭再打开对应浏览器才能生效。

```bash
curl -X PUT "http://127.0.0.1:54381/api/v1/profiles/PROFILE_UUID" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -d '{"proxyId": "p1"}'
```

`POST /browser/update` 侧重点是比特风格的指纹与分组等；内联代理字段以 Swagger 中 `BrowserUpdateRequest` 为准，与「代理池 ID」绑定不是同一套字段。

#### 批量代理管理

为多个浏览器批量设置相同代理时，对每个 profile 调用上述 `PUT /api/v1/profiles/{id}`（或于客户端操作），再按需批量关闭/打开：

```bash
curl -X POST http://127.0.0.1:54381/browser/close/all
curl -X POST http://127.0.0.1:54381/browser/open/all
```

### 批量操作策略

#### 方式 1：通过 Cloak API

Cloak 提供批量操作 API：

```bash
# 批量打开浏览器
curl -X POST http://127.0.0.1:54381/browser/open/batch \
  -H "Content-Type: application/json" \
  -d '{"ids": ["id1", "id2", "id3"]}'

# 批量关闭浏览器
curl -X POST http://127.0.0.1:54381/browser/close/batch \
  -H "Content-Type: application/json" \
  -d '{"ids": ["id1", "id2", "id3"]}'
```

#### 方式 2：遍历操作

对于自动化操作，需要逐个连接 CDP 端口执行：

```
1. 调用 /browser/ports 获取所有端口
2. 对每个端口：
   a. 连接到 Chrome DevTools
   b. 执行操作
   c. 记录结果
3. 汇总所有结果
```

#### 方式 3：并行操作

对于独立操作，可以并行执行以提高效率。

### 批量操作示例

**批量导航到同一 URL**

```bash
# 1. 获取所有端口
PORTS=$(curl -s -X POST http://127.0.0.1:54381/browser/ports | jq -r '.data | to_entries[] | .value')

# 2. 对每个端口执行导航（需要通过 CDP）
for port in $PORTS; do
  echo "Navigating browser on port $port"
  # 通过 CDP 发送导航命令
done
```

## MCP 工具使用指南

### Chrome DevTools MCP 工具

**重要**: Chrome DevTools MCP 工具需要先加载才能使用。

```
# 加载工具
ToolSearch query="chrome-devtools"
```

### 常用工具说明

#### mcp__chrome-devtools__take_snapshot

获取页面可访问性树快照，返回元素及其 uid。

```
用于：
- 了解页面结构
- 获取元素的 uid 用于后续操作
- 验证操作结果
```

#### mcp__chrome-devtools__click

点击页面元素。

```
参数:
- uid: 从 snapshot 获取的元素 uid
- dblClick: 是否双击 (可选)
```

#### mcp__chrome-devtools__fill

在输入框中填写文本。

```
参数:
- uid: 输入框的 uid
- value: 要填写的文本
```

#### mcp__chrome-devtools__fill_form

批量填写多个表单字段。

```
参数:
- elements: [{"uid": "uid1", "value": "value1"}, ...]
```

#### mcp__chrome-devtools__navigate_page

导航到 URL 或前进/后退/刷新。

```
参数:
- type: "url" | "back" | "forward" | "reload"
- url: 目标 URL (type="url" 时)
```

#### mcp__chrome-devtools__evaluate_script

执行 JavaScript 代码。

```
参数:
- function: JavaScript 函数字符串
- args: 参数列表 (可选)
```

#### mcp__chrome-devtools__take_screenshot

截取屏幕截图。

```
参数:
- format: "png" | "jpeg" | "webp"
- fullPage: 是否全页截图
- filePath: 保存路径 (可选)
```

#### mcp__chrome-devtools__wait_for

等待指定文本出现。

```
参数:
- text: 要等待的文本
- timeout: 超时时间 (毫秒)
```

## 故障排除

### 问题 1：无法连接到 Cloak API

**症状**: 调用 `http://127.0.0.1:54381` 无响应

**解决方案**:
1. 确认 Cloak 客户端正在运行
2. 检查端口是否被占用
3. 检查防火墙设置

### 问题 2：浏览器列表为空

**症状**: `/browser/ports` 返回空对象

**解决方案**:
1. 在 Cloak UI 中打开至少一个浏览器窗口
2. 或调用 `/browser/open` API 打开浏览器

### 问题 3：CDP 连接失败

**症状**: 无法连接到 `127.0.0.1:{port}`

**解决方案**:
1. 确认浏览器进程仍在运行 (`/browser/pids/all`)
2. 确认 CDP 端口正确 (`/browser/ports`)
3. 检查浏览器是否崩溃

### 问题 4：元素找不到

**症状**: click 或 fill 操作失败

**解决方案**:
1. 先调用 `take_snapshot` 获取最新页面结构
2. 使用返回的 uid 进行操作
3. 检查元素是否在 iframe 中

### 问题 5：操作超时

**症状**: CDP 命令超时

**解决方案**:
1. 增加等待时间
2. 使用 `wait_for` 等待页面加载完成
3. 检查网络连接

## 最佳实践

### 1. 始终先检查状态

在执行任何操作前，先调用 `/browser/ports` 确认浏览器状态。

### 2. 使用快照获取选择器

不要猜测元素选择器，使用 `take_snapshot` 获取准确的 uid。

### 3. 添加适当的等待

页面加载和动画需要时间，使用 `wait_for` 确保元素就绪。

### 4. 处理错误 gracefully

每个操作都可能失败，添加错误处理和重试逻辑。

### 5. 批量操作时控制并发

避免同时操作过多浏览器，可能触发反爬检测。

## 相关资源

- [Chrome DevTools Protocol 文档](https://chromedevtools.github.io/devtools-protocol/)
- [Cloak README](../../README.md)
- [Cloak CLAUDE.md](../../CLAUDE.md)
