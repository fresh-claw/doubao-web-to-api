---
name: doubao-web-to-api
description: "Use when Codex or another local agent needs to control an already logged-in Doubao web chat on Windows or macOS. Exposes Doubao Web as a JSON-returning command interface with open, login-check, new, ask, read, last, and reset, using Playwright over Chrome DevTools."
---

# doubao-web-to-api

通过 Playwright 直控已登录的豆包网页，把对话能力封成统一的命令接口，让本机 Agent 可以直接发起文本问答、切换模式并读取回复。

适合：
- 本机已登录豆包
- 需要兼容 `Windows` 和 `macOS`
- 希望以命令行方式发起问答并读取回复
- 接受首次登录一次，后续复用专用浏览器配置

当前范围：
- `open`
- `login-check`
- `new`
- `ask`
- `read`
- `last`
- `reset`

第一版只做文本问答，不处理文件上传、图片理解和复杂会话管理。

## 依赖

必须满足：
- 已安装 `playwright`
- 已有可用的 Chrome、Edge 或 Chromium
- 浏览器允许使用远程调试端口
- 豆包已在专用浏览器配置里登录
- 本机可运行 `python3`（Windows 可用 `python`）

如果还没准备好，先看：
- [setup.md](references/setup.md)

## 命令

### macOS

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py open
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py login-check
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py new
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "帮我总结这段内容"
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py read
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py last
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py reset
```

### Windows

```powershell
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py open
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py login-check
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py new
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "帮我总结这段内容"
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py read
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py last
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py reset
```

## 参数

- `--mode quick|thinking|expert`
  - 只对 `ask` 生效
  - 会把豆包切到对应模式后再提问

- `--cdp-endpoint`
  - 默认 `http://127.0.0.1:9231`
  - 指向当前浏览器调试端口

- `--browser-path`
  - 用于 `open`
  - 不传则自动查找 Chrome、Edge 或 Chromium

- `--profile-dir`
  - 用于 `open`
  - 默认 `~/.doubao-web-to-api/browser-profile`

- `--timeout`
  - 默认 `180` 秒
  - `ask` 等待豆包回复的上限时间

示例：

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "分析这段文案" --mode thinking --timeout 300
```

## 输出

所有命令统一输出 JSON。

成功示例：

```json
{
  "ok": true,
  "action": "ask",
  "question": "问题",
  "answer": "这里是豆包回复",
  "current_mode": "思考",
  "url": "https://www.doubao.com/chat/123"
}
```

失败示例：

```json
{
  "ok": false,
  "error": "not_logged_in",
  "message": "豆包网页未登录，请先在浏览器里完成登录。",
  "action": "login-check"
}
```

## 调用逻辑

1. 通过 CDP 连接到当前浏览器
2. 找到豆包对话页
3. `ask` 时可先切模式
4. 写入问题并等待新回复稳定
5. 返回最新回复文本

状态文件位置：
- `~/.doubao-web-to-api/state.json`

## 什么时候该停下

遇到这些情况，不要继续自动化：
- 浏览器调试端口没开
- 豆包没登录
- 出现验证码
- 出现风控页
- 页面结构明显变化

这时应直接停止，并提示人工处理。

## 维护入口

后续维护优先看：
- [setup.md](references/setup.md)
- [maintenance.md](references/maintenance.md)
