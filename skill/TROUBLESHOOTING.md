# CDP 自动化故障排除指南

## 常见问题分类

1. [连接问题](#连接问题)
2. [浏览器问题](#浏览器问题)
3. [元素操作问题](#元素操作问题)
4. [批量操作问题](#批量操作问题)
5. [性能问题](#性能问题)

---

## 连接问题

### 问题：无法连接到 Cloak API

**症状：**
```
curl: (7) Failed to connect to 127.0.0.1 port 54381
```

**可能原因：**
1. Cloak 客户端未运行
2. 端口被其他程序占用
3. 防火墙阻止连接

**解决方案：**

```bash
# 1. 检查 Cloak 是否运行
tasklist | findstr cloak

# 2. 检查端口是否被监听
netstat -ano | findstr 54381

# 3. 如果端口被占用，找到并结束占用进程
netstat -ano | findstr 54381
taskkill /PID <占用进程PID> /F
```

### 问题：无法连接到 CDP 端口

**症状：**
```
curl: (7) Failed to connect to 127.0.0.1 port 9222
```

**可能原因：**
1. 浏览器未启动或已崩溃
2. CDP 端口分配错误
3. 浏览器进程僵死

**解决方案：**

```bash
# 1. 检查浏览器进程
curl -X POST http://127.0.0.1:54381/browser/pids/all

# 2. 检查端口映射
curl -X POST http://127.0.0.1:54381/browser/ports

# 3. 如果进程存在但无法连接，重启浏览器
curl -X POST http://127.0.0.1:54381/browser/close \
  -H "Content-Type: application/json" \
  -d '{"id": "profile-uuid"}'

curl -X POST http://127.0.0.1:54381/browser/open \
  -H "Content-Type: application/json" \
  -d '{"id": "profile-uuid"}'
```

### 问题：WebSocket 连接断开

**症状：**
- CDP 命令无响应
- 连接突然断开

**可能原因：**
1. 浏览器页面跳转
2. 浏览器崩溃
3. 网络问题

**解决方案：**
1. 实现心跳检测
2. 添加重连机制
3. 捕获断开事件并处理

```javascript
// 心跳检测示例
setInterval(() => {
  ws.send(JSON.stringify({ id: Date.now(), method: "Page.getResourceTree", params: {} }));
}, 30000);
```

---

## 浏览器问题

### 问题：浏览器启动失败

**症状：**
```json
{
  "success": false,
  "msg": "启动浏览器失败"
}
```

**可能原因：**
1. FBroSharp 内核未下载
2. 配置文件损坏
3. 缓存冲突
4. 系统资源不足

**解决方案：**

```bash
# 1. 检查内核是否存在
dir "%AppData%\com.cloak.browser\fbro\fbro.exe"

# 2. 检查内核版本
"%AppData%\com.cloak.browser\fbro\fbro.exe" --version

# 3. 清理缓存重新下载（需要重启 Cloak）
rmdir /s /q "%AppData%\com.cloak.browser\fbro"
```

### 问题：浏览器打开后立即关闭

**可能原因：**
1. 指纹配置错误
2. 代理配置错误
3. 扩展冲突

**解决方案：**

```bash
# 1. 检查浏览器详情
curl -X POST http://127.0.0.1:54381/browser/detail \
  -H "Content-Type: application/json" \
  -d '{"id": "profile-uuid"}'

# 2. 尝试禁用代理
curl -X POST http://127.0.0.1:54381/browser/update \
  -H "Content-Type: application/json" \
  -d '{"id": "profile-uuid", "proxy": ""}'

# 3. 重新打开浏览器
```

### 问题：浏览器无响应

**症状：**
- 页面不加载
- CDP 命令超时

**解决方案：**

```bash
# 1. 检查进程是否存在
curl -X POST http://127.0.0.1:54381/browser/pids/all

# 2. 强制关闭并重启
curl -X POST http://127.0.0.1:54381/browser/close \
  -H "Content-Type: application/json" \
  -d '{"id": "profile-uuid"}'
```

---

## 元素操作问题

### 问题：元素找不到

**症状：**
```
Error: Element not found
```

**可能原因：**
1. 页面未加载完成
2. 选择器错误
3. 元素在 iframe 中
4. 元素动态生成

**解决方案：**

```
1. 使用 wait_for 等待元素
2. 先获取 snapshot 确认元素存在
3. 检查是否需要切换 iframe
4. 增加重试机制
```

**示例：**

```javascript
// 等待元素出现后再操作
mcp__chrome-devtools__wait_for(text="按钮文字", timeout=10000)
mcp__chrome-devtools__take_snapshot()  // 获取最新 uid
mcp__chrome-devtools__click(uid="正确的uid")
```

### 问题：点击无效果

**可能原因：**
1. 元素被遮挡
2. 事件被阻止
3. 需要滚动到元素

**解决方案：**

```javascript
// 使用 JavaScript 点击
mcp__chrome-devtools__evaluate_script(
  function="(uid) => { document.querySelector('selector').scrollIntoView(); document.querySelector('selector').click(); }"
)
```

### 问题：输入内容丢失

**可能原因：**
1. 使用了 React/Vue 等框架
2. 输入事件未触发

**解决方案：**

```javascript
// 触发完整的输入事件链
const input = document.querySelector('input');
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
nativeInputValueSetter.call(input, '新值');
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));
```

### 问题：iframe 内元素无法操作

**解决方案：**

```javascript
// 1. 获取 iframe 的 target
const targets = await fetch('http://127.0.0.1:9222/json').then(r => r.json());
const iframeTarget = targets.find(t => t.parentId);  // 有 parentId 的是 iframe

// 2. 连接到 iframe 的 WebSocket
const ws = new WebSocket(iframeTarget.webSocketDebuggerUrl);

// 3. 在 iframe 中执行操作
```

---

## 批量操作问题

### 问题：批量操作部分失败

**症状：**
- 部分浏览器操作成功，部分失败

**解决方案：**

1. **记录失败项**
```javascript
const results = [];
for (const browser of browsers) {
  try {
    await operate(browser);
    results.push({ id: browser.id, success: true });
  } catch (error) {
    results.push({ id: browser.id, success: false, error: error.message });
  }
}
```

2. **重试失败项**
```javascript
const failed = results.filter(r => !r.success);
for (const item of failed) {
  await retry(item.id);
}
```

3. **生成详细报告**
```javascript
console.log('执行报告:');
console.log(`- 成功: ${results.filter(r => r.success).length}`);
console.log(`- 失败: ${failed.length}`);
failed.forEach(f => console.log(`  - ${f.id}: ${f.error}`));
```

### 问题：批量操作太慢

**解决方案：**

1. **并行执行**
```javascript
await Promise.all(browsers.map(b => operate(b)));
```

2. **限制并发数**
```javascript
const limit = 5;  // 最多同时 5 个
const chunks = [];
for (let i = 0; i < browsers.length; i += limit) {
  chunks.push(browsers.slice(i, i + limit));
}

for (const chunk of chunks) {
  await Promise.all(chunk.map(b => operate(b)));
}
```

### 问题：批量操作触发反爬

**解决方案：**

1. **添加随机延迟**
```javascript
const delay = Math.random() * 2000 + 1000;  // 1-3 秒随机延迟
await new Promise(r => setTimeout(r, delay));
```

2. **分批执行**
```javascript
const batchSize = 5;
const batchDelay = 30000;  // 每批间隔 30 秒
```

3. **模拟人类行为**
```javascript
// 随机移动鼠标
// 随机滚动页面
// 随机停顿
```

---

## 性能问题

### 问题：CDP 命令响应慢

**可能原因：**
1. 页面内容过多
2. 网络延迟
3. 浏览器资源占用高

**解决方案：**

1. **增加超时时间**
```javascript
// 默认 30 秒，可增加到 60 秒
const timeout = 60000;
```

2. **优化页面**
```javascript
// 禁用图片加载
// 阻止不必要的请求
```

3. **减少并发**
```javascript
// 降低同时操作的浏览器数量
```

### 问题：内存占用过高

**解决方案：**

1. **及时关闭连接**
```javascript
// 操作完成后关闭 WebSocket
ws.close();
```

2. **定期重启浏览器**
```bash
# 每隔一段时间重启浏览器
curl -X POST http://127.0.0.1:54381/browser/close
curl -X POST http://127.0.0.1:54381/browser/open
```

3. **清理缓存**
```javascript
// 清理浏览器缓存
await sendCommand('Network.clearBrowserCache');
await sendCommand('Network.clearBrowserCookies');
```

---

## 调试技巧

### 1. 启用详细日志

```bash
# 查看 Cloak 日志
type "%AppData%\com.cloak.browser\logs\cloak.log"
```

### 2. 使用 Chrome DevTools

```
1. 打开 chrome://inspect
2. 配置 localhost:9222
3. 点击 inspect 查看远程调试
```

### 3. 检查 CDP 通信

```javascript
// 记录所有 CDP 消息
ws.onmessage = (event) => {
  console.log('CDP Response:', event.data);
};
```

### 4. 验证 API 响应

```bash
# 使用 jq 格式化 JSON
curl -s -X POST http://127.0.0.1:54381/browser/list | jq
```

---

## 常见错误代码

| 错误代码 | 说明 | 解决方案 |
|----------|------|----------|
| `-32000` | 通用 CDP 错误 | 检查命令参数 |
| `-32600` | 无效请求 | 检查 JSON 格式 |
| `-32601` | 方法不存在 | 检查方法名拼写 |
| `-32602` | 无效参数 | 检查参数类型 |
| `-32603` | 内部错误 | 检查浏览器状态 |

---

## 获取帮助

如果以上方法都无法解决问题：

1. 查看项目 README.md
2. 查看项目 CLAUDE.md
3. 检查 Cloak 客户端是否有更新
4. 联系技术支持
