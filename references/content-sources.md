# Content Sources

Central feed is updated daily at 6am Beijing time. It is published from the
maintainer's machine rather than CI, because the WeChat source depends on a
self-hosted service that CI cannot reach. If that machine is offline,
subscribers simply keep reading the last successfully published feed.

Sources:

### Podcasts (14 channels)
Dwarkesh Patel, Lex Fridman, Latent Space, All-In Podcast, a16z, Naval, No Priors,
SemiAnalysis (Dylan Patel), Google DeepMind, Lightcone (YC), Lenny's Podcast,
Invest Like the Best, Capital Allocators, The Acquirers Podcast

### People tracking (28 people, YouTube-wide guest search)
Beyond the fixed channels, the central feed searches YouTube daily for these
people appearing as podcast/interview **guests** anywhere, limited server-side
to videos uploaded in the past week. Channels under 50k subscribers are
rejected (small re-upload accounts), and for overseas people, channels or
titles in a non-Latin script are rejected too (large foreign-language
dub/reaction channels carry no English transcript and aren't real interviews).
As a definitive backstop, an overseas-person video with no English caption
track at all is rejected — this catches foreign shows that use an English title
(e.g. Jensen Huang on the Korean variety show You Quiz on the Block, captions
only in Korean). Only English originals get through. Videos that merely talk
ABOUT the person are rejected too — a title whose grammar puts the name in
topic position ("Journalist Karen Hao on Sam Altman...", "the truth about X")
is coverage, not an appearance; only videos where the person actually speaks
count. Hits merge into the same
podcast feed with a `person` field (and `region: "cn"` for China AI voices,
which are exempt from both filters).

**Overseas:** Sundar Pichai, Greg Brockman, Sam Altman, Demis Hassabis, Jensen Huang,
Satya Nadella, Mark Zuckerberg; Anthropic (Dario/Daniela Amodei, Krishna Rao,
Mike Krieger, Sholto Douglas, Amanda Askell, Boris Cherny, Cat Wu, Alex Albert);
Kevin Weil (OpenAI), Ivan Zhao (Notion), Dylan Patel (SemiAnalysis), Gavin Baker (Atreides),
Naval Ravikant

**China AI:** 闫俊杰 (MiniMax), 杨植麟 (Moonshot), 梁文锋 (DeepSeek), 唐杰 (智谱),
罗福莉, 李广密 (拾象), 肖弘 (Manus)

### Twitter/X (21 accounts)
**Analysts:** Karpathy, Swyx, Dylan Patel (SemiAnalysis), Irrational Analysis,
Artificial Analysis (independent model benchmarks), Naval Ravikant,
Leopold Aschenbrenner, Jim Keller
**Executives:** Sam Altman, Dario Amodei, Demis Hassabis (Google DeepMind), Tang Jie (Z.ai)
**Infrastructure:** NVIDIA (Jensen Huang / AI infrastructure signal)
**Builders:** Amanda Askell, Boris Cherny (Claude Code), Cat Wu, Alex Albert, Guillermo Rauch (Vercel), Amjad Masad (Replit), Josh Woodward (Google Labs), Paul Gauthier (Aider)

### Official blogs (3 labs)
Anthropic (official sitemap — Anthropic has no RSS — filtered by the real
publish date on the article page), OpenAI (official RSS), Google DeepMind
(official RSS). Model launches, product releases, research and safety
frameworks land straight from the source instead of second-hand coverage.
Up to 5 per lab per day, 48h window. Served as `feed-blogs.json`.

### WeChat 公众号 (2 accounts)
数字生命卡兹克 (hands-on AI tooling tests and engineering practice),
Web3天空之城 (AI × crypto, capital and industry shifts behind the tech).

A lot of first-hand Chinese AI content (model evals, engineering write-ups,
industry analysis) is published only on WeChat 公众号 and never surfaces in the
English sources. The central feed pulls subscribed 公众号 through a self-hosted
[wewe-rss](https://github.com/cooderl/wewe-rss) instance and merges them in.
72h window, up to 30 articles per day and 5 per account; every item carries the
source 公众号 name and a body excerpt (first 1500 chars). Served as
`feed-wechat.json`, and merged into the same `articles` stream as the official
blogs (so they share the B1/B2 numbering).

### arXiv Papers (daily, up to 30)
cs.AI (Artificial Intelligence), cs.CL (Computation and Language), cs.LG (Machine Learning)

All feeds are fetched centrally. **No API keys needed for content.**
