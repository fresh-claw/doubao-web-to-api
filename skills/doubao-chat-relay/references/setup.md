# setup

## 目标

把 `doubao-chat-relay` 在 `Windows` 和 `macOS` 上接通。

## 一、安装 OpenCLI

```bash
npm install -g @jackwener/opencli
```

验证：

```bash
opencli list
```

如果这一步失败，后面都不用继续。

## 二、优先接网页版

优先原因：
- 更简单
- 不需要桌面版远程调试
- 更接近日常使用方式

### 步骤

1. 安装 OpenCLI 官方 Browser Bridge 扩展
2. 在浏览器里打开豆包网页
3. 手动登录豆包
4. 执行：

```bash
opencli doubao status -f json
```

如果返回成功，再执行：

```bash
python3 skills/doubao-chat-relay/scripts/doubao_relay.py login-check
```

Windows 则用：

```powershell
python skills/doubao-chat-relay/scripts/doubao_relay.py login-check
```

## 三、网页版不稳时改用桌面版

### macOS

```bash
/Applications/Doubao.app/Contents/MacOS/Doubao --remote-debugging-port=9225
export OPENCLI_CDP_ENDPOINT="http://127.0.0.1:9225"
opencli doubao-app status -f json
```

### Windows

```powershell
start "" "C:\Path\To\Doubao.exe" --remote-debugging-port=9225
set OPENCLI_CDP_ENDPOINT=http://127.0.0.1:9225
opencli doubao-app status -f json
```

把 `C:\Path\To\Doubao.exe` 换成实际路径。

## 四、基本验收

按这个顺序验：

1. `opencli list`
2. `opencli doubao status -f json` 或 `opencli doubao-app status -f json`
3. `python3 ... login-check`
4. `python3 ... new`
5. `python3 ... ask "你好"`
6. `python3 ... read`

只要第 5 步和第 6 步能正常拿到回复，这个 skill 就算接通。

## 五、常见问题

### 1. `opencli` 不存在

说明：
- 没安装
- 或 PATH 没生效

先执行：

```bash
opencli list
```

### 2. 网页版 `status` 失败

优先检查：
- 扩展有没有连上
- 豆包是不是当前浏览器里登录的
- 浏览器 profile 对不对

### 3. 桌面版 `status` 失败

优先检查：
- 有没有带 `--remote-debugging-port`
- `OPENCLI_CDP_ENDPOINT` 是否正确
- 豆包桌面版是否真的启动了调试端口

### 4. `ask` 超时

加长超时：

```bash
python3 skills/doubao-chat-relay/scripts/doubao_relay.py ask "问题" --timeout 300
```

### 5. 出现验证码或风控

直接人工处理，不要继续自动化。

