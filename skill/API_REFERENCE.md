# Cloak CDP API 参考

本文档为技能说明速查；**字段与路径以运行中服务导出的 OpenAPI 为准**（随 `src-tauri/src/api/openapi.rs` 更新）。

- **Swagger UI**: `http://127.0.0.1:54381/swagger-ui`
- **OpenAPI JSON**: `http://127.0.0.1:54381/api-docs/openapi.json`
- **Markdown 导出**: `http://127.0.0.1:54381/api-docs/markdown`

## 基础信息

- **HTTP API 地址**: `http://127.0.0.1:54381`
- **WebSocket 地址**: `ws://127.0.0.1:54382`
- **CDP 端口范围**: `9222 - 9999`（实际以运行时分配为准）
- **健康检查**: `GET /health` 或 `POST /health`

## 浏览器管理 API

### POST /browser/list

获取浏览器配置文件列表。

**请求体:**
```json
{
  "page": 0,
  "pageSize": 100
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": "uuid-string",
        "name": "浏览器名称",
        "group": "分组名称",
        "proxy": "http://user:pass@host:port",
        "status": "运行中|已关闭",
        "debugPort": 9222,
        "lastUsed": "2024-01-01T00:00:00Z",
        "tags": ["标签1", "标签2"]
      }
    ],
    "total": 10
  }
}
```

### POST /browser/open

打开指定浏览器。

**请求体:**
```json
{
  "id": "profile-uuid"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "ws": "127.0.0.1:9222/devtools/browser/xxx",
    "http": "127.0.0.1:9222",
    "debugPort": 9222,
    "pid": 12345,
    "name": "浏览器名称",
    "profileId": "profile-uuid"
  }
}
```

**错误响应:**
```json
{
  "success": false,
  "msg": "浏览器已打开"
}
```

### POST /browser/close

关闭指定浏览器。

**请求体:**
```json
{
  "id": "profile-uuid"
}
```

**响应:**
```json
{
  "success": true,
  "data": null
}
```

### POST /browser/close/all

关闭所有运行中的浏览器。

**请求体:** 无

**响应:**
```json
{
  "success": true,
  "data": {
    "closedCount": 5
  }
}
```

### POST /browser/ports

获取所有运行中浏览器的 CDP 端口。

**请求体:** 无

**响应:**
```json
{
  "success": true,
  "data": {
    "profile-id-1": 9222,
    "profile-id-2": 9223,
    "profile-id-3": 9224
  }
}
```

### POST /browser/pids/all

获取所有运行中浏览器的进程 ID。

**请求体:** 无

**响应:**
```json
{
  "success": true,
  "data": {
    "profile-id-1": 12345,
    "profile-id-2": 12346
  }
}
```

### POST /browser/detail

获取浏览器详情。

**请求体:**
```json
{
  "id": "profile-uuid"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "浏览器名称",
    "group": "分组",
    "proxy": "",
    "status": "运行中",
    "debugPort": 9222,
    "fingerprint": {
      "userAgent": "Mozilla/5.0...",
      "platform": "Win32",
      "resolution": "1920x1080",
      "canvas": "噪音",
      "webgl": "噪音",
      "audio": "噪音",
      "webrtc": "转发",
      "timezone": "Asia/Shanghai",
      "language": "zh-CN"
    }
  }
}
```

### POST /browser/update

创建或更新浏览器配置（**比特浏览器兼容**，camelCase）。

**请求体（节选，完整见 Swagger `BrowserUpdateRequest`）：**
```json
{
  "name": "浏览器名称",
  "groupId": "550e8400-e29b-41d4-a716-446655440000",
  "randomFingerprint": false,
  "homepageUrl": "https://example.com",
  "tags": ["标签1", "标签2"],
  "browserFingerPrint": {
    "coreVersion": "130",
    "ostype": "PC",
    "os": "Win32",
    "timeZone": "Asia/Shanghai",
    "webRTC": "3",
    "canvas": "0",
    "webGL": "0",
    "audioContext": "0"
  }
}
```

**说明**：绑定「代理池」中已保存的代理 ID 时，优先使用 **REST** `PUT /api/v1/profiles/{id}` 的 `proxyId`（需 `X-Api-Key`）。内联代理（`proxyMethod`、`proxyType`、`host`、`port` 等）见 OpenAPI。

### POST /browser/update/partial

部分更新浏览器（单条 `id` 或批量 `ids`），请求体为比特兼容结构，指纹子对象字段名为 `browserFingerPrint`。详见 Swagger。

### POST /browser/delete

删除浏览器配置。

**请求体:**
```json
{
  "id": "profile-uuid"
}
```

## 批量操作 API

### POST /browser/open/batch

