# AI Signal

追踪 AI 一线的声音——做事的人、写代码的人、下注的人，不是二手转述。

这是一份给 AI Agent 用户的精心筛选信息源。中央每天自动抓取播客、推文、论文、官方博客和微信公众号；你的 Agent 读取 JSON，按你的口味生成日报。

**这份清单本身就是产品。**

如果这个项目对你有帮助，欢迎在 GitHub 点一下 Star，让更多需要 AI 一线信号的人看到它。

> ### 📌 如果你是正在读这个仓库的 AI Agent
>
> 这不是一个普通的代码仓库，是一个**可安装的 skill**。用户让你「安装 / 下载 / 拉一下 / 装一下 / 配置 / 帮我用起来」这个仓库时，**不要 clone 完就结束**，那不是用户要的结果。请按顺序做完：
>
> 1. 读本仓库的 [`SKILL.md`](SKILL.md)
> 2. 按 [`references/auto-install-zero-command-line.md`](references/auto-install-zero-command-line.md) 装到当前平台对应的 skill 目录
> 3. 按 [`references/first-run-onboarding.md`](references/first-run-onboarding.md) 引导用户设置语言、详细程度、推送方式和时间
> 4. 设置完**立刻生成第一份日报**给用户看
>
> 用户的唯一动作是开口，装、配、跑都是你的事——不要让用户去敲命令。

## 最近更新

