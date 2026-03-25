# CDP 自动化工作流程示例

## 工作流程 1：检查并操作单个浏览器

### 场景
用户想对某个特定的浏览器窗口执行自动化操作。

### 步骤

1. **检查 Cloak 服务状态**
   ```bash
   curl http://127.0.0.1:54381/health
   ```
   （亦支持 `POST /health`，返回 JSON。）

2. **获取浏览器列表，找到目标浏览器**
   ```bash
   curl -X POST http://127.0.0.1:54381/browser/list
   ```

3. **如果浏览器未运行，先打开**
   ```bash
   curl -X POST http://127.0.0.1:54381/browser/open \
     -H "Content-Type: application/json" \
     -d '{"id": "profile-uuid"}'
   ```

4. **获取 CDP 端口**
   ```bash
   curl -X POST http://127.0.0.1:54381/browser/ports
   # 记录对应的 debugPort
   ```

5. **使用 MCP 工具操作浏览器**
   ```
   # 加载 Chrome DevTools MCP 工具
   ToolSearch query="chrome-devtools"

   # 导航到目标页面
   mcp__chrome-devtools__navigate_page(type="url", url="https://example.com")

   # 获取页面快照
   mcp__chrome-devtools__take_snapshot()

   # 根据快照中的 uid 进行操作
   mcp__chrome-devtools__click(uid="element-uid")
   ```

### 示例对话

```
用户: 帮我检查当前有哪些浏览器在运行

助手:
我来检查 Cloak 的浏览器状态...

[调用 /browser/ports API]

当前有 3 个浏览器正在运行：
1. 账号1 (CDP 端口: 9222)
2. 账号2 (CDP 端口: 9223)
3. 账号3 (CDP 端口: 9224)

请问您想操作哪个浏览器？
```

---

## 工作流程 2：自动登录网站

### 场景
用户想在指定的浏览器中自动登录某个网站。

### 步骤

1. **确认浏览器状态和端口**

2. **导航到登录页面**
   ```
   mcp__chrome-devtools__navigate_page(type="url", url="https://example.com/login")
   ```

3. **等待页面加载**
   ```
   mcp__chrome-devtools__wait_for(text="登录", timeout=5000)
   ```

4. **获取页面快照，找到表单元素**
   ```
   mcp__chrome-devtools__take_snapshot()
   ```

5. **填写登录表单**
   ```
   mcp__chrome-devtools__fill_form(elements=[
     {"uid": "username-input-uid", "value": "my_username"},
     {"uid": "password-input-uid", "value": "my_password"}
   ])
   ```

6. **点击登录按钮**
   ```
   mcp__chrome-devtools__click(uid="login-button-uid")
   ```

7. **等待登录成功**
   ```
   mcp__chrome-devtools__wait_for(text="欢迎", timeout=10000)
   ```

### 示例对话

```
用户: 帮我在账号1的浏览器中登录 example.com，用户名是 test，密码是 123456

助手:
我来帮您自动登录...

首先导航到登录页面...
[调用 navigate_page]

获取页面结构...
[调用 take_snapshot]

找到登录表单元素：
- 用户名输入框: uid "15"
- 密码输入框: uid "16"
- 登录按钮: uid "17"

填写登录信息...
[调用 fill_form]

点击登录按钮...
[调用 click]

等待登录完成...
[调用 wait_for]

登录成功！当前页面显示"欢迎回来"。
```

---

## 工作流程 3：批量打开浏览器并导航

### 场景
用户想让所有浏览器同时打开同一个网页。

### 步骤

1. **获取所有浏览器配置**
   ```bash
   curl -X POST http://127.0.0.1:54381/browser/list
   ```

2. **打开所有未运行的浏览器**
   ```bash
   curl -X POST http://127.0.0.1:54381/browser/open/all
   ```

3. **等待所有浏览器启动**

4. **逐个执行导航**（通过 API 或 CDP）

### 使用 Cloak 内置 AI 接口

本地 HTTP 服务上的路径为 **`/ai/chat`**（开发中前端可能通过 Vite 代理到 `/internal-api/...`，直连后端时请用下面地址）：

```bash
curl -X POST http://127.0.0.1:54381/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "让所有浏览器都打开 https://example.com"
  }'
```

### 示例对话

