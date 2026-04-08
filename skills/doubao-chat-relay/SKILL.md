---
name: doubao-chat-relay
description: "Use when OpenClaw needs to talk to Doubao through OpenCLI on Windows or macOS. Supports login-check, new, ask, read, and reset. Best for internal text chat workflows, not for high-stability production APIs."
---

# doubao-chat-relay

作者：**小马AI**

这个 skill 的作用是：  
让 OpenClaw 通过 OpenCLI 调用豆包，而不是直接接豆包官方 API。

适合：
- 要让 OpenClaw 和豆包对话
- 要复用已经登录好的豆包网页或豆包桌面版
- 要兼容 `Windows` 和 `macOS`

不适合：
- 高并发批量调用
- 强依赖稳定接口的生产链路
- 需要自动绕过验证码、风控或登录校验

## 第一版能力

当前只支持文本问答：
- `login-check`
- `new`
- `ask`
- `read`
- `reset`

当前不做：
- 文件上传
- 图片理解
- 多会话管理
- 自动登录

## 依赖

必须满足：
- 已安装 `opencli`
- 已接通 `opencli doubao` 或 `opencli doubao-app`
- 豆包已手动登录
- 本机可运行 `python3`（Windows 可用 `python`）

如果还没准备好，先看：
- [setup.md](references/setup.md)

## 命令

### macOS

```bash
python3 skills/doubao-chat-relay/scripts/doubao_relay.py login-check
python3 skills/doubao-chat-relay/scripts/doubao_relay.py new
python3 skills/doubao-chat-relay/scripts/doubao_relay.py ask "帮我总结这段内容"
python3 skills/doubao-chat-relay/scripts/doubao_relay.py read
python3 skills/doubao-chat-relay/scripts/doubao_relay.py reset
```

### Windows

```powershell
python skills/doubao-chat-relay/scripts/doubao_relay.py login-check
python skills/doubao-chat-relay/scripts/doubao_relay.py new
python skills/doubao-chat-relay/scripts/doubao_relay.py ask "帮我总结这段内容"
python skills/doubao-chat-relay/scripts/doubao_relay.py read
python skills/doubao-chat-relay/scripts/doubao_relay.py reset
```

## 参数

- `--adapter auto|web|app`
  - `auto`：先试网页版，再试桌面版
  - `web`：只用 `opencli doubao`
  - `app`：只用 `opencli doubao-app`

- `--timeout`
  - 默认 `180` 秒
  - 长回答可以调大

示例：

```bash
python3 skills/doubao-chat-relay/scripts/doubao_relay.py ask "分析这段文案" --adapter web --timeout 300
```

## 输出

所有命令统一输出 JSON。

成功示例：

```json
{
  "ok": true,
  "adapter": "web",
  "adapter_kind": "web",
  "action": "ask",
  "result": {},
  "answer": "这里是豆包回复",
  "command": ["opencli", "doubao", "ask", "问题", "-f", "json"]
}
```

失败示例：

```json
{
  "ok": false,
  "error": "opencli_not_found",
  "message": "未找到 opencli，请先安装并加入 PATH。",
  "action": "login-check"
}
```

## 调用逻辑

默认 `auto` 模式下：
1. 先试网页版
2. 网页版失败再试桌面版
3. 哪个成功，就记住上一次可用适配器
4. 下次优先复用上一次成功的适配器

状态文件位置：
- `~/.openclaw/state/doubao-chat-relay.json`

## 什么时候该停下

遇到这些情况，不要继续自动化：
- 豆包没登录
- 出现验证码
- 出现风控页
- 页面结构明显变化
- OpenCLI 适配器失效

这时应直接提示人工处理。

## 维护入口

后续维护优先看：
- [setup.md](references/setup.md)
- [maintenance.md](references/maintenance.md)
