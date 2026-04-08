# Doubao Web 2 API

作者：**小马AI**

把已登录的豆包网页版变成统一的命令接口，方便本机 Agent 直接发起对话、创建新会话、切换模式、读取最新回复。

适合：
- 已接受首次登录一次，后续直接复用
- 想让能执行本地命令的 Agent 直接调用豆包
- 需要同时兼容 `Windows` 和 `macOS`

不适合：
- 高并发批量任务
- 强依赖稳定接口的生产链路
- 自动绕过验证码、风控或登录限制

## 能做什么

- 打开专用浏览器并进入豆包
- 检查豆包是否已登录并可调用
- 新建会话
- 切换 `快速 / 思考 / 专家`
- 发送问题并读取完整回复
- 统一输出 JSON，方便继续封装

这版主链路不是 `opencli`，而是 `Playwright + Chrome DevTools` 直控当前豆包页面。

## 当前支持

- `open`
- `login-check`
- `new`
- `ask`
- `read`
- `last`
- `reset`

第一版只做文本问答，不包含文件上传、图片理解和复杂会话管理。

## 运行前准备

必须满足这 4 个条件：

1. 已安装 `playwright`
2. 本机有 `Chrome / Edge / Chromium`
3. 豆包会在专用浏览器配置里登录一次
4. 本机可运行 Python

详细安装步骤见：

- [安装与接通](skills/doubao-web-to-api/references/setup.md)

## 快速开始

### macOS

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py open
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py login-check
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py new
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "帮我总结这段内容" --mode quick
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "帮我分析这个问题" --mode thinking
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py read
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py last
```

### Windows

```powershell
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py open
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py login-check
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py new
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "帮我总结这段内容" --mode quick
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "帮我分析这个问题" --mode thinking
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py read
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py last
```

## 参数说明

### `--mode`

- `quick`：快速
- `thinking`：思考
- `expert`：专家

只对 `ask` 生效。

### `--cdp-endpoint`

默认值：`http://127.0.0.1:9231`

### `--profile-dir`

默认值：`~/.doubao-web-to-api/browser-profile`

### `--browser-path`

只对 `open` 生效。  
不传会自动查找本机浏览器。

### `--timeout`

等待超时时间，默认 `180` 秒。  
如果问题长、回复慢，可以调大。

示例：

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "分析这段文案" --mode thinking --timeout 300
```

## 返回结果

所有命令统一返回 JSON。

成功示例：

```json
{
  "ok": true,
  "action": "ask",
  "question": "分析这段文案",
  "answer": "这里是豆包回复",
  "current_mode": "思考",
  "url": "https://www.doubao.com/chat/123"
}
```

失败示例：

```json
{
  "ok": false,
  "error": "cdp_not_available",
  "message": "未连接到浏览器调试端口，请先执行 open。",
  "action": "login-check"
}
```

## 工作方式

默认会复用 `~/.doubao-web-to-api/browser-profile` 这套浏览器配置。  
登录一次后，后续直接连到浏览器调试端口，不再重复登录。

状态文件位置：

- `~/.doubao-web-to-api/state.json`

## 常见问题

### 1. `login-check` 提示 `cdp_not_available`

先执行：

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py open
```

### 2. 提示未登录

说明这套专用浏览器配置还没有登录豆包。  
在 `open` 打开的窗口里登录一次即可。

### 3. `ask` 超时

把超时调大：

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "问题" --mode thinking --timeout 300
```

### 4. 出现验证码或风控

不要继续自动化，直接人工处理。

## 仓库内容

```text
doubao-web-to-api/
├── README.md
└── skills/
    ├── catalog.json
    └── doubao-web-to-api/
        ├── SKILL.md
        ├── scripts/
        │   └── doubao_web_to_api.py
        └── references/
            ├── setup.md
            └── maintenance.md
```

## 相关文件

- [SKILL.md](skills/doubao-web-to-api/SKILL.md)
- [安装与接通](skills/doubao-web-to-api/references/setup.md)
- [维护说明](skills/doubao-web-to-api/references/maintenance.md)
- [Skill 清单](skills/catalog.json)

## 后续新增 Skill

后续会继续按同样方式管理新的 skill。  
每个 skill 单独放在 `skills/<skill-name>/`，并统一写安装、使用、维护文档。
