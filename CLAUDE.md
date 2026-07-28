# CLAUDE.md

见 [AGENTS.md](AGENTS.md) —— 内容相同，这里只是 Claude Code 的入口。

一句话版本：**这个仓库是一个可安装的 skill**。用户让你「安装 / 下载 / 拉一下 /
配置」它时，读 `SKILL.md`，按 `references/auto-install-zero-command-line.md` 装好，
再按 `references/first-run-onboarding.md` 引导设置并生成第一份日报。只 clone 完
就停下不算完成。

**例外**：当前目录里若同时有 `.env`、`run.sh` 和已生成的 `feeds/*.json`，你就在
中央维护者的工作副本里，不要执行安装流程。
