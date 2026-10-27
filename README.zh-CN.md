# Brand Research Brain

**从感兴趣的网站学习，建立自己的 Shopify second brain。**

贴一个网站 → 读懂这个生意 → 学到三个具体做法 → 写进 Obsidian，并生成可阅读、截图分享的 HTML → 服务之后的选品、建站和增长。

[English](README.md) · [LiberNovo 学习示例](examples/learning/brain/wiki/brands/libernovo.md) · [新旧对照](docs/libernovo-comparison.md) · [验证记录](docs/validation.md)

## 两个核心 skills 与一个按需研究入口

| Skill | 作用 |
| --- | --- |
| `brain-init` | 创建本地 Shopify research and learning Brain，保存学习目标、阶段和兴趣。 |
| `brand-intake` | 从官网、文章、clip 或笔记学习，生成简洁案例和有价值的关联知识。 |
| `growth-research` | 按需研究社交媒体、创作者和 SEO，生成一篇简洁的增长学习。 |

研究时会考虑选品与用户洞察、产品与品牌、建站与转化、内容、获客增长、SEO，只展开材料支持的部分。每篇默认写清楚生意、三个具体做法，以及对自己项目的启发和一个小行动。材料太少时宁可少写，也不凑数。

案例不会默认变成品牌咨询报告。不需要评分、Study/Kill 判断、30 天实验计划或维度检查表。需要深入策略时，直接提出具体问题。

## 每次研究附一份 HTML 学习文档

v0.6.0 支持完整增长研究：概览下可展开增长阶段、内容实例、社交/创作者/SEO与零售路径、数据解读和具体借鉴。专题默认全部可读，有内部目录；知识卡模式按专题独立成卡，长内容自然延展。已有深入笔记不会再被硬压成三条要点，也无需打开 Markdown 才能读完整学习。

仅更新展示时复用已有研究，不重新调用 Monid 等数据提供方、不读取凭据、不增加研究日志。此版本没有内置 Monid 连接；普通网站 intake 仍保持简洁。

v0.6.0 明确品类部分的含义：**先讲本案是什么品类 → 创新亮点及依据 → 最后谈借鉴**。例如研究水杯配件时，先解释挂钩、挂饰和收纳怎样改变水杯的角色，再把原则迁移到用户的候选方向。品类卡不再直接跳到新产品的佩戴、固定或技术难点；这些放在清楚标注的借鉴与 ideas 部分。不会要求每个案例必须首创、必须有三个创新点或新建一份品类页。

v0.6.0 加强学习表达：先讲清一个具体购买场景、可替代选择和三项可借鉴做法，再提炼品类与想法。明确标为假设的例子可以用来提出测试；不把“参与感、交付边界”等抽象词当成解释，也不把研究限制写成整篇主线。重要选品问题可做一次有边界的补查，无需完整市场报告。[学习质量约定](plugins/brand-research-brain/skills/brand-intake/references/learning-quality.md)

深入 growth 默认只更新 HTML 的增长部分及来源，保护原有封面、方法、品类、ideas 和案例行动。若新证据实际纠正这些内容，再明确修订整篇。插件不依赖某个用户的私人 AGENTS.md，也不会把其偏好复制为开源默认值。

v0.6.0 在保存或更新 Markdown 后，生成 `reports/<品牌>.html`，精简展现案例事实、三个具体方法、品类洞察、增长洞察和当前案例的灵感，来源放在末尾。材料不足时少写，不编造获客策略或效果。

版式参考 Wise 的亮绿、深绿、大字和留白，使用原创布局和系统字体。支持连续阅读、分页知识卡和浏览器打印 / PDF；分享卡可逐张截图，内容长时自然延展。单文件可离线打开，不需要部署、付费 API 或额外 Obsidian 插件。尚未自动生成 PNG/PDF 或发布到社交平台。

HTML 是从已保存笔记提炼的阅读版本；知识库仍以 Markdown 为准。之后深入 growth 会刷新同一份文档，保留原有事实和方法。技术依据留在 `.brb/share/`；不会为了生成 HTML 重写原始材料或增加研究日志。你也可以明确要求本次只输出 Markdown。[输出约定](plugins/brand-research-brain/skills/brand-intake/references/share-card.md)

## 使用

需要可读写本地文件的 Agent、Python 3.9+；官网阅读使用宿主已有的浏览器或网页工具。不需要单独的模型 API key、服务器、Shopify 账号或 Obsidian REST 插件。

在 Codex 中使用本地源码安装：

```sh
codex plugin marketplace add .
codex plugin add brand-research-brain@brand-research-brain
```

插件更新后，按宿主提示刷新或开启新对话，确认显示的版本。源码 ZIP 是适合 GitHub 的独立仓库；plugin ZIP 是单插件包，按宿主支持的导入方式使用。[发布说明](docs/releasing.md) 解释两者区别。

