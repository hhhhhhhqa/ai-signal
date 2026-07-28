# AI Signal + 微信公众号 —— 部署与运维总结

> 本文档记录了这套"AI 一线信号日报"系统的完整搭建成果、日常操作和排错方法。
> 最后更新:2026-07-27

---

## 1. 这是什么

一套**每天自动汇总 AI 一线信息、生成个性化日报**的系统,可以分发给同事一起用。

信息来源:
- **Twitter/X**(19 个一线账号,twscrape 抓取)
- **播客**(14 个频道 + 28 位人物的全网访谈搜索)
- **arXiv 论文**(cs.AI / cs.CL / cs.LG)
- **官方博客**(Anthropic / OpenAI / Google DeepMind)
- **微信公众号** ⭐️(本次新增,通过自建 wewe-rss)

---

## 2. 整体架构:中央供料 + 客户端各自生成

```
        ┌──────────── 中央(只有你一台 Mac 维护)────────────┐
        │  Twitter(cookie) + 播客 + arXiv + 博客 + 公众号     │
        │        ↓ scripts/generate_feed.py                  │
        │  产出 feeds/feed-*.json  ──►  git push 到公开 repo   │
        └───────────────────────────┬────────────────────────┘
                                    │  GitHub / CDN 公开托管
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
          同事A 的 Agent        同事B 的 Agent        同事C 的 Agent
        (装 /ai-signal 技能,拉 JSON,按各自口味生成日报)
```

**关键点:所有麻烦事(cookie、公众号登录、抓取)只在你这一端。**
同事只需装 `/ai-signal` 技能指向你的 repo,**不需要任何 key/cookie/服务**,直接从 GitHub 拉 JSON 生成日报。

> 因为 wewe-rss 跑在你 Mac 本地,**抓公众号这步必须在你 Mac 上跑**
> (GitHub Actions 云端够不到你本地的 127.0.0.1:4000)。这就是"发布者模式":
> 你 Mac 开机时跑一次 → push;你 Mac 关着,同事照样能拉到上一次的内容。

---

## 3. 现在有哪些组件在跑

| 组件 | 说明 | 位置/地址 |
|------|------|-----------|
| **Colima** | Mac 上的 Docker 运行时(aarch64 + vz + Rosetta) | `colima status` |
| **wewe-rss** | 公众号 → RSS(Docker,arm64 原生) | http://localhost:4000 |
| **ai-signal** | 抓取 + 日报生成脚本 | 本目录 `ai-signal-main/` |
| **Python venv** | 跑 ai-signal 脚本的环境 | `ai-signal-main/.venv` |

---

## 4. 日常操作

### 4.1 生成/刷新 feed(抓取全部来源)

```bash
cd "/Users/1huang/Desktop/willing capital/ai-signal-main"
export TWITTER_COOKIES='auth_token=...; ct0=...'   # 抓 Twitter 需要
.venv/bin/python scripts/generate_feed.py          # 抓全部
# 或单独抓某个源:
.venv/bin/python scripts/generate_feed.py --wechat-only
.venv/bin/python scripts/generate_feed.py --twitter-only
```
产物在 `feeds/feed-*.json`(含新增的 `feed-wechat.json`)。

### 4.2 生成日报

```bash
.venv/bin/python scripts/prepare_digest.py           # 正常:自动去重,只出没看过的
.venv/bin/python scripts/prepare_digest.py --include-seen   # 演示:不去重,倒出窗口内全部
```
它会写完整数据到 `~/.ai-signal/payload/payload.json`,由 Agent 读取后写成日报。

> **注意**:每个源有自己的"回看窗口"(见 `config/sources.json` 的 `lookback_hours`):
> Twitter 48h、播客 72h(人物 7 天)、论文 120h(跨周末)、博客 48h、公众号 72h。
> 所以日报会跨几天是正常的;正常运行靠 `~/.ai-signal/seen.json` **去重**,不会重复推。

---

## 5. 微信公众号子系统(wewe-rss)

### 5.1 基本信息