- `2026-07-28`：X 新增 [@ArtificialAnlys](https://x.com/ArtificialAnlys)（独立模型评测跑分）和 [@paulgauthier](https://x.com/paulgauthier)（Aider 作者），共 21 个账号；公众号新增「Web3天空之城」，共 2 个
- `2026-07-28`：新增微信公众号来源——中文 AI 生态里很多一手内容只发在公众号，现在通过自建 wewe-rss 接入，和官方博客并入同一条 articles 流进日报（编号 B1/B2，可展开）
- `2026-07-28`：中央改为「本机发布者」模式——公众号抓取依赖自建服务，云端够不到，因此改由维护者的 Mac 每天 06:00 定时全量抓取并推送到本仓库；订阅方无感，照常从 GitHub / CDN 拉 JSON
- `2026-07-08`：新增 Naval Ravikant——加入 X 人物追踪、YouTube 人物访谈搜索和 Naval RSS 播客频道；Naval 频道单独使用 14 天窗口，避免错过低频长节目
- `2026-07-08`：人物追踪剔除"被谈论但本人没出场"的视频——标题语法守卫识别 "记者 on 某人"/"the truth about 某人" 这类评论内容，只收本人真实出场的访谈
- `2026-07-08`：定时任务默认限时拉到 15 分钟，避免网络或模型较慢时任务被中途杀掉后反复重启；OpenClaw cron 模板加 `--timeout-seconds 900`，其他平台要求任务限时 ≥10 分钟，另加故障排查一节
- `2026-07-07`：修复论文抓不到最新——arXiv 的 `submittedDate` 排序索引滞后（已知问题）导致"最新论文"卡在 3-4 天前，叠加时间窗把结果筛空、静默喂旧数据。改用 `lastUpdatedDate` 实时排序 + 72h 窗口，恢复抓当天最新论文
- `2026-07-06`：新增官方博客追踪——Anthropic / OpenAI / Google DeepMind 的模型发布、产品上线、研究成果直接进日报（编号 B1/B2，可展开）
- `2026-07-06`：大陆直连加固——feed 镜像从 2 个扩到 5 个 CDN 入口，被阻断的源 5 秒快速跳过（回应用户反馈"没 VPN 拉不到数据"）
- `2026-07-05`：新增人物追踪——28 位 AI 高管/分析师/创始人上任何播客都会被抓到（不再限于订阅频道），只收本周上传的最新访谈
- `2026-07-05`：修正 3 个 X 账号 handle（Dylan Patel / Leopold Aschenbrenner / Jim Keller 此前配错，一直抓不到推文）
- `2026-07-05`：feed 拉取加多源镜像——GitHub 不可达时自动切 jsDelivr CDN
- `2026-07-05`：推文加主题过滤，节日祝福 / 生活动态等噪音不再进 feed
- `2026-07-04`：安装瘦身——用户侧只需 `httpx[socks]`；修复 SOCKS 代理下拉取失败与 Python 3.9 装不上

完整历史见 [CHANGELOG](CHANGELOG.md)。

---

## 你会得到什么

由你的 AI Agent 读取中央 JSON 后生成一份日报（可直接在聊天里看；如果你的 Agent 支持定时任务，也可以每天自动推送），包含：

- 一线播客的最新内容（日报先给简介；你说“展开 P2”后再按需读取该期全文字幕）
- 精选推特账号的当日观点
- Anthropic / OpenAI / Google DeepMind 官方博客的最新发布（新模型、产品、研究、安全框架）
- 精选微信公众号的最新文章（中文 AI 生态的一手内容，很多只在公众号发）
- arXiv 最新 AI/ML/NLP 论文标题、链接和摘要原文
- 每条播客、推文和论文都显示来源发布时间，并按你的时区转换；无法验证的时间会明确标记
- 按你的偏好定制：中文 / 英文 / 双语，精华 / 标准 / 完整
- 不需要内容 API key——所有内容由中央服务统一抓取

> AI Signal 是 **Agent-first** 架构：中央只供料，不替每个用户生成最终日报。真正的总结、翻译、格式定制，都由用户自己的 Agent 完成。

## 日报不是终点

日报只是第一层筛选。看完以后你可以继续让 Agent 展开任意一条内容，尤其是长播客：

- “展开第 2 个播客”
- “把 Vercel agents 这期做一个 breakdown”
- “这期播客按核心观点、论证链、关键引用、投资含义展开”

如果该播客有全文字幕，日报会标记为可展开；只有你明确要求“展开 P2”后，Agent 才会按 `guid` 拉取这一期全文，而不是每天预先下载所有字幕。

字幕从最后一次出现在最近更新 feed 起保留 14 天。播客退出主 feed 后，仍可通过字幕索引展开；超过 14 天后全文缓存自动过期，只保留日报中的标题、链接和已有摘要。

## 信息源

### 播客（14 个频道）

| 频道 | 为什么选 |
|------|----------|
| [Dwarkesh Patel](https://www.dwarkesh.com) | 最深度的 AI 一对一访谈，嘉宾全是一线研究者 |
| [Lex Fridman](https://lexfridman.com/podcast/) | 覆盖面最广的 AI 长对话 |
| [Latent Space](https://www.latent.space) | AI 工程师生态的脉搏，Swyx 主理 |
| [All-In Podcast](https://www.allinpodcast.co) | 四个顶级 VC 的周度辩论，AI + 宏观 |
| [a16z](https://a16z.com/podcasts/) | 硅谷最大 VC 的一手投资视角 |
| [Naval](https://nav.al/) | Naval Ravikant 对 AI、技术、创业和资本形成的长线判断 |
| [No Priors](https://www.youtube.com/@NoPriorsPodcast) | Sarah Guo + Elad Gil，AI infra 创始人密度最高 |
| [SemiAnalysis](https://www.youtube.com/@SemiAnalysis) | Dylan Patel，半导体与 AI 基础设施最深度的独立分析 |
| [Google DeepMind](https://deepmind.com/podcast) | DeepMind 官方，前沿研究视角 |
| [Lightcone (YC)](https://www.youtube.com/@ycombinator) | YC 合伙人看 AI 创业生态 |
| [Lenny's Podcast](https://www.lennysnewsletter.com/) | AI 产品落地的一线反馈 |
| [Invest Like the Best](https://www.joincolossus.com/episodes) | 顶级投资人的思维框架 |
| [Capital Allocators](https://capitalallocators.com/podcast/) | 机构投资者视角 |
| [The Acquirers Podcast](https://acquirersmultiple.com/podcast/) | 价值投资方法论 |

### 人物追踪（28 人，全网搜索）

频道订阅之外，每天在 YouTube 全网搜索这些人作为**嘉宾**出现的访谈（RSS 只覆盖主持人自己的节目，这里补他们上别人节目的场合），搜索用 YouTube 服务端"本周上传"过滤器限定，只收最新的：

**海外**：Sundar Pichai、Greg Brockman、Sam Altman、Demis Hassabis、Jensen Huang、Satya Nadella、Mark Zuckerberg；Anthropic 全线（Dario / Daniela Amodei、Krishna Rao、Mike Krieger、Sholto Douglas、Amanda Askell、Boris Cherny、Cat Wu、Alex Albert）；Kevin Weil（OpenAI CPO）、Ivan Zhao（Notion）、Dylan Patel（SemiAnalysis）、Gavin Baker（Atreides）、Naval Ravikant

**中国 AI**：闫俊杰（MiniMax）、杨植麟（月之暗面）、梁文锋（DeepSeek）、唐杰（智谱）、罗福莉、李广密（拾象）、肖弘（Manus）

> 过滤规则：只收本周上传（YouTube 服务端过滤）、标题必须含人名（去同名假阳性）、时长 ≥ 15 分钟（去切片/shorts）、频道订阅数 ≥ 5 万（去小搬运号）、海外人物剔除非拉丁文字频道名/标题（去大号外语搬运/二创，如中文配音、印地语二创、韩语搬运）、海外人物要求视频有英文字幕轨（挡住英文标题的外语综艺，如韩综 You Quiz 上的 Jensen Huang 只有韩语字幕；只要英文原版）、剔除例行盘面播报和影视剧合集噪音；与频道订阅命中的同一期节目自动去重；每天最多新收 5 条，日报不会被人物命中刷屏。名单在 `config/sources.json` 的 `podcasts.people`。

### Twitter/X（21 个账号）

**分析师/研究者**：[@karpathy](https://x.com/karpathy)、[@swyx](https://x.com/swyx)、[@dylan522p](https://x.com/dylan522p)（SemiAnalysis）、[@insane_analyst](https://x.com/insane_analyst)（Irrational Analysis，半导体投资）、[@ArtificialAnlys](https://x.com/ArtificialAnlys)（Artificial Analysis，独立模型评测与跑分）、[@naval](https://x.com/naval)（Naval Ravikant）、[@leopoldasch](https://x.com/leopoldasch)、[@jimkxa](https://x.com/jimkxa)（Jim Keller）

**决策者**：[@sama](https://x.com/sama)、[@DarioAmodei](https://x.com/DarioAmodei)、[@demishassabis](https://x.com/demishassabis)（Google DeepMind）、[@jietang](https://x.com/jietang)（Z.ai / Tsinghua）

**基础设施**：[@nvidia](https://x.com/nvidia)（Jensen Huang / NVIDIA AI 基础设施信号）

**建造者**：[@AmandaAskell](https://x.com/AmandaAskell)、[@bcherny](https://x.com/bcherny)（Claude Code）、[@_catwu](https://x.com/_catwu)、[@alexalbert__](https://x.com/alexalbert__)、[@rauchg](https://x.com/rauchg)（Vercel）、[@amasad](https://x.com/amasad)（Replit）、[@joshwoodward](https://x.com/joshwoodward)（Google Labs）、[@paulgauthier](https://x.com/paulgauthier)（Aider 作者）

> 选人标准：在一线做事 / 有独立判断 / 用真金白银下注。不选搬运号、评论员、流量账号。

> 内容门槛：默认剔除回复，并要求互动分数达到 10（点赞 + 2×转发 + 回复）；小众账号可在 `config/sources.json` 单独降低门槛或允许回复。刚发布但互动不足的内容可能延后到下一次抓取。

### 官方博客（3 家）

| 来源 | 抓取方式 |
|------|----------|
| [Anthropic](https://www.anthropic.com/news) | 官方 sitemap（Anthropic 无 RSS）+ 文章页真实发布日期过滤 |
| [OpenAI](https://openai.com/news/) | 官方 RSS |
| [Google DeepMind](https://deepmind.google/blog/) | 官方 RSS |

> 模型发布、产品上线、研究成果、安全框架，第一时间从官方渠道进日报，不等二手转述。每家每天最多 5 条，48 小时窗口。

### 微信公众号（2 个）

| 公众号 | 为什么选 |
|--------|----------|
| 数字生命卡兹克 | 一线 AI 工具实测与工程实践，出手快、动手做，不停留在转述 |
| Web3天空之城 | AI 与加密的交叉视角，关注技术叙事背后的资本与产业变化 |

中文 AI 生态里大量一手内容（模型评测、工程实践、行业观察）只在公众号发，英文源覆盖不到。中央通过自建的 [wewe-rss](https://github.com/cooderl/wewe-rss) 把订阅的公众号转成 RSS 再并入 feed，产出 `feed-wechat.json`，在日报里和官方博客同属 articles 流，会标注来源公众号名，**带正文摘要**（默认前 1500 字，可展开原文链接）。

> 72 小时窗口，每天最多 30 篇、单个公众号最多 5 篇。订阅列表由中央维护，随时可加，**订阅方不需要任何配置**——公众号登录态、Docker、抓取全在中央那一端。

### arXiv 论文（每日最多 30 篇）

| 分类 | 覆盖范围 |
|------|----------|
| cs.AI | 人工智能 |
| cs.CL | 计算语言学（LLM / NLP 论文主阵地） |
| cs.LG | 机器学习 |

> 使用 5 天滚动窗口跨过周末和休刊时段，客户端按论文 ID 去重，不会重复推送。中央每天北京时间 06:00 做全量抓取，工作日约 09:30 再做一次 arXiv 专用刷新，以避开新论文批次尚未发布的空窗；09:30 前的早报可能仍使用上一批论文。

## 快速开始

打开你的 AI Agent（OpenClaw / Claude Code / Cursor / WorkBuddy / Codex 等），把下面这句**整句**发给它：

> **帮我安装并配置这个 skill：https://github.com/hhhhhhhqa/ai-signal
> 读它的 SKILL.md，按 references/auto-install-zero-command-line.md 装好，
> 然后引导我完成初始设置并生成第一份日报。**

AI 会自动完成安装，然后引导你设置推送频率和时间、语言、详细程度和输出方式。设置完**立刻生成第一份日报**。

不需要敲命令、不需要内容 API key。你需要一个能运行这个 skill 的 AI Agent。

<details>
<summary>它只把仓库下载下来就没动静了？</summary>

**别只说「下载」。** 「下载 / clone / 拉一下」在 AI 听来就是取文件，它照做完就结束了，这是它理解正确、不是出错。要用「**安装并配置**」这种带完整意图的说法，最好像上面那样把后续步骤一并说清。

如果它已经下载完停住了，直接补一句：

> **读一下这个仓库的 SKILL.md，按里面的安装流程装好，然后引导我做初始设置。**

**还是不行？** 有些入口（比如各家的 GitHub 连接器 / 仓库导入功能）只把仓库当资料读进上下文，不会执行里面的安装流程。这种情况换一个能跑命令的 Agent 会话，或者用下面的手动安装。

</details>

<details>
<summary>手动安装（如果你的 Agent 不支持自动安装）</summary>

```bash
# OpenClaw
git clone https://github.com/hhhhhhhqa/ai-signal.git ~/skills/ai-signal
cd ~/skills/ai-signal/scripts && pip install -r ../requirements.txt

# Claude Code
git clone https://github.com/hhhhhhhqa/ai-signal.git ~/.claude/skills/ai-signal
cd ~/.claude/skills/ai-signal/scripts && pip install -r ../requirements.txt

# 其他
git clone https://github.com/hhhhhhhqa/ai-signal.git
cd ai-signal/scripts && pip install -r ../requirements.txt
```

**国内网络 clone 失败？** 用镜像加速前缀（示例，失效就换一个同类服务）：

```bash
git clone https://gh-proxy.com/https://github.com/hhhhhhhqa/ai-signal.git
# 或
git clone https://ghfast.top/https://github.com/hhhhhhhqa/ai-signal.git
```

安装后的每日 feed 更新不依赖代理：GitHub 直连失败时自动切换 jsDelivr CDN 镜像。

安装完成后告诉你的 Agent：**"set up ai signal"**

</details>

## 定制

所有偏好都可以用对话修改：

| 设置 | 选项 | 对话示例 |
|------|------|----------|
| 语言 | 中文 / 英文 / 双语 | "切换成中文" |
| 详细程度 | 精华 / 标准 / 完整 | "我要更详细的" |
| 领域 | AI / 投资 | "只看 AI 的" |
| 推送 | Telegram / 飞书 / 邮件 / 聊天 | "推到 Telegram" |

### 本地反馈

看完日报后可以直接说“P2 有用”“X1 是噪音”“多看芯片”或“少看融资新闻”。Agent 会把反馈保存在本机 `~/.ai-signal/feedback.jsonl`，最近 90 天的反馈会作为下一份日报的软排序偏好，不上传到中央服务，也不会因为一次负面反馈永久屏蔽重大消息。

用户要求展开某期播客时，会自动记录一次 `expanded`，用来观察哪些内容真正引发深读；展开只代表兴趣，不自动等同于“有用”。

### 自定义摘要风格

编辑 `~/.ai-signal/prompts/` 下的文件：

- `summarize-podcast.md` — 播客怎么总结
- `summarize-tweets.md` — 推文怎么提炼
- `summarize-papers.md` — 论文怎么摘要
- `digest-intro.md` — 整体语气和格式

纯文本指令，不是代码。改完下次推送生效。

## 工作原理

```mermaid
flowchart LR
  A["一线信息源<br/>X / 播客 / arXiv<br/>官方博客 / 公众号"] --> B["中央<br/>每天 06:00 自动抓取"]
  B --> C["公开 JSON feeds<br/>feed-x / feed-podcasts / feed-arxiv<br/>feed-blogs / feed-wechat"]
  C --> D["你的 AI Agent<br/>读取 JSON + 你的偏好"]
  D --> E["生成个性化日报<br/>中文/英文、长/短、可继续追问"]
  E --> F["聊天窗口 / Telegram / 飞书 / 邮件"]
```

简单说：中央只负责每天把 AI 一线原料抓好，用户自己的 Agent 负责筛选、翻译、总结和推送。这样不需要每个用户准备内容 API key，也不会把你的阅读偏好上传到中央服务。

**你不需要任何内容 API key。** 内容抓取在中央完成，摘要由你自己的 AI Agent 读取 JSON 后生成。

默认是 **JSON-first**：中央只提供原始 feed，不生成中文版日报。这能减少中文、emoji、长播客字幕在命令行、定时任务和推送链路里的编码问题。中央 LLM 摘要能力仍保留为手动调试选项，但不是默认用户路径。

<details>
<summary>中央是怎么跑的（只有维护者需要看）</summary>

公众号来源依赖一个自建的 wewe-rss 服务（跑在维护者本机 Docker 里），云端 CI 够不到，所以中央采用**本机发布者模式**：维护者的 Mac 每天定时跑一次全量抓取，再把 `feeds/` 推到本仓库。

```bash
./run.sh              # 抓全部来源 + 转录无字幕播客（最多 2 集）
./run.sh --no-asr     # 只抓取，不做 ASR 转录（快、省钱）
./run.sh --digest     # 抓取后再生成一份日报 payload
./run.sh --publish    # 抓取后 git commit + push 到本仓库（定时任务用这个）
```

无人值守由两个 launchd 任务承担：

| 任务 | 时间 | 干什么 |
|---|---|---|
| `com.aisignal.daily` | 每天 06:00 | 跑 `run.sh --publish`：抓取 → 提交 → 推送 → 健康检查 |
| `com.aisignal.wechatcheck` | 每天 00:00 | 只查微信读书登录是否失效，失效就发邮件 |

主任务外面套 `caffeinate -i` 防止跑到一半进休眠；配合 `pmset repeat wakepoweron` 在 05:55 唤醒机器，保证准点而不是等唤醒后补跑。推送失败会重试 4 次，仍失败则提交留在本地，下次运行一并补推，不丢数据。

**公众号同步不依赖 wewe-rss 自己的定时任务。** 它的内置 cron 在微信读书 token 过期时会抛 `暂无可用读书账号` 中止，而且不会自行恢复——实测静默跳过了整整一天。所以抓取前我们主动调它的 `feed.refreshArticles` 拉一次最新文章，需要在 `.env` 里配 `WEWE_RSS_AUTH_CODE`（就是控制台登录码，见 `~/wewe-rss/auth_code.txt`）。这样既保证每天拿到的是新数据，也让登录失效在我们关心的那一刻就报错，而不是变成一份看不出问题的旧 feed。

排查看两处：

```bash
launchctl print gui/$(id -u)/com.aisignal.daily | grep -E "runs|last exit code"
tail -30 run-cron.log
```

**静默故障告警。** 无人值守最大的风险不是报错，是**不报错**：X cookie 过期、微信读书掉登录、ASR 余额耗尽、venv 里的依赖丢了，这些都不会让任务退出码变成非 0，只会让 feed 悄悄停在昨天。`run.sh` 最后会跑 `scripts/healthcheck.py` 专门查这些：

| 检查 | 判据 | 提示 |
|------|------|------|
| 依赖 | 中央依赖能否 import | 给出补装命令 |
| X/Twitter | feed 是否超 26h 没更新 / 全部账号 0 内容 | cookie 过期，去更新 `TWITTER_COOKIES` |
| 公众号 | 账号是否被禁用（收到 401 当下就置位）；wewe-rss 是否可达；`syncTime` 是否超 26h 没推进 | 服务挂了 or 微信读书要重新扫码 |
| ASR 转录 | 转录失败里是否含余额/配额字样 | 去火山引擎控制台看余额 |
| arXiv / 博客 / 播客 | feed 是否超 26h 没更新 | 对应来源连续抓取失败 |

结果写进 `~/.ai-signal/health.json`，有问题时**默认弹一条 macOS 通知**（零配置）。想收邮件或推到手机，在 `.env` 里补上任一组，多个渠道可叠加：

```bash
# 邮件(两种发信方式，SMTP 失败会自动回落到 Resend)
HEALTH_EMAIL_TO=you@example.com
HEALTH_SMTP_USER=you@gmail.com     # 方式 A：SMTP，密码用 Google 应用专用密码
HEALTH_SMTP_PASS=xxxxxxxxxxxxxxxx  #   host/port 默认 smtp.gmail.com:465
RESEND_API_KEY=re_xxx              # 方式 B：Resend（HTTPS，不吃 SMTP 端口封锁）

HEALTH_WEBHOOK_URL=...             # 飞书 / 企业微信 自定义机器人
HEALTH_TG_BOT_TOKEN=...            # Telegram（配合 HEALTH_TG_CHAT_ID）
HEALTH_TG_CHAT_ID=...
```

配完不用等真故障，直接验证通道：

```bash
set -a; source .env; set +a
.venv/bin/python scripts/healthcheck.py --test
```

> **大陆网络注意**：Gmail 的 SMTP 端口（465/587）在大陆基本发不出去——465 的 TLS 会被直接掐断，587 连得上但收不到 SMTP 欢迎语。不挂代理的话走方式 B（Resend 是 HTTPS，不受影响）。SMTP 失败时代码会自动回落到 Resend，两个都配上最稳。

> ASR 那项是**症状检测**不是余额查询——火山的 API-key 凭据查不了余额，所以只能在转录报错里识别余额/配额关键词。余额耗尽会在第一次尝试转录时被发现，不会提前预警。

**中央那台机器关着也不影响订阅方**——大家拉到的是上一次成功推送的 feed。

</details>

## 要求

- 一个 AI Agent（OpenClaw、Claude Code、Cursor、WorkBuddy、Codex 等均可）
- 网络连接（拉取中央 feed；不需要 VPN——GitHub 不可达时自动走 jsDelivr CDN 镜像）

就这些。不需要内容 API key。所有内容由中央统一抓取，每天自动更新。若要无人值守地每天自动收到，需要使用支持定时任务的 Agent；普通非持久 Agent 更适合手动输入 `/ai-signal` 查看。

## 隐私

- 不采集任何用户数据
- 你的配置和偏好只存在你自己的机器上（`~/.ai-signal/`）
- 只聚合公开内容（公开推文、公开播客、公开论文）

## 关于

这份清单来自一个二级市场研究员的日常信息源。筛选标准只有一个：**这个人说的话，值不值得我每天花时间看。**

公众号「奔波儿r」· [GitHub](https://github.com/Benboerba620)

## License

MIT
