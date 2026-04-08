# setup

## 目标

把 `doubao-web-to-api` 在 `Windows` 和 `macOS` 上接通。

## 一、安装依赖

先保证本机有 Python 和 Playwright：

```bash
python3 -m pip install playwright
```

Windows：

```powershell
python -m pip install playwright
```

## 二、打开专用浏览器

macOS：

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py open
```

Windows：

```powershell
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py open
```

默认会：

- 启动 `Chrome / Edge / Chromium`
- 打开远程调试端口 `9231`
- 使用专用配置目录 `~/.doubao-web-to-api/browser-profile`
- 进入豆包聊天页

## 三、登录豆包

在刚打开的浏览器窗口里手动登录一次豆包。

后面再次使用时，会继续复用这套浏览器配置，不用重复登录。

## 四、基本验收

按这个顺序验：

1. `open`
2. `login-check`
3. `new`
4. `ask`
5. `read`

macOS：

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py login-check
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py new
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "你好，请只回复：已连接" --mode quick
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py read
```

Windows：

```powershell
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py login-check
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py new
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "你好，请只回复：已连接" --mode quick
python skills/doubao-web-to-api/scripts/doubao_web_to_api.py read
```

## 五、常见问题

### 1. `open` 提示找不到浏览器

手动指定：

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py open --browser-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

### 2. `login-check` 提示 `cdp_not_available`

说明浏览器调试端口没连上。  
先重新执行：

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py open
```

### 3. `login-check` 提示未登录

说明当前专用浏览器配置还没有豆包登录态。  
在 `open` 打开的窗口里登录一次。

### 4. `ask` 超时

先把超时调大：

```bash
python3 skills/doubao-web-to-api/scripts/doubao_web_to_api.py ask "问题" --mode thinking --timeout 300
```

### 5. 出现验证码或风控

直接人工处理，不要继续自动化。