```
用户: 让所有浏览器都打开百度

助手:
我来执行批量操作...

首先获取所有浏览器列表...
[调用 /browser/list]

发现 5 个浏览器配置，其中 2 个正在运行。

打开未运行的浏览器...
[调用 /browser/open/all]

等待浏览器启动...

获取所有 CDP 端口...
[调用 /browser/ports]

逐个执行导航：
- 账号1 (9222): 导航到百度... ✓
- 账号2 (9223): 导航到百度... ✓
- 账号3 (9224): 导航到百度... ✓
- 账号4 (9225): 导航到百度... ✓
- 账号5 (9226): 导航到百度... ✓

完成！所有 5 个浏览器已打开百度。
```

---

## 工作流程 4：批量截图

### 场景
用户想截取所有浏览器的当前屏幕。

### 步骤

1. **获取运行中的浏览器端口**
   ```bash
   curl -X POST http://127.0.0.1:54381/browser/ports
   ```

2. **对每个端口执行截图**
   - 连接 CDP
   - 调用 `Page.captureScreenshot`
   - 保存图片

### 示例代码（通过 CDP）

```javascript
async function captureAllScreenshots(ports) {
  const results = [];
  for (const [profileId, port] of Object.entries(ports)) {
    try {
      // 获取 targets
      const targets = await fetch(`http://127.0.0.1:${port}/json`).then(r => r.json());

      // 找到 page target
      const pageTarget = targets.find(t => t.type === 'page' && !t.url.startsWith('chrome://'));

      if (!pageTarget) continue;

      // 连接 WebSocket
      const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);

      // 发送截图命令
      const result = await sendCommand(ws, 'Page.captureScreenshot', {});

      // 保存图片
      const buffer = Buffer.from(result.data, 'base64');
      await fs.writeFile(`${profileId}.png`, buffer);

      results.push({ profileId, success: true });
    } catch (error) {
      results.push({ profileId, success: false, error: error.message });
    }
  }
  return results;
}
```

---

## 工作流程 5：批量执行 JavaScript

### 场景
用户想在所有浏览器中执行相同的 JavaScript 代码。

### 使用场景
- 获取所有页面的标题
- 批量填写表单
- 批量点击按钮
- 收集页面数据

### 步骤

1. **获取运行中的浏览器端口**

2. **对每个浏览器执行 JS**

### 示例：获取所有页面标题

```javascript
const js = "document.title";

// 通过 CDP 发送到每个浏览器
```

### 示例对话

```
用户: 帮我获取所有浏览器当前页面的标题

助手:
我来获取所有页面的标题...

[调用 /browser/ports 获取端口列表]
[对每个端口通过 CDP 执行 document.title]

结果：
1. 账号1: "百度一下，你就知道"
2. 账号2: "淘宝网 - 淘！我喜欢"
3. 账号3: "京东(JD.COM)-正品低价"
```

---

## 工作流程 6：数据采集

### 场景
用户想从多个浏览器中采集数据。

### 步骤

1. **准备采集脚本**

2. **在所有浏览器中执行**

3. **收集结果**

### 示例：采集商品信息

```javascript
// 采集脚本
const productInfo = {
  title: document.querySelector('.product-title')?.textContent,
  price: document.querySelector('.price')?.textContent,
  rating: document.querySelector('.rating')?.textContent,
  reviews: document.querySelector('.review-count')?.textContent
};
JSON.stringify(productInfo);
```

### 示例对话

```
用户: 帮我从所有打开的淘宝页面采集商品信息

助手:
我来执行数据采集...

[获取所有浏览器端口]
[逐个执行采集脚本]

采集结果：

浏览器1:
- 商品: iPhone 15 Pro Max
- 价格: ¥9,999
- 评分: 4.9
- 评价数: 12,345

浏览器2:
- 商品: MacBook Pro 14寸
- 价格: ¥14,999
- 评分: 4.8
- 评价数: 8,765

...

