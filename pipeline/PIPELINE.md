# Weekly newsroom pipeline

本文件是每次 Scheduled Task 首先读取的入口。GPT 负责研究和生成 JSON；Python 只做结构校验、聚合、渲染，不负责搜索、新闻理解、翻译或摘要。不调用爬虫或 LLM API。

## 1. 确定本期

- issue_date 为本次约定的周一日期，格式 YYYY-MM-DD。默认采用运行时最近一个已到达的 UTC 周一；延迟执行仍使用该期日期。
- observation window 为 UTC `[issue_date - 7 天, issue_date)`，起始日包含、结束日不包含；三个模块完全一致。published_at 使用来源发布时间转换为 UTC 后的日期，不使用检索日期。
- 目标目录：data/issues/YYYY-MM-DD/。历史期数不得修改。若本期已存在，不覆盖、不追加；报告已存在并停止，任何修订由用户另行授权。

## 2. 读取规范

依次读取 pipeline/EDITORIAL_POLICY.md、pipeline/TRANSLATION_POLICY.md，然后按以下顺序读取每个 enabled module 的 MODULE.md 和 schema.json：

1. technology：modules/technology/（enabled）
2. politics：modules/politics/（enabled）
3. finance：modules/finance/（enabled）

第一版三个模块固定启用；这里不是动态插件注册系统。增删模块时需同步修改构建脚本的 MODULES 和测试。

## 3. 依次完成三个模块

每个模块独立完成：新闻搜索 → 阅读原始来源 → 来源核实 → 重要性筛选 → 模块内部事件去重 → 中文摘要 → JSON 输出。先完成 technology，再 politics，最后 finance。

- 每个模块 5–8 条；不得为凑数虚构事实、日期、来源或链接。找不到足够可靠新闻时报告失败，不提交不完整期数。
- 同一事件的多篇报道合并为一个 item；保留最可靠、最直接的原始链接。跨模块允许同一事件，不做跨模块语义去重。
- 严格使用对应 schema 的字段和类型，保留原始标题和 URL，不添加 Markdown 代码围栏。
- 分别写入 data/issues/YYYY-MM-DD/technology.json、politics.json、finance.json。
- 正式数据不得复用 demo 新闻或 example.com 占位链接。

## 4. 校验、提交和报告

1. 在三个文件全部生成后运行 `python scripts/build_site.py`。它校验全部期数，按科技、时政、财经顺序在内存中聚合，然后重建 site/index.html 和 site/reports/YYYY-MM-DD.html。
2. 失败时依据明确错误修正本期 JSON，再次校验；不要修改历史数据或放宽 schema 来通过校验。若历史数据阻断构建，报告用户处理。
3. 检查 diff 只包含本期三个 JSON；不要提交生成的 site/ 或修改规范。将本期三个文件放入一个 commit，提交到 main。推送前同步远程，若本期已被其他运行提交则停止，不覆盖。
4. GitHub Actions 自动再次校验、构建和部署 Pages。检查对应 commit 的 workflow 和 Pages 部署状态，成功或失败均报告本期日期、条数、commit、workflow 和网站链接。
5. 无法执行 Python、提交 GitHub 或查看部署时，如实报告阻断步骤，不声称完成。执行环境必须具备联网阅读、仓库读写、Python 3.12 和 jsonschema 能力；普通定时提醒不等同于这些工具权限。

不要修改历史期数、不要自动补做旧期数、不要修改 workflow 或 repo 规则。示例期 2026-09-07 是虚构演示，不属于生产新闻。
