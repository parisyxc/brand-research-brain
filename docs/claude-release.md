# 在 Claude 发布和使用 Brand Research Brain

Brand Research Brain 帮助个人创业者学习优秀品牌，把品牌、品类、用户增长和灵感借鉴持续积淀成 Shopify 学习 Brain。输入官网、文章或材料，读懂生意，学习三个具体做法，保存关联 Markdown 和中文 HTML。

首版推荐通过同一个 GitHub 仓库分发给 Claude Code 用户，直接维护本地 Brain 和 Obsidian 文件。仓库已补齐 Claude manifest、marketplace 和专用 ZIP，复用 v0.6.0 的三个 skills 与原版 Python 工具。尚未创建 GitHub 远端或向 Anthropic 目录提交。结构校验与实际 Claude 案例试跑是不同检查，最新实测范围见文末。

## 选择使用入口

| 入口 | 本插件的使用方式 |
| --- | --- |
| Claude Code | 首版推荐。提供实际 Brain 文件夹和 Python 3.9+，通过本地文件、命令和可用网页工具执行完整流程。 |
| Claude Cowork | 可以通过插件入口上传自定义包。选择并授权实际项目文件夹，先确认脚本执行和网页访问，再验证写回；尚未进行本插件的 Cowork 端到端测试。 |
| Claude 网页或 Desktop 的 Chat | 当前官方支持插件 skills。可以用于阅读、讨论和生成研究；本插件的完整保存流程需要文件及 Python 执行能力。不能把用户本机路径视为网页端可访问目录，不能承诺自动写回本机 Obsidian。 |

官方入口与能力可能更新，以 [Claude 插件说明](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) 为准。插件安装不自动赋予目标文件夹权限，也不提供额外模型或搜索额度。

## 发布者把什么放到 GitHub

发布独立的 `brand-research-brain` 源码仓库，保留隐藏目录：

```text
.claude-plugin/marketplace.json            Claude 仓库目录
.agents/plugins/marketplace.json          Codex 仓库目录
plugins/brand-research-brain/
  .claude-plugin/plugin.json              Claude 插件身份
  .codex-plugin/plugin.json               Codex 兼容身份
  plugin.json                            Portable 身份
  README.md
  skills/brain-init/
  skills/brand-intake/
  skills/growth-research/
docs/claude-release.md
```

两份 marketplace 指向同一个插件目录。三个 manifest 的名称、版本、描述、作者和许可保持一致。不要发布外围个人 vault、`.local/`、真实用户测试材料或凭据。打包工具按既有公开文件边界排除这些内容。