已将数据保存到 products.json
```

---

## 工作流程 7：自动化工作流

### 场景
用户想执行一系列连续的自动化操作。

### 步骤定义

```json
{
  "steps": [
    {"action": "navigate", "url": "https://example.com/login"},
    {"action": "wait", "text": "登录"},
    {"action": "fill", "selector": "#username", "value": "user"},
    {"action": "fill", "selector": "#password", "value": "pass"},
    {"action": "click", "selector": "#login-btn"},
    {"action": "wait", "text": "欢迎"},
    {"action": "navigate", "url": "https://example.com/dashboard"},
    {"action": "screenshot", "filename": "dashboard.png"}
  ]
}
```

### 执行流程

```
1. 解析工作流定义
2. 逐步执行每个 action
3. 记录每步结果
4. 出错时决定是否继续
5. 生成执行报告
```

---

## 工作流程 8：创建和配置代理

### 场景
用户想创建代理配置并应用到浏览器。

### 步骤

#### 方式 1：创建自定义代理

1. **创建代理配置**
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

2. **检测代理连通性**
   ```bash
   curl -X POST http://127.0.0.1:54381/proxy/check \
     -H "Content-Type: application/json" \
     -d '{"id": "p1"}'
   ```

3. **将代理池中的代理绑定到档案**（需 `X-Api-Key`，字段名见 Swagger）
   ```bash
   curl -X PUT "http://127.0.0.1:54381/api/v1/profiles/BROWSER_PROFILE_ID" \
     -H "Content-Type: application/json" \
     -H "X-Api-Key: YOUR_API_KEY" \
     -d '{"proxyId": "p1"}'
   ```

#### 方式 2：创建 API 提取代理

```bash
curl -X POST http://127.0.0.1:54381/proxy/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "动态代理",
    "type": "SOCKS5",
    "host": "https://api.proxy.com/get?key=xxx",
    "port": "0",
    "remark": "每次启动自动获取新IP"
  }'
```

**API提取代理特点:**
- host 填写 API 提取链接
- port 固定填 "0" 作为标识
- 每次启动浏览器时自动从 API 获取新的代理 IP
- 适合需要频繁更换 IP 的场景

### 示例对话

```
用户: 帮我创建一个香港的SOCKS5代理，地址是45.12.33.1，端口1080

助手:
我来创建代理配置...

[调用 /proxy/add API]

代理创建成功！
- 名称: 香港代理
- 类型: SOCKS5
- 地址: 45.12.33.1:1080
- ID: p1

正在后台检测代理连通性...

[调用 /proxy/check API]

代理检测完成：
✓ 状态: 有效
✓ 延迟: 123ms
✓ 公网IP: 45.12.33.1
✓ 位置: 中国/香港/香港
✓ ISP: HKT

您现在可以在创建浏览器时使用这个代理了。
```

---

## 工作流程 9：为浏览器设置代理

### 场景
用户想为已存在的浏览器设置或更换代理。

### 步骤

1. **获取代理列表**
   ```bash
   curl -X POST http://127.0.0.1:54381/proxy/list
   ```

2. **获取浏览器列表**
   ```bash
   curl -X POST http://127.0.0.1:54381/browser/list
   ```

3. **更新档案中的代理绑定**（`proxyId` 为代理池中的 ID；需 `X-Api-Key`）
   ```bash
   curl -X PUT "http://127.0.0.1:54381/api/v1/profiles/browser-uuid" \
     -H "Content-Type: application/json" \
     -H "X-Api-Key: YOUR_API_KEY" \
     -d '{"proxyId": "p1"}'
   ```

4. **重启浏览器应用新配置**
   ```bash
   # 关闭浏览器
   curl -X POST http://127.0.0.1:54381/browser/close \
     -H "Content-Type: application/json" \
     -d '{"id": "browser-uuid"}'
   
   # 重新打开
   curl -X POST http://127.0.0.1:54381/browser/open \
     -H "Content-Type: application/json" \
     -d '{"id": "browser-uuid"}'
   ```

### 移除代理

REST 更新时将 `proxyId` 置为 JSON `null` 表示清除绑定（直连），详见 `UpdateProfileRequest` 说明。

```bash
curl -X PUT "http://127.0.0.1:54381/api/v1/profiles/browser-uuid" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -d '{"proxyId": null}'
```

### 示例对话

```
用户: 把"账号1"的代理改成"香港代理"

助手:
我来为浏览器设置代理...

[调用 /browser/list 查找"账号1"]
[调用 /proxy/list 查找"香港代理"]

找到浏览器: 账号1 (ID: xxx-xxx-xxx)
找到代理: 香港代理 (ID: p1, 45.12.33.1:1080)

[调用 PUT /api/v1/profiles/{id} 设置 proxyId]

代理设置成功！

⚠️ 注意: 浏览器"账号1"当前正在运行中。
需要重启浏览器才能应用新的代理配置。

是否现在重启浏览器？
```

---

## 工作流程 10：批量代理管理

### 场景
用户想批量为多个浏览器设置相同的代理。

### 步骤

1. **获取所有浏览器**
   ```bash
   curl -X POST http://127.0.0.1:54381/browser/list
   ```

2. **批量更新代理配置**
   ```bash
   # 对每个 profile 调用 REST（需 X-Api-Key）
   for browser_id in "${browser_ids[@]}"; do
     curl -X PUT "http://127.0.0.1:54381/api/v1/profiles/$browser_id" \
       -H "Content-Type: application/json" \
       -H "X-Api-Key: YOUR_API_KEY" \
       -d '{"proxyId": "p1"}'
   done
   ```

3. **批量重启浏览器**
   ```bash
   # 关闭所有
   curl -X POST http://127.0.0.1:54381/browser/close/all
   
   # 重新打开
   curl -X POST http://127.0.0.1:54381/browser/open/all
   ```

### 示例对话

```
用户: 把所有浏览器都设置成"香港代理"

