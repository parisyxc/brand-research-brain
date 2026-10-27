# Brand Research Brain

Learn from a brand website, article or clip. Understand the business, learn three concrete practices, and save linked Shopify research plus readable Chinese HTML. Thin evidence can yield fewer practices.

## Skills

- `brain-init`: create a personal Shopify research and learning Brain.
- `brand-intake`: learn from a case and accumulate substantive category, idea, storefront and growth knowledge.
- `growth-research`: on request, investigate social media, creators and SEO, or present an existing full study in HTML.

Skills use Python 3.9+ standard-library helpers. The host must provide file access, execution, and browsing/search for live website research. No remote server, Shopify account, separate model API key or paid research provider is bundled.

## Claude Code

After extracting the standalone plugin ZIP into a folder, load that folder with `claude --plugin-dir ./brand-research-brain`. For persistent installation, use the source repository's marketplace and install `brand-research-brain@brand-research-brain`.

In a Claude Code session:

```text
/brand-research-brain:brain-init
/brand-research-brain:brand-intake
/brand-research-brain:growth-research
```

Tell the skill the actual Brain path and research material. Read and follow the skill's linked contracts before using its scripts; saving and rendering are separate steps. Claude Code-specific metadata is in `.claude-plugin/plugin.json`; the same skill bodies serve the portable/Codex package.

## 中文使用

先指定一个自己的文件夹：

> 创建一个中文 Shopify 学习 Brain。我正在探索品类，想学习选品、定位和内容。

然后给一个网站：

> 继续使用刚才的 Brain，研究这个网站：URL。讲清生意和本案品类亮点，学三个具体方法，沉淀当前案例自己的 ideas，并生成中文 HTML。

已有 Brain 先读 `AGENTS.md`、`BRAIN.md`、`brain.json` 和相关笔记。保留 raw、用户偏好与已有学习。不要把插件目录作为 Brain。

用 Obsidian 打开本地 Brain 即可阅读。云端会话需要另行导出或同步；安装插件不等于拥有本机文件权限。Claude Code、Cowork 和网页聊天的文件能力不同，使用前确认实际工作目录与 Python 能力。

## Data and licensing

The plugin saves source material and knowledge to the Brain selected by its user. Website research uses the host's retrieval tools and quotas. It does not automatically contact people, publish, buy products, connect paid providers, or enable monitoring.

Original code, instructions and summaries are MIT licensed, copyright Paris Young. Third-party brands and source material retain their own rights. The containing repository has the full release and validation notes. Packaging/manifest checks do not establish agent research quality or successful installation in every Claude surface.
