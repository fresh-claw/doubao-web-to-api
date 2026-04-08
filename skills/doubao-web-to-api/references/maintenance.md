# maintenance

## 一、现在依赖什么

这版依赖 3 层：

1. `doubao_web_to_api.py`
2. 浏览器远程调试端口
3. 豆包网页自身结构

## 二、排查顺序

### 第一步：看浏览器调试端口在不在

默认端口是 `9231`。

```bash
curl -s http://127.0.0.1:9231/json/version
```

如果这一步失败，先执行：

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py open
```

### 第二步：看登录态在不在

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py login-check
```

如果这里失败，优先处理登录。

### 第三步：看问答链路通不通

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py new
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "你好，请只回复：已连接" --mode quick
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py read
```

## 三、最容易坏的地方

### 1. 输入框选择器变了

现在依赖：

- `textarea[placeholder="发消息..."]`

如果豆包改版，优先看这里。

### 2. 新对话按钮变了

现在依赖：

- `[data-testid="create_conversation_button"]`

### 3. 模式切换按钮变了

现在依赖：

- `[data-testid="mode-select-action-button"]`
- `[data-testid="deep-thinking-action-item-0"]`
- `[data-testid="deep-thinking-action-item-1"]`
- `[data-testid="deep-thinking-action-item-3"]`

### 4. 消息列表结构变了

现在依赖：

- `[data-testid="message-list"]`
- `[data-testid="send_message"]`
- `[data-testid="receive_message"]`

如果能发不能读，优先看这几项。

## 四、状态文件

状态文件：

- `~/.doubao-web-to-api/state.json`

主要记录：

- `cdp_endpoint`
- `browser_path`
- `profile_dir`
- `start_url`
- `last_mode`

如果怀疑记录错了，可以删掉后重试。

## 五、推荐自检

每次改完至少跑：

```bash
python3 -m py_compile skills/doubao-web-to-api/scripts/doubao_web_to_api.py
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py login-check
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py new
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "你好，请只回复：Q1" --mode quick
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "你好，请只回复：T1" --mode thinking
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py read
```

## 六、后续扩展

下一阶段适合加：

- 文件上传
- 历史会话切换
- 会话标题读取
- 图片理解

但顺序建议是：

1. 先稳定文本对话
2. 再加历史会话
3. 最后再做文件和图片