助手:
我来执行批量代理设置...

[调用 /browser/list 获取所有浏览器]
[调用 /proxy/list 查找"香港代理"]

找到 5 个浏览器配置
找到代理: 香港代理 (ID: p1)

开始批量设置...

✓ 账号1: 代理已设置
✓ 账号2: 代理已设置
✓ 账号3: 代理已设置
✓ 账号4: 代理已设置
✓ 账号5: 代理已设置

批量设置完成！
- 成功: 5 个
- 失败: 0 个

⚠️ 注意: 其中 2 个浏览器正在运行中，需要重启才能应用新配置。

是否批量重启所有浏览器？
```

---

## 工作流程 11：代理检测和监控

### 场景
用户想检测代理的可用性和性能。

### 步骤

1. **检测单个代理**
   ```bash
   curl -X POST http://127.0.0.1:54381/proxy/check \
     -H "Content-Type: application/json" \
     -d '{"id": "p1"}'
   ```

2. **批量检测所有代理**
   ```bash
   # 获取所有代理
   PROXIES=$(curl -s -X POST http://127.0.0.1:54381/proxy/list)
   
   # 逐个检测
   for proxy_id in $(echo $PROXIES | jq -r '.data.list[].id'); do
     curl -X POST http://127.0.0.1:54381/proxy/check \
       -H "Content-Type: application/json" \
       -d "{\"id\": \"$proxy_id\"}"
   done
   ```

### 检测结果解读

```json
{
  "status": "有效",      // 有效/失效
  "delay": 123,         // 延迟（毫秒）
  "ip": "45.12.33.1",   // 公网IP
  "country": "中国",     // 国家
  "region": "香港",      // 地区
  "city": "香港",        // 城市
  "isp": "HKT",         // ISP运营商
  "timezone": "Asia/Hong_Kong"  // 时区
}
```

### 示例对话

```
用户: 检测一下所有代理是否可用

助手:
我来检测所有代理...

[调用 /proxy/list 获取代理列表]

找到 3 个代理配置，开始检测...

1. 香港代理 (45.12.33.1:1080)
   ✓ 状态: 有效
   ✓ 延迟: 123ms
   ✓ 位置: 中国/香港/香港
   ✓ ISP: HKT

2. 美国代理 (23.45.67.89:1080)
   ✗ 状态: 失效
   ✗ 错误: 连接超时

3. 动态代理 (API提取)
   ⚠ 状态: 未检测
   ⚠ 说明: API提取代理需要在启动浏览器时才会获取实际IP

检测完成！
- 有效: 1 个
- 失效: 1 个
- 未检测: 1 个

建议: 删除失效的"美国代理"或更新其配置。
```

---

## 工作流程 12：定时任务

### 场景
用户想定时执行某些操作。

### 实现方式

1. **使用系统定时任务**
   - Windows: Task Scheduler
   - Linux: cron

2. **使用脚本调度**
   ```bash
   # 每小时执行一次检查
   0 * * * * /path/to/script.sh
   ```

3. **通过 Cloak API 控制**

### 示例脚本

```bash
#!/bin/bash
# check_and_report.sh

# 获取浏览器状态
BROWSERS=$(curl -s -X POST http://127.0.0.1:54381/browser/ports)

# 执行检查逻辑
# ...

# 发送报告
# ...
```

---

## 错误处理最佳实践

### 1. 连接失败处理

```
1. 检查 Cloak 是否运行
2. 检查浏览器是否启动
3. 检查端口是否正确
4. 重试机制
```

### 2. 元素找不到处理

```
1. 重新获取页面快照
2. 使用更通用的选择器
3. 增加等待时间
4. 使用 wait_for 确保元素就绪
```

### 3. 操作超时处理

```
1. 增加超时时间
2. 检查网络状况
3. 检查页面是否有弹窗
4. 处理可能的对话框
```

### 4. 批量操作失败处理

```
1. 记录失败的浏览器
2. 单独重试失败的浏览器
3. 生成详细的执行报告
4. 支持断点续传
```
