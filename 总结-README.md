# AI Signal + 微信公众号 —— 部署与运维总结

> 本文档记录了这套"AI 一线信号日报"系统的完整搭建成果、日常操作和排错方法。
> 最后更新:2026-07-29

---

## 1. 这是什么

一套**每天自动汇总 AI 一线信息、生成个性化日报**的系统,可以分发给同事一起用。

信息来源:
- **Twitter/X**(19 个一线账号,twscrape 抓取)
- **播客**(14 个频道 + 28 位人物的全网访谈搜索)
- **arXiv 论文**(cs.AI / cs.CL / cs.LG)
- **官方博客**(Anthropic / OpenAI / Google DeepMind)
- **微信公众号**(自建 we-mp-rss,2026-07-29 起;此前用 wewe-rss)

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
| **we-mp-rss** | 公众号 → RSS(**当前使用**,公众号平台登录) | http://127.0.0.1:8001 |
| wewe-rss | 旧方案,已停用但容器保留 | http://127.0.0.1:4000 |
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

## 5. 微信公众号子系统(we-mp-rss,2026-07-29 起启用)

### 5.0 怎么打开、怎么才能扫码成功

| 项 | 值 |
|----|----|
| 控制台 | http://127.0.0.1:8001/ |
| 账号 | `admin` / `admin@123` |
| 端口 | 只绑 127.0.0.1,不对外 |
| 数据目录 | `~/we-mp-rss/data`(含 `db.db` 和登录凭据 `wx.lic`) |
| 登录方式 | **公众号平台**扫码(不是微信读书),有效期约 **4 天** |

**前提是 Xvfb 必须在跑**,否则微信会把无头浏览器识别成机器人,二维码永远不出现。
容器的 `start.sh` 已打补丁自动清理残留的 `/tmp/.X99-lock`,所以 `docker restart`
之后会自愈,不用手动干预。确认一下:

```bash
docker exec we-mp-rss sh -c 'ps aux | grep -i "[X]vfb"'   # 必须有输出
```

**扫码步骤**:

1. 开 http://127.0.0.1:8001/ 登录后台,点授权
2. 二维码出不来就**强制刷新**(Cmd+Shift+R)—— 之前多次 404 会被浏览器缓存住;
   或直接开 `http://127.0.0.1:8001/static/wx_qrcode.png?nocache=$(date +%s)`
3. 手机扫码后**一定要点「确认登录」**,页面跳转到公众平台首页才算成功
4. 看日志判断真假:

```bash
docker logs we-mp-rss --since 5m | grep -E "已跳转到公众平台|已更新Token|超时"
```

| 日志 | 含义 |
|------|------|
| `检测到页面跳转（尚未确认登录）` | 还没成 |
| `已跳转到公众平台首页，扫码确认完成` | **真成了** |
| `已更新Token: xxx` | 凭据落库 |
| `扫码登录超时` | 5 分钟没确认,重来 |

> ⚠️ **镜像里的代码有 bug,是打过补丁的。** `docker restart` 能保住补丁,
> **`docker rm` 重建就会丢**,必须重新打。补丁文件见
> `/private/tmp/.../scratchpad/wx_patched.py`,容器内原版备份在
> `/app/driver/wx.py.bak`。详见 5.6。

### 5.0.1 关键环境变量

```bash
-e HEADLESS=false -e ENABLE_XVFB=true    # 不加二维码出不来(微信反无头检测)
-e GATHER.CONTENT=True                    # 不加抓不到正文,默认是 False
-e GATHER.CONTENT_AUTO_CHECK=True
```

### 5.0.2 ai-signal 怎么接的

`config/sources.json` 的 `wechat.provider = "we-mp-rss"`,读两个免鉴权接口:

- `GET /rss/all` —— 全部文章,正文在 `<content:encoded>` 里
- `GET /rss/{mp_id}` —— 从 `<channel><title>` 取公众号名

**不依赖时序**:ai-signal 在抓公众号前会自己调
`/api/v1/wx/mps/update/{mp_id}` 触发同步并**等它把正文采完**,再读 `/rss/all`。
需要 `.env` 里的 `WEMP_USERNAME` / `WEMP_PASSWORD`。

we-mp-rss 自己那个 05:57 的 cron 现在只是兜底 —— Mac 夜里休眠时它本来就不会跑
(虚拟机整个挂起),这正是不能靠它的原因。

---

## 5.5 旧方案:wewe-rss(已停用,容器保留)

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

**不用主动盯。** 账号失效时会自动发邮件到 royhuang066@gmail.com,
**附件里直接带登录二维码**,用微信扫一下就恢复了。检测有三层:
抓取时刷新失败立刻报错、账号 status 被禁用当下可查、`syncTime` 超 26 小时兜底;
另有一个 00:00 的 launchd 任务(`com.aisignal.wechatcheck`)每天单独查一次。

二维码有效期只有几分钟,过期了重新跑一次就会生成新的:

```bash
cd ~/ai-signal-main && set -a && source .env && set +a
.venv/bin/python scripts/healthcheck.py --wechat-only
```