> 在我指定的文件夹创建一个中文 Shopify 学习 Brain。我还在探索品类，想重点学习选品和产品页。

> 研究这个网站：URL。帮我读懂这个生意，学三个具体做法，写进 Brain。

Claude Code 用户现在可以从同一仓库安装，复用三个 skills：

```sh
claude plugin marketplace add .
claude plugin install brand-research-brain@brand-research-brain
```

仓库包含 Claude 专用识别文件，并生成 `brand-research-brain-0.6.0-claude-plugin.zip`。[Claude 发布与使用说明](docs/claude-release.md) 包含 GitHub 安装、首次使用、Cowork/网页端能力边界和后续目录提交步骤。当前完成结构与工具检查，Claude 实际研究会话仍需验收。

把生成的 Brain 文件夹作为 Obsidian vault 打开。Markdown 和双向链接就是知识库；Claude 或 Codex 读取其中的 `AGENTS.md`、`BRAIN.md` 后可以继续维护。插件不提供自动同步；网页会话也不会因安装插件而自动获得本机文件访问权。

之后可以继续问：

> 我研究过的案例中，有哪些产品页做法能用于我现在的候选产品？

## 按需深入 growth

> 深入研究 UseIt 的社交媒体、创作者和 SEO。只用公开免费流程，写成简洁的增长学习，链接回原案例。

这会主动查看站外账号、帖子、发布社区、介绍文章与搜索入口，区分品牌内容、独立提及、hunter 和已披露合作。新增或更新一篇 `wiki/growth/<品牌>-growth.md`，记录最清楚的发现路径、最多三个具体做法和一个自己的小行动。普通 intake 不会自动扩展成完整营销调查。

[UseIt 实际免费研究](examples/growth/brain/wiki/growth/useit-growth.md) 基于实时网页与浏览器访问。X 网页读取受阻后，普通浏览器公开预览成功；另外读取 Product Hunt 与第三方介绍页。没有付费 API、注册或登录，仍会使用现有 Agent/搜索服务额度。缺少创作者或 SEO 成效证据时如实说明，不靠想象补全策略。

AISA 仅作为[可选增强说明](plugins/brand-research-brain/skills/growth-research/references/optional-aisa.md)，本包不连接账户、不包含 key、不自动调用付费服务。有明确需求和预算时，才通过宿主已有连接补取社交或 SEO 数据；不需要 AISA 也能研究。

## 如何积累知识

采用 Karpathy 的 LLM Wiki 模式：保留原始材料，用 LLM 持续整理和关联知识，利用既有笔记回答新问题。这里是对这种模式的实现，并不依赖 Karpathy 的代码包或服务。

```text
raw/                 来源与实践记录，原始材料不覆盖
wiki/brands/         简洁案例学习
wiki/categories/     品类、用户问题与选品
wiki/shopify/        建站、产品页与转化
wiki/growth/         内容、推广、SEO 与留存
wiki/ideas/          与自己项目相关的想法
wiki/index.md        学习地图
wiki/log.md          简短学习日志
.brb/                后台来源登记
```

一个网站的多个网页分别留来源，但只合成一次案例、记一条日志。**每次 intake 都检查 categories、ideas、shopify、growth**，先读相关旧页，有实质新增就合并更新，相关但无新增就保留，材料不足则暂不建页。不强制固定页数。检查理由只进入后台登记，不在案例、日志或聊天里展示检查表。

**Ideas 先从当前案例提炼独立启发与假设，再判断是否合并到已有想法。** 只有用户问题或机制相同、且有实质新增时才合并；不能把新案例都套进旧项目，也不强制每个品牌生造一页。[判断规则与示例](docs/ideas.md)。想法仍需验证，不代表用户已执行。来源名可读、证据可追溯；官网展示不是效果证明，也不会因为用来学 Shopify 就假定对方使用 Shopify。

## 版本与已有 Brain

v0.6.0 保留插件身份、旧 Brain、来源和历史测试。已有 Brain 不会随插件更新自动改写；请明确让 Agent 调整学习目标和指南，保留自己的偏好和已有研究。对旧案例重做学习笔记时，先读取现有内容，再显式修订。旧版 payload 继续用于历史重放；新流程使用 `learn.py` 一次保存网站学习。增长研究采用同一 helper 的 `mode: growth`，支持保留主案例不动、单独写 growth 页。当前保存需包含后台四类 `knowledge_reviews`；旧 Brain 和历史记录仍可读取，旧 payload 只在明确的历史重放入口使用，不会偷偷迁移原文件。

## 开源与验证

参见 [开发命令](README.md#development)、[验证范围](docs/validation.md) 和 [发布说明](docs/releasing.md)。发布包排除个人 vault、原始私人测试副本和本地配置；没有自动推送 GitHub 或提交公开目录。

原始代码、skills 和原创摘要采用 MIT。第三方网站、文章与品牌资料保留各自权利：[来源说明](THIRD_PARTY.md)。
