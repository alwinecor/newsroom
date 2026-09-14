# 财经 / finance

## 1. 模块身份与目标

- module：`finance`；状态：enabled。
- 每周通常筛选 5 篇国际权威机构的宏观经济与金融分析，允许轻度浮动；schema 校验范围为 4–6 条。
- 本文件独立定义本模块的内容要求；执行前读取同目录 `schema.json`。期数、共享窗口和发布流程由 `PIPELINE.md` 定义。

## 2. 内容范围

Finance 聚焦 **全球宏观经济与金融环境**，优先收录以下类型的实质性机构分析：

### 全球经济与通胀

包括全球及主要经济体的增长、通胀、就业、生产率、经济周期、需求与供给冲击等。

### 货币政策与利率

包括 Federal Reserve、ECB、Bank of England、Bank of Japan、PBoC 及其他主要央行的政策路径、利率前景、政策传导及全球货币政策分化。

### 债券、汇率与金融条件

包括主权债、长期与短期收益率、期限溢价、信用环境、美元与主要货币、全球资本流动、融资条件及金融稳定。

### 财政、贸易与结构性宏观问题

包括公共债务、财政政策、税收、关税、国际贸易、能源冲击、产业与劳动力结构变化，以及其他具有国际影响的宏观经济问题。

## 3. 来源与核实

以下为优先来源池，不要求每周所有机构出现。

### S+：国际公共与准公共经济研究机构

- IMF
- BIS
- OECD
- World Bank
- Federal Reserve research / FEDS Notes
- ECB Blog / Economic Bulletin / research
- Bank of England research
- Bank of Japan research
- 其他具有同等国际影响力的主要央行研究部门或多边经济机构

### S：全球宏观与投资研究机构

- BlackRock Investment Institute
- J.P. Morgan Asset Management / Global Research
- UBS CIO / UBS Investment Research
- Goldman Sachs Research / Insights
- Morgan Stanley Research

### A+

- PIMCO
- Vanguard Investment Strategy Group
- Amundi Investment Institute
- Schroders
- Fidelity International
- Capital Group
- State Street Global Advisors
- 以及具有同等全球宏观研究能力的大型机构

筛选时遵循：**分析相关性、公开可读性与深度优先；机构权威性用于同等候选之间排序。**

一篇来自较低优先级机构、但对本周核心宏观问题有完整且高质量分析的文章，可以优于一篇顶级机构仅顺带提及该主题的内容。

- 必须直接阅读正文或足够完整的官方原文；不得仅依据搜索结果摘要、转载摘要、媒体转述或二手引用生成摘要。
- 优先选择能够解释经济机制、政策路径、金融条件和结构性变化的分析。
- 机构观点、预测与判断必须明确归属，不得改写为已确认事实。
- S+、S、A+ 是本模块的候选来源优先级，不是 JSON 字段或枚举。每篇文章均须直接来自机构原文，不另设来源类型字段。

## 4. 筛选、日期与去重

- 独立执行搜索 → 阅读原文 → 来源核实 → 重要性筛选 → 模块内去重 → 中文摘要 → JSON 输出。
- published_at 为原始发布时间转换为 UTC 后的 YYYY-MM-DD 日期，必须位于 `[window.start, window.end)`；不得用检索日期替代。
- 同一机构对同一主题的重复或更新分析通常只保留最新、最完整的一篇。
- 不同机构实质讨论同一问题时，通常只保留 **1–2 篇解释框架或观点明显不同的代表文章**。
- 去除 URL 的非必要追踪参数，但不得破坏有效查询参数。结构校验不能替代事实核查或语义去重。

## 5. 排序与主文选择

Finance 是统一的宏观栏目，不应被单一主题完全占据。

- 除非单一事件在当周具有压倒性重要性，否则最终入选内容原则上应覆盖 **至少 3 个不同宏观主题或经济体**。
- 当多个高质量机构都讨论同一主题时，应优先保留：
  1. 解释框架更完整的文章；
  2. 对全球影响更明确的文章；
  3. 观点或分析路径彼此有明显差异的文章。

- 按以下因素综合排序，不按发布时间排序：
  1. 对本周全球宏观环境的重要性；
  2. 分析深度与解释力；
  3. 国际影响范围；
  4. 机构权威性与专业代表性。
- 将最重要、最具代表性的一篇放在数组第一条，作为 Finance 顶部单栏主文。
- GPT 负责选择与排序；Python 保留数组顺序，不自行评估或重排。

## 6. 中文摘要规范

1. 中文内容是忠实的信息摘要，不是逐句机器翻译；使用自然、清晰、完整的中文。
2. original_title 保留来源原始语言和标题，不翻译。
3. 摘要中除通常不作翻译的特殊名词（如 AI、GDP 等），其他内容全部使用中文表述。
4. 摘要说明具体发生了什么，让读者可以直接了解原文内容。
5. 保留重要数字、单位、时间及统计口径，不扩大原文结论。
6. 保留 may / reportedly / according to 等不确定性，可表述为“可能”“据报道”“据某方称”。
7. 不添加模型自己的分析、推测或投资建议。
8. 每条 summary_zh 建议约 160-300 个中文字符；schema 不严格限制长度。

## 7. JSON 输出规范

- 输出路径：`data/issues/YYYY-MM-DD/finance.json`，不添加 Markdown 代码围栏。
- 顶层必须包含 module（固定为 `finance`）、issue_date、window、items；issue_date 与目录日期一致，window 与本期其他模块一致。
- 每条 item 必须包含下表全部字段。字段类型、数量和额外字段限制以同目录 schema.json 为准，不得自行增添字段。

| 字段 | 要求 |
| --- | --- |
| id | 模块内唯一，建议 `finance-001` 等 |
| category | 具体主题分类 |
| original_title | 来源原始标题，不翻译 |
| source_name | 原始来源名称 |
| published_at | 原始发布的 UTC 日期，必须在观察窗口内 |
| url | 直接指向原文的 HTTP(S) 链接，不含用户名或密码 |
| summary_zh | 符合本模块摘要规范的中文内容 |

## 8. 完成与失败条件

- 完成本模块全部研究、去重、排序及输出要求后，交由 pipeline 执行校验与发布。
- 不得为凑数虚构事实、日期、来源或链接；不足 4 篇可靠文章时报告失败，不提交不完整期数。
- 不修改历史数据，不放宽 schema 或日期范围来通过校验；发现规范与 schema 冲突时报告用户处理。
