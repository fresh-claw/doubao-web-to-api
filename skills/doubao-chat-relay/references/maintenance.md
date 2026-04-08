# maintenance

## 一、这个 skill 现在依赖什么

它依赖 3 层：

1. `doubao_relay.py`
2. `opencli doubao` 或 `opencli doubao-app`
3. 豆包网页或桌面版自身页面结构

所以出问题时，要先判断是哪一层坏了。

## 二、排查顺序

### 第一步：看 OpenCLI 在不在

```bash
opencli list
```

如果这一步失败，先修 OpenCLI，不要看脚本。

### 第二步：看适配器在不在

网页版：

```bash
opencli doubao status -f json
```

桌面版：

```bash
opencli doubao-app status -f json
```

如果这里失败，说明是 OpenCLI 和豆包连接层的问题。

### 第三步：看 skill 脚本是不是好的

```bash
python3 skills/doubao-chat-relay/scripts/doubao_relay.py login-check
python3 skills/doubao-chat-relay/scripts/doubao_relay.py ask "你好"
```

如果 OpenCLI 本身正常，但脚本报错，再修脚本。

## 三、最容易坏的地方

### 1. OpenCLI 命令变了

如果 OpenCLI 后续改了命令格式，要改：
- `scripts/doubao_relay.py`

重点看这里：
- `ADAPTERS`
- `build_cmd()`
- `ACTION_ALIASES`

### 2. 豆包适配器返回 JSON 结构变了

如果还能返回，但拿不到正文，要改：
- `parse_jsonish()`
- `flatten_text()`
- `guess_answer()`

### 3. 网页版不稳定

做法：
- 先改用 `--adapter app`
- 如果桌面版更稳，就把默认逻辑改成先试 `app`

### 4. 本地状态文件脏了

状态文件：
- `~/.openclaw/state/doubao-chat-relay.json`

如果怀疑记录错了，可以删掉后重试。

## 四、推荐维护动作

每次改完后，至少跑这 5 条：

```bash
python3 -m py_compile skills/doubao-chat-relay/scripts/doubao_relay.py
python3 skills/doubao-chat-relay/scripts/doubao_relay.py login-check
python3 skills/doubao-chat-relay/scripts/doubao_relay.py new
python3 skills/doubao-chat-relay/scripts/doubao_relay.py ask "你好"
python3 skills/doubao-chat-relay/scripts/doubao_relay.py read
```

## 五、后续扩展建议

下一阶段可以加：
- `history`
- `last`
- `raw`
- `ask --system`
- `ask-file`

但建议顺序是：
1. 先把文本问答稳定住
2. 再加历史
3. 最后再碰文件上传

## 六、加新 skill 时怎么管目录

未来新增 skill，按这一套：

```text
skills/<skill-name>/
├── SKILL.md
├── scripts/
└── references/
```

并且同步更新：
- `skills/catalog.json`
- 仓库首页 `README.md`