**为什么会失效(2026-07-28 查清)**:不是"登录过期",是**配额被打满**。
作者在 [issue #396](https://github.com/cooderl/wewe-rss/issues/396) 里说明,
上游中转接口限制**一个号每天 50 次请求、一个 IP 24 小时 300 次**,
超了返回 401,而 wewe-rss 分不清"token 无效"和"配额用完",一律当失效禁用账号。

所以:**别手动点"更新全部"**(每点一次都在烧额度),订阅的公众号越多消耗越快。
真要缓解就**加第二个微信读书小号**——源码 `getAvailableAccount()` 支持最多 10 个账号
并随机轮换,每个号有独立的 50 次额度。

> ⚠️ 网上流传的"扫码时别勾『24 小时后自动退出』"**已经过时**——
> 那个选项在当前版本的登录界面里根本不存在,多位用户在
> [issue #458](https://github.com/cooderl/wewe-rss/issues/458) 里确认过。

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
- **二维码出不来**:2026-07-29 已查明并修复,不是微信封了扫码登录 —— 是镜像代码落后
  + 无头浏览器被识别 + 可见性判断 bug 三者叠加。见 5.6。**别删 `~/we-mp-rss/`,现在在用。**

---

## 8. 进度

**已完成 ✅**
- Twitter 抓取跑通(twscrape + cookie),cookie 也已存进 GitHub Secrets
- wewe-rss 部署 + 微信读书登录 + 订阅公众号 + 出 RSS
- ai-signal 接入公众号,端到端跑通,29 个测试全过
- 生成过一份含公众号的真日报验证效果

**已完成 ✅(2026-07-28 补)**
- 代码改动已提交进 `hhhhhhhqa/ai-signal` repo(同事可装)
- Mac 定时任务已配:launchd `com.aisignal.daily` 每天 06:00 跑 `run.sh --publish`,
  外套 `caffeinate -i`,配合 `pmset repeat wakepoweron 05:55` 准点唤醒
- 云端 GitHub Actions 的日常 cron 已停(会和本机 push 打架、且盖掉公众号),
  只保留 `workflow_dispatch` 手动兜底
- 静默故障告警已加:`scripts/healthcheck.py`,run.sh 末尾自动跑,
  覆盖 cookie 过期 / 微信读书掉登录 / ASR 余额 / 依赖丢失 / feed 变陈旧

**待办 ⬜**
1. 写"同事安装 /ai-signal"的一页说明
2. (可选)按需调短各源 `lookback_hours`,让日报更"当日"
3. arXiv 连续 429 限流待处理(7-24 起 feed 就没更新过,一直在喂旧论文)
4. (可选)在 `.env` 配 `HEALTH_WEBHOOK_URL`,让告警推到手机而不只是 macOS 通知

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

---

## 5.6 we-mp-rss 打过的补丁(重建容器后必须重打)

镜像 `ghcr.io/rachelos/we-mp-rss:latest` 的代码落后于 GitHub 源码,且新代码本身还有
两个 bug。二维码能显示出来靠的是下面 4 处修复:

| # | 问题 | 修法 | 来源 |
|---|------|------|------|
| 1 | 镜像里 `wx.py` 是旧版(733 行),`networkidle` 无超时,微信登录页有持续轮询 → 永久卡死 | 换成 GitHub 最新版(814 行) | [issue #436](https://github.com/rachelos/we-mp-rss/issues/436) |
| 2 | 无头浏览器被微信识别,返回反爬页 | `HEADLESS=false` + `ENABLE_XVFB=true` | issue #436 |
| 3 | `start.sh` 里 Xvfb 启动前不清理 `/tmp/.X99-lock`,容器重启后残留的锁让 Xvfb 起不来 → 二维码不出现 | 在启动 Xvfb 前加 `rm -f /tmp/.X99-lock` | **本地发现** |
| 4 | `_wait_qrcode_ready` 用 `getComputedStyle(img)` 判断可见性,读的是 img 自身样式;二维码被**祖先容器**隐藏时它仍返回可见,于是跳过"切换到扫码登录"的点击,截图必然超时 | 改用 `getBoundingClientRect()`,祖先隐藏时返回 0×0 | **本地发现,上游未知** |
| 5 | `framenavigated` 监听器对任意 frame(含快捷登录 iframe)都打印"登录成功",用户以为好了就停手,实际 `wait_for_url` 还在等,5 分钟后超时 | 改成如实报告跳转,成功只由 `wait_for_url` 判定 | **本地发现,上游未知** |

重建容器后恢复补丁:

```bash
docker cp <备份的 wx.py> we-mp-rss:/app/driver/wx.py
docker exec we-mp-rss sh -c 'rm -f /tmp/.X99-lock'
docker restart we-mp-rss
```

> 上游还有两个未修的 issue 悬着:[#397](https://github.com/rachelos/we-mp-rss/issues/397)
> (容器内账号信息获取失败)和 [#419](https://github.com/rachelos/we-mp-rss/issues/419)
> (登录状态从不向微信校验,只看本地过期时间)。目前没影响到我们,但要心里有数。