| 项 | 值 |
|----|----|
| 容器 | `cooderl/wewe-rss-sqlite:latest`(arm64 原生) |
| 控制台 | http://localhost:4000/dash |
| 登录码 AUTH_CODE | 见 `~/wewe-rss/auth_code.txt` |
| 数据目录(要备份) | `~/wewe-rss/data`(SQLite) |
| ai-signal 拉取地址 | `http://127.0.0.1:4000/feeds/all.json` |
| 登录方式 | **微信读书**扫码(非公众号平台) |

### 5.2 加公众号

打开控制台 → 账号管理确认微信读书已登录 → 搜索公众号名 / 粘贴公众号文章分享链接添加。
> ⚠️ 一次别加太多,频繁添加会被微信读书临时锁(「小黑屋」),等 24 小时或重启容器恢复。
> 你加号后 **ai-signal 自动包含**,无需改配置。

### 5.3 重新登录(登录失效时)

微信读书登录态会不定期失效(常见数周)。失效时:控制台里重新**扫码**即可(30 秒)。
只有你要做这件事,**同事无感**。扫码时**别勾"24 小时后自动退出"**。

### 5.4 常用命令

```bash
docker restart wewe-rss          # 重启(解「小黑屋」也用它)
docker logs -f wewe-rss          # 看日志
docker stop wewe-rss             # 停止
curl -s http://127.0.0.1:4000/feeds | python3 -m json.tool   # 看已订阅的公众号列表
```

---

## 6. 代码改动(本次为接入公众号所做)

| 文件 | 改动 |
|------|------|
| `config/sources.json` | 新增 `wechat` 配置块(base_url 指向 wewe-rss) |
| `scripts/generate_feed.py` | 新增 `fetch_wechat()` + `--wechat-only`,产出 `feed-wechat.json` |
| `scripts/prepare_digest.py` | 把公众号文章并入日报的 `articles` 流(自带来源公众号名) |

> ⚠️ 这些改动目前**只在本地**,还没提交进 GitHub repo(`hhhhhhhqa/ai-signal`)。
> 要让同事拿到,需要把本地目录跟 repo 对接并提交(见"待办")。

---

## 7. 关键坑与排错

- **公众号抓取 503 / 拉不到**:必须用 `127.0.0.1` 不能用 `localhost`。
  httpx 用 localhost 会走 IPv6(::1),撞上 Colima 的 IPv6 转发问题返回空 503。已在配置里固定 127.0.0.1。
- **Docker 没反应**:先 `colima start`。
- **公众号内容不更新**:检查微信读书登录是否失效(控制台看账号状态),失效就重新扫码。
- **为什么用 wewe-rss 不用 we-mp-rss**:we-mp-rss 走"公众号平台扫码登录",对现在的微信已失效
  (二维码出不来);wewe-rss 走微信读书接口,更稳。`~/we-mp-rss/` 目录已弃用,可删。

---

## 8. 进度

**已完成 ✅**
- Twitter 抓取跑通(twscrape + cookie),cookie 也已存进 GitHub Secrets
- wewe-rss 部署 + 微信读书登录 + 订阅公众号 + 出 RSS
- ai-signal 接入公众号,端到端跑通,29 个测试全过
- 生成过一份含公众号的真日报验证效果

**待办 ⬜**
1. 把代码改动提交进 `hhhhhhhqa/ai-signal` repo(同事才能装)
2. 配 Mac 定时任务(launchd):每天自动 `generate_feed` + `git push`
3. 加 wewe-rss 登录失效提醒(掉了自动通知你去重扫)
4. 写"同事安装 /ai-signal"的一页说明
5. (可选)按需调短各源 `lookback_hours`,让日报更"当日"

---

## 9. 速查

```bash
# 一次性刷新并生成日报数据
cd "/Users/1huang/Desktop/willing capital/ai-signal-main"
export TWITTER_COOKIES='auth_token=...; ct0=...'
.venv/bin/python scripts/generate_feed.py
.venv/bin/python scripts/prepare_digest.py

# 公众号服务
docker restart wewe-rss                    # 重启
open http://localhost:4000/dash            # 控制台(AUTH_CODE 见 ~/wewe-rss/auth_code.txt)
```