在仓库根目录执行：

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 scripts/validate_repo.py
claude plugin validate ./plugins/brand-research-brain
claude plugin validate .
python3 scripts/package.py
```

新版 Claude CLI 支持 `--strict` 时，对两条 `claude plugin validate` 加上该参数，让警告也导致失败。不要把旧 CLI 的校验等同于当前目录的提交检查。

将源码提交到自己的 GitHub 仓库，按现有 [GitHub 发布说明](releasing.md) 创建 `v0.6.0` Release。首个公开版本尚未发布，因此这里保留现有版本；以后发布变更时递增所有 manifest 的版本。

发布附件：

- `brand-research-brain-0.6.0-source.zip`：独立源码，包含两类 marketplace。
- `brand-research-brain-0.6.0-plugin.zip`：Portable/Codex 包，同时保留 Claude 识别文件。
- `brand-research-brain-0.6.0-claude-plugin.zip`：Claude 专用包，ZIP 根目录直接包含 `.claude-plugin/plugin.json`、`skills/`、README 和 LICENSE，无 Codex 元数据。
- `SHA256SUMS`：当前三份包的校验值。

Claude 专用包适合下载、解压测试或在支持自定义插件上传的 Claude 入口导入。无需用户手动复制三个 skill 文件夹。

## 新用户从 GitHub 安装

把 `YOUR_GITHUB_NAME` 换成作者的真实用户名。这是占位示例，不是当前已经存在的仓库。

在电脑终端执行：

```sh
claude plugin marketplace add YOUR_GITHUB_NAME/brand-research-brain
claude plugin install brand-research-brain@brand-research-brain
```

也可以在 Claude Code 对话中操作：

```text
/plugin marketplace add YOUR_GITHUB_NAME/brand-research-brain
/plugin install brand-research-brain@brand-research-brain
```

按宿主提示选择安装范围并刷新或开启新会话。在 `/plugin` 中检查启用状态，输入 `/` 查找三个入口：

```text
/brand-research-brain:brain-init
/brand-research-brain:brand-intake
/brand-research-brain:growth-research
```

尚未发布 GitHub 时，在解压后的源码根目录用 `claude plugin marketplace add .` 添加本地来源，再执行相同安装命令。只试一个会话时，解压 Claude 专用 ZIP 到一个文件夹，运行 `claude --plugin-dir /path/to/unzipped-plugin`。插件工具目录与自己的 Brain 必须分开。

使用前在自己的项目文件夹启动 Claude Code，明确 Brain 的实际位置；不要在插件源码目录中混入个人研究。完整安装和更新语法见 [官方安装文档](https://code.claude.com/docs/en/plugins/install)。

## 第一次使用

将路径和 URL 换成用户自己的实际输入：

> 使用 Brand Research Brain，在 /path/to/my-shopify-brain 创建一个中文 Shopify research and learning Brain。我正在探索适合个人创业的品类，希望学习怎样利用中国供应链服务海外用户。先研究这个网站：URL。讲清它的生意和本案品类亮点，提炼三个具体做法，沉淀当前案例自己的 ideas，并生成中文 HTML。缺少证据时少写，不编造销量或增长效果。

已有 Brain 不必重建：

> 继续使用 /path/to/my-shopify-brain。先读 AGENTS.md、BRAIN.md、brain.json 和相关旧笔记，保留已有内容。Intake 这个案例：URL。我特别想学习它的产品切口、定位和内容。更新有实质新增的关联知识与 HTML。

需要深入增长时：

> 深入研究这个案例的社交媒体、创作者和 SEO。查看实际内容，区分增长阶段，给出具体实例和可借鉴做法，并完整呈现在 HTML。先用公开网页，不接付费 API。

普通 intake 保持简洁。每次后台检查 categories、ideas、shopify、growth；有实质内容才更新，不强制四篇新页面。深入 growth 保护原有案例学习；只要求展示已有研究时，不重新调用数据提供方。

可以随时问：

> 结合我已经研究的案例，和我 brainstorm 这个产品想法：……。请引用具体案例，比较两三个做法和取舍，给一个小验证动作。先讨论，等我确定后再保存为产品假设。

把本地 Brain 文件夹作为 Obsidian vault 打开即可。数据不锁在 Claude 对话里；在其他 Agent 中继续维护时仍先读取现有 Brain 指南。云端执行环境需要导出或单独配置同步。

## 对外发布简介

Brand Research Brain 是一个面向 OPC 个人创业者的 Shopify 研究与学习插件。给它一个感兴趣的品牌网站，从品牌、品类、用户增长、灵感借鉴四个维度学习具体做法，持续积累到自己的知识库，再围绕选品、定位和内容与 Agent 共创。采用 Karpathy LLM Wiki 思路，保存可在 Obsidian 使用的 Markdown，并生成可阅读、截图分享的中文 HTML。中国供应链线索和品牌案例用于提出假设；采购、供应验证、开店和营销执行仍是后续工作。

## 以后进入 Anthropic 目录

GitHub 自建 marketplace 分发与 Anthropic 目录上架是两条路径。先让其他用户从 GitHub 安装并完成实际案例，再考虑目录申请。目录入口为 [claude.ai/directory/manage](https://claude.ai/directory/manage)，选择 Plugin bundle，提供真实仓库、插件路径 `plugins/brand-research-brain` 和跟踪分支或 tag。

按当前 [官方提交指南](https://claude.com/docs/plugins/submit)，目录需要检查 GitHub 写权限、适用计划/角色、插件元数据、README、许可、数据处理、联系方式和合规确认；仓库需要在正式上架前公开。真实主页、仓库地址和联系信息确定后再补入，不使用编造地址。当前包没有远程 MCP 服务器，因此没有自己的 MCP 服务器可另行提交。

本次只准备发布文件和说明，没有提交申请或接受条款。CLI 校验通过不等于目录通过，也不等于所有 Claude 入口都完成了研究测试。

## 已验证与下一次实测

本次在本机 Claude Code 2.1.12 使用 `claude plugin validate` 检查源码插件、marketplace 及解压后的发布包；该旧版本不支持 `--strict`。通用 Python 测试、仓库校验和原有案例重放分别检查保存、渲染、结构与历史兼容性。

尚未在 Claude 对话中执行网站 intake，也未做 Cowork/网页端安装和远程 GitHub 安装验证。正式对外宣称已在 Claude 跑通之前，完成：

1. 空白 Brain 安装并发现三个 skills，贴一个网站，生成可读 Markdown 与 HTML。
2. 在同一 Brain 研究第二个案例，保留旧内容，检查当前案例自己的 ideas 和关联页。
3. 提供已完成的多阶段 growth 笔记，只更新 HTML；阶段、实例、借鉴完整可读，其他部分保留。
4. 用新用户环境从真实 GitHub 地址安装，重复第一步，记录宿主版本与结果。

官方文档核对日期：2026-10-26。后续界面和提交要求变化时，先复核上面的官方链接。
