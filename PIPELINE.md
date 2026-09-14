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

## 4. 校验、提交和报告

1. 在四个文件全部生成后运行 `python scripts/build_site.py`。它校验全部期数，按科技、时政、财经、市场顺序在内存中聚合，市场内部按国际金价、美国股市、中国股市顺序渲染，仅为缺失的报告生成 reports/YYYY-MM-DD.html，再将最新报告复制为 site/index.html，复用已有报告并更新 site/archive.json。每周新增一期时无需重新渲染旧网页；历史 HTML 可以维护修改，也可移除指定一期 HTML 后运行构建重新生成。此处复用旧网页是构建优化，不限制后续修改历史 HTML；历史新闻 JSON 的编辑规则保持不变。
2. 失败时依据明确错误修正本期 JSON，再次校验；不要修改历史数据或放宽 schema 来通过校验。若历史数据阻断构建，报告用户处理。
3. 检查 diff 只包含本期四个 JSON 和新生成的 reports/YYYY-MM-DD.html；不要提交生成的 site/ 或修改规范。将这五个文件放入一个 commit，提交到 main。推送前同步远程，若本期已被其他运行提交则停止，不覆盖。
4. GitHub Actions 自动再次校验、构建和部署 Pages。检查对应 commit 的 workflow 和 Pages 部署状态，成功或失败均报告本期日期、条数、commit、workflow 和网站链接。
5. 无法执行 Python、提交 GitHub 或查看部署时，如实报告阻断步骤，不声称完成。执行环境必须具备联网阅读、仓库读写、Python 3.12 和 jsonschema 能力；普通定时提醒不等同于这些工具权限。

不要修改历史期数、不要自动补做旧期数、不要修改 workflow 或 repo 规则。