批量打开浏览器。

**请求体:**
```json
{
  "ids": ["id1", "id2", "id3"]
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "results": [
      {"id": "id1", "success": true, "debugPort": 9222},
      {"id": "id2", "success": true, "debugPort": 9223},
      {"id": "id3", "success": false, "error": "浏览器已打开"}
    ]
  }
}
```

### POST /browser/close/batch

批量关闭浏览器。

**请求体:**
```json
{
  "ids": ["id1", "id2", "id3"]
}
```

### POST /browser/open/all

打开所有浏览器。

**请求体:** 无

### POST /browser/delete/batch

批量删除浏览器配置。

**请求体:**
```json
{
  "ids": ["id1", "id2", "id3"]
}
```

## 代理管理 API

### POST /proxy/list

获取所有代理配置列表。

**请求体:** 无

**响应:**
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": "p1",
        "name": "香港代理",
        "type": "SOCKS5",
        "host": "45.12.33.1",
        "port": "1080",
        "username": "user",
        "password": "pass",
        "remark": "备注信息",
        "status": "有效",
        "latency": "45ms",
        "publicIp": "45.12.33.1",
        "country": "中国",
        "region": "香港",
        "city": "香港",
        "isp": "HKT",
        "timezone": "Asia/Hong_Kong",
        "lastCheckTime": "2024-01-01T00:00:00Z"
      },
      {
        "id": "p2",
        "name": "动态代理",
        "type": "SOCKS5",
        "host": "https://api.proxy.com/get?key=xxx",
        "port": "0",
        "remark": "API提取代理",
        "status": "未检测"
      }
    ]
  }
}
```

### POST /proxy/add

创建新的代理配置。支持两种模式：

1. **自定义代理**: 手动输入代理配置
2. **API提取代理**: 通过API自动获取代理（host填API链接，port填"0"）

**请求体:**
```json
{
  "name": "代理名称",
  "type": "SOCKS5",
  "host": "45.12.33.1",
  "port": "1080",
  "username": "user",
  "password": "pass",
  "remark": "备注信息"
}
```

**API提取代理示例:**
```json
{
  "name": "动态代理",
  "type": "SOCKS5",
  "host": "https://api.proxy.com/get?key=xxx",
  "port": "0",
  "remark": "每次启动浏览器自动获取新IP"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "p1",
    "name": "香港代理",
    "type": "SOCKS5",
    "host": "45.12.33.1",
    "port": "1080"
  }
}
```

**代理类型:**
- `HTTP` - HTTP 代理
- `HTTPS` - HTTPS 代理
- `SOCKS5` - SOCKS5 代理（推荐）

### POST /proxy/delete

删除指定的代理配置。

**请求体:**
```json
{
  "id": "p1"
}
```

**响应:**
```json
{
  "success": true,
  "data": null
}
```

**注意**: 删除代理前会自动解除所有使用该代理的浏览器关联。

### POST /proxy/check

检测代理的连通性、延迟和地理位置信息。

**请求体:**
```json
{
  "id": "p1"
}
```

**响应（字段以 Swagger `ProxyCheckResult` 为准）：**
```json
{
  "success": true,
  "data": {
    "id": "p1",
    "status": "有效",
    "latency": "45ms",
    "isVerified": true,
    "publicIp": "45.12.33.1",
    "country": "中国",
    "region": "香港",
    "city": "香港",
    "isp": "HKT",
    "timezone": "Asia/Hong_Kong",
    "errorMessage": null
  }
}
```

**失败响应示例:**
```json
{
  "success": true,
  "data": {
    "id": "p1",
    "status": "失效",
    "latency": "0ms",
    "isVerified": false,
    "errorMessage": "连接超时"
  }
}
```

## 分组管理 API

### POST /group/list

获取分组列表。

**请求体:** 无

**响应:**
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": "group-uuid",
        "name": "分组名称",
        "profileCount": 5,
        "createdAt": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

### POST /group/add

创建分组。

**请求体:**
```json
{
  "groupName": "新分组",
  "sortNum": 0
}
```

### POST /group/delete

删除分组。

**请求体:**
```json
{
  "id": "group-uuid"
}
```

### POST /group/edit

编辑分组（字段见 Swagger；含 `id`、`groupName`、可选 `sortNum`）。

### POST /group/detail

获取分组详情。

**请求体:**
```json
{
  "id": "group-uuid"
}
```

## CDP 端点

### HTTP 端点

每个浏览器开放以下 HTTP 端点：

| 端点 | 说明 |
|------|------|
| `GET http://127.0.0.1:{port}/json` | 获取所有 targets |
| `GET http://127.0.0.1:{port}/json/list` | 同上 |
| `GET http://127.0.0.1:{port}/json/version` | 获取版本信息 |
| `GET http://127.0.0.1:{port}/json/protocol` | 获取协议定义 |

