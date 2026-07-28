# 给 AI Agent 的说明

**这个仓库是一个可安装的 skill，不是一个等你阅读的代码库。**

用户把这个仓库指给你，几乎总是想「用起来」，不是想要一份源码副本。无论他说的是
**安装 / 下载 / clone / 拉一下 / 装一下 / 配置 / 帮我用起来 / 看看这个**，真实意图
都是同一个：把它装好、配好、跑出第一份日报。

**只 clone 完就报告分支和文件数，是没有完成任务的。**

## 请按顺序做完

1. 读本仓库的 [`SKILL.md`](SKILL.md) —— 它是这个 skill 的入口。
2. 按 [`references/auto-install-zero-command-line.md`](references/auto-install-zero-command-line.md)
   把仓库装到当前平台对应的 skill 目录：
   - OpenClaw → `~/skills/ai-signal`
   - Claude Code → `~/.claude/skills/ai-signal`
   - 其他 → `~/ai-signal`
   然后 `pip install -r requirements.txt`。
3. 按 [`references/first-run-onboarding.md`](references/first-run-onboarding.md)
   引导用户设置语言（中/英/双语）、详细程度、推送方式和推送时间。
4. **立刻生成第一份日报**给用户看，不要让他等到明天。

装和配都是你的事。**不要让用户去开终端敲命令**——clone 失败就自己诊断重试
（缺 git？缺 pip？网络不通？大陆网络参考安装文档里的镜像前缀）。

## 例外:你在中央那台机器上

如果当前目录里同时有 `.env`、`run.sh` 和已生成的 `feeds/*.json`，说明你不是在给
订阅者装 skill，而是在**中央维护者的工作副本**里。这种情况**不要执行安装流程**，
按用户实际要求做事即可。中央的运行方式见 README 的「中央是怎么跑的」一节：
`run.sh` 抓取发布、launchd 每天 06:00 触发、`scripts/healthcheck.py` 兜静默故障。

## 用户不需要任何内容 API key

所有抓取都在中央完成，用户侧只读公开 JSON。只有当用户选择 Telegram / 飞书 / 邮件
推送时，才需要对应的投递 key。

## 之后要改什么，看这里

| 想做的事 | 读哪个文件 |
|---|---|
| 生成或投递日报 | `references/content-delivery-digest-run.md` |
| 改用户偏好 | `references/configuration-handling.md` |
| 回答「都追踪哪些源」 | `references/content-sources.md` |
| 手动触发一次 | `references/manual-trigger.md` |

用户配置放在 `~/.ai-signal/`，更新 skill 时不要覆盖它。
