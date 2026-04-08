# 小马AI Skills

这是一个按 skill 方式组织的仓库。

作者：**小马AI**

目标：
- 统一管理可复用的 skill
- 每个 skill 独立放在 `skills/<skill-name>/`
- 让后续新增 skill 时，目录、说明、维护方式都保持一致

## 目录结构

```text
xiaomai-ai-skills/
├── README.md
├── .gitignore
└── skills/
    ├── catalog.json
    └── doubao-chat-relay/
        ├── SKILL.md
        ├── scripts/
        │   └── doubao_relay.py
        └── references/
            ├── setup.md
            └── maintenance.md
```

## 当前 Skills

| Skill | 作用 | 状态 |
|------|------|------|
| `doubao-chat-relay` | 让 OpenClaw 通过 OpenCLI 调豆包网页或桌面版做文本问答 | 可用 |

## 当前 Skill 清单

详见：

- [skills/catalog.json](skills/catalog.json)

## doubao-chat-relay

用途：
- 让 OpenClaw 具备和豆包对话的能力
- 优先复用 OpenCLI，而不是自己重写整套网页自动化
- 兼容 `Windows` 和 `macOS`

支持命令：
- `login-check`
- `new`
- `ask`
- `read`
- `reset`

详细说明：
- [skills/doubao-chat-relay/SKILL.md](skills/doubao-chat-relay/SKILL.md)
- [skills/doubao-chat-relay/references/setup.md](skills/doubao-chat-relay/references/setup.md)
- [skills/doubao-chat-relay/references/maintenance.md](skills/doubao-chat-relay/references/maintenance.md)

## 后续新增 Skill 的放法

每个新 skill 都按这个结构新增：

```text
skills/<skill-name>/
├── SKILL.md
├── scripts/
└── references/
```

新增后要做 4 件事：
1. 更新 `skills/catalog.json`
2. 在仓库首页补一条目录
3. 把安装、使用、维护写完整
4. 自检脚本能不能单独运行

## 维护原则

- `SKILL.md` 负责告诉模型何时使用、如何调用
- `references/` 放详细说明和维护信息
- `scripts/` 放稳定可执行的脚本
- 不把个人凭证、登录态、Cookie 提交进仓库
- 不把临时调试文件混进正式 skill
