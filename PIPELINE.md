# Weekly newsroom pipeline

本文件是每次 Scheduled Task 首先读取的入口。GPT 负责研究和生成 JSON；Python 只做结构校验、聚合、渲染，不负责搜索、新闻理解、翻译或摘要。不调用爬虫或 LLM API。

## 1. 确定本期

- issue_date 为本次约定的周一日期，格式 YYYY-MM-DD。默认采用运行时最近一个已到达的 UTC 周一；延迟执行仍使用该期日期。
- observation window 为 UTC `[issue_date - 7 天, issue_date)`，起始日包含、结束日不包含；四个模块完全一致。published_at 使用来源发布时间转换为 UTC 后的日期，不使用检索日期。
- 目标目录：data/issues/YYYY-MM-DD/。历史期数不得修改。若本期已存在，不覆盖、不追加；报告已存在并停止，任何修订由用户另行授权。

## 2. 读取规范

读完本总纲后，按以下顺序直接读取每个 enabled module 的 MODULE.md，再读取同目录 schema.json。MODULE.md 独立定义该模块的全部内容规则，包括范围、来源、筛选、排序、中文摘要、字段与失败条件；不得将其他模块的内容规范自动套用到本模块。schema.json 定义可执行的结构约束，若与模块规范冲突应报告用户处理，不自行放宽规则：

1. technology：modules/technology/（enabled）
2. politics：modules/politics/（enabled）
3. finance：modules/finance/（enabled）
4. markets：modules/markets/（enabled）；内部分区为国际金价（gold）→ 美国股市（us_equities）→ 中国股市（china_equities）。

四个模块固定启用，所有期数（包括 2026-09-07）都必须提供 markets.json，缺少时校验失败。不要自动补写历史数据，应报告用户处理；这里不是动态插件注册系统。增删模块时需同步修改构建脚本的 MODULES 和测试。

## 3. 依次完成四个模块

- 按第 2 节顺序分别执行模块自己的 MODULE.md，完成其研究、核实、筛选、去重、摘要、排序和 JSON 输出要求。条数、来源层级、内容字段和主文选择均以该模块规范为准。
- 每个模块写入 `data/issues/YYYY-MM-DD/<module>.json`；日期与共享窗口保持一致，结构严格符合对应 schema，不添加 Markdown 代码围栏。
- 模块独立完成，不做跨模块语义去重；不得虚构内容或替其他模块放宽要求。
- 所有 enabled modules 全部成功才进入本期校验与发布。任一模块失败，报告具体模块及原因，不提交不完整期数。

## 4. 提交 JSON 与自动发布

1. 四个模块完成后，检查字段、条数、来源和数组顺序符合各 MODULE.md 与 schema.json。
2. 推送前同步 main；若本期已被其他运行提交则停止，不覆盖。检查 diff 只包含本期四个 JSON，将它们放在一个 commit 中推送到 main。
3. GitHub Actions 自动运行测试、校验全部期数，并只为缺失报告生成 reports/YYYY-MM-DD.html。已有网页直接复用；最新报告复制到 site/index.html，归档导航自动更新。
4. Actions 使用 GITHUB_TOKEN 将新报告自动提交回 main，然后上传网站并部署 Pages。报告提交失败或远程发生并发更新时停止部署，不强推；由后续运行或手动 workflow_dispatch 基于最新 main 重试。
5. 检查 JSON commit 对应的 Actions 运行，确认测试、报告回写与 Pages 部署完成；成功或失败均报告本期日期、各模块条数、JSON commit、workflow 和网站链接。失败时报告具体错误，当前网站保持上次成功部署版本。
6. 校验失败后，不自动修改历史期数或放宽规则。本期 JSON 已提交后的修订同样需要用户授权；修订后再次推送触发自动构建。若只需重试临时部署失败，可重跑 workflow，无需改写数据。
7. 不要修改历史期数、不要自动补做旧期数、不要修改 workflow 或 repo 规则。
