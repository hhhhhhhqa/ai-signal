#!/usr/bin/env bash
# AI Signal 中央一键运行(Mac 本地)。
# 用法:
#   ./run.sh            抓取全部来源 + 转录无字幕播客(最多2集)
#   ./run.sh --no-asr   只抓取,不做火山 ASR 转录(省钱/快)
#   ./run.sh --digest   抓取(+转录)后,再生成一份日报 payload
set -uo pipefail
cd "$(dirname "$0")"

# ── 载入本地密钥 ─────────────────────────────────────────────
if [ ! -f .env ]; then
  echo "❌ 缺少 .env(应包含 TWITTER_COOKIES 和 VOLC_ASR_API_KEY)"; exit 1
fi
set -a; source .env; set +a
PY="$(pwd)/.venv/bin/python"

DO_ASR=1; DO_DIGEST=0; DO_PUBLISH=0
for a in "$@"; do
  [ "$a" = "--no-asr" ] && DO_ASR=0
  [ "$a" = "--digest" ] && DO_DIGEST=1
  [ "$a" = "--publish" ] && DO_PUBLISH=1
done

# ── 1. 确保 Docker / wewe-rss 在运行(公众号需要)──────────────
echo "==> 1/4 检查 wewe-rss(公众号来源)"
colima status >/dev/null 2>&1 || colima start
docker start wewe-rss >/dev/null 2>&1 || true
ok=0
for i in $(seq 1 15); do
  if curl -sf http://127.0.0.1:4000/feeds/all.json -o /dev/null; then ok=1; break; fi
  sleep 2
done
if [ "$ok" = 1 ]; then echo "   ✅ wewe-rss 就绪"; else echo "   ⚠️ wewe-rss 未就绪,公众号这次可能抓不到(其它源照常)"; fi

# ── 2. 抓取全部来源 ─────────────────────────────────────────
echo "==> 2/4 抓取 Twitter / 播客 / arXiv / 官方博客 / 公众号"
"$PY" scripts/generate_feed.py

# ── 3. 转录无字幕播客(火山 ASR,可选)──────────────────────
if [ "$DO_ASR" = 1 ]; then
  echo "==> 3/4 转录无字幕播客(最多 2 集)"
  "$PY" scripts/transcribe_missing_podcasts.py --limit 2 || echo "   ⚠️ 转录有告警,已跳过继续"
else
  echo "==> 3/4 跳过转录(--no-asr)"
fi

# ── 4. 可选:生成日报 payload ───────────────────────────────
if [ "$DO_DIGEST" = 1 ]; then
  echo "==> 4/4 生成日报 payload"
  "$PY" scripts/prepare_digest.py --include-seen > /tmp/ai-signal-digest.json 2>/dev/null && \
    echo "   ✅ payload: ~/.ai-signal/payload/payload.json(manifest 见 /tmp/ai-signal-digest.json)"
else
  echo "==> 4/4 完成。feeds/ 已更新。"
fi

# ── 发布:提交 feeds 并推送到 GitHub(供同事订阅)──────────────
if [ "$DO_PUBLISH" = 1 ]; then
  echo "==> 发布:提交 feeds 并推送到 GitHub"
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git add feeds/ 2>/dev/null
    if git diff --staged --quiet; then
      echo "   ℹ️ feeds 无变化,跳过推送"
    else
      git commit -q -m "Feed update $(date -u +%Y-%m-%d)"
      pushed=0
      for i in 1 2 3 4; do
        if git push -q origin main 2>/dev/null; then pushed=1; break; fi
        echo "   ⚠️ 推送第 $i 次失败(网络?),10 秒后重试..."; sleep 10
      done
      if [ "$pushed" = 1 ]; then
        echo "   ✅ 已推送到 hhhhhhhqa/ai-signal"
      else
        echo "   ❌ 推送多次失败;提交已在本地,下次运行会一并补推(不丢数据)"
      fi
    fi
  else
    echo "   ⚠️ 当前目录不是 git 仓库,跳过发布"
  fi
fi

echo ""
echo "🎉 done ($(date '+%Y-%m-%d %H:%M'))"