### Targets 响应示例

```json
[
  {
    "description": "",
    "devtoolsFrontendUrl": "...",
    "id": "target-id",
    "title": "页面标题",
    "type": "page",
    "url": "https://example.com",
    "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/page/target-id",
    "parentId": null
  }
]
```

### Target 类型

| 类型 | 说明 |
|------|------|
| `page` | 普通网页 |
| `background_page` | 扩展后台页面 |
| `service_worker` | Service Worker |
| `browser` | 浏览器级别 |
| `webview` | WebView |
| `iframe` | 嵌入式框架 |

### WebSocket 连接

连接到 `webSocketDebuggerUrl` 后，可发送 CDP 命令：

```json
{
  "id": 1,
  "method": "Page.navigate",
  "params": {
    "url": "https://example.com"
  }
}
```

## 常用 CDP 命令

### Page 域

```javascript
// 导航
{"id": 1, "method": "Page.navigate", "params": {"url": "https://example.com"}}

// 刷新
{"id": 2, "method": "Page.reload", "params": {}}

// 截图
{"id": 3, "method": "Page.captureScreenshot", "params": {"format": "png"}}

// 获取文档
{"id": 4, "method": "Page.getDocument", "params": {}}
```

### Runtime 域

```javascript
// 执行 JavaScript
{"id": 5, "method": "Runtime.evaluate", "params": {
  "expression": "document.title",
  "returnByValue": true
}}

// 调用函数
{"id": 6, "method": "Runtime.callFunctionOn", "params": {
  "functionDeclaration": "function() { return this.textContent; }",
  "objectId": "object-id"
}}
```

### Input 域

```javascript
// 鼠标点击
{"id": 7, "method": "Input.dispatchMouseEvent", "params": {
  "type": "click",
  "x": 100,
  "y": 200,
  "button": "left",
  "clickCount": 1
}}

// 键盘输入
{"id": 8, "method": "Input.dispatchKeyEvent", "params": {
  "type": "keyDown",
  "text": "a"
}}

// 插入文本
{"id": 9, "method": "Input.insertText", "params": {
  "text": "hello"
}}
```

### Network 域

```javascript
// 启用网络监控
{"id": 10, "method": "Network.enable", "params": {}}

// 获取 Cookie
{"id": 11, "method": "Network.getCookies", "params": {"urls": ["https://example.com"]}}

// 设置 Cookie
{"id": 12, "method": "Network.setCookie", "params": {
  "name": "session",
  "value": "abc123",
  "domain": ".example.com"
}}
```

### DOM 域

```javascript
// 获取文档
{"id": 13, "method": "DOM.getDocument", "params": {}}

// 查询选择器
{"id": 14, "method": "DOM.querySelector", "params": {
  "nodeId": 1,
  "selector": "#username"
}}

// 获取外部 HTML
{"id": 15, "method": "DOM.getOuterHTML", "params": {"nodeId": 2}}
```

## 错误处理

### HTTP API 错误

```json
{
  "success": false,
  "msg": "错误信息"
}
```

### CDP 错误

```json
{
  "id": 1,
  "error": {
    "code": -32000,
    "message": "错误信息"
  }
}
```

## cURL 示例

### 获取浏览器列表

```bash
curl -X POST http://127.0.0.1:54381/browser/list \
  -H "Content-Type: application/json" \
  -d '{"page": 0, "pageSize": 100}'
```

### 打开浏览器

```bash
curl -X POST http://127.0.0.1:54381/browser/open \
  -H "Content-Type: application/json" \
  -d '{"id": "your-profile-id"}'
```

### 获取 CDP 端口

```bash
curl -X POST http://127.0.0.1:54381/browser/ports
```

### 直接访问 CDP

```bash
# 获取 targets
curl http://127.0.0.1:9222/json

# 获取版本
curl http://127.0.0.1:9222/json/version
```

### 代理管理

```bash
# 获取代理列表
curl -X POST http://127.0.0.1:54381/proxy/list

# 创建自定义代理
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

# 创建 API 提取代理
curl -X POST http://127.0.0.1:54381/proxy/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "动态代理",
    "type": "SOCKS5",
    "host": "https://api.proxy.com/get?key=xxx",
    "port": "0"
  }'

# 检测代理
curl -X POST http://127.0.0.1:54381/proxy/check \
  -H "Content-Type: application/json" \
  -d '{"id": "p1"}'

# 删除代理
curl -X POST http://127.0.0.1:54381/proxy/delete \
  -H "Content-Type: application/json" \
  -d '{"id": "p1"}'
```
