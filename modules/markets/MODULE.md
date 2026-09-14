# 市场 / markets

## 1. 模块身份与目标

- module：`markets`；状态：enabled。
- 固定按国际金价、美国股市、中国股市的顺序展示三个市场；每个市场通常收录 3 篇机构分析，允许 2–4 篇。
- 仅收录观察窗口内权威机构的最新公开分析，不生成市场现状或模型自己的预测、投资建议、买卖建议、目标仓位与综合“共识”。
- 本文件独立定义本模块的内容要求；执行前读取同目录 `schema.json`。期数、共享窗口和发布流程由 `PIPELINE.md` 定义。

## 2. 内容范围

### 国际金价 / gold

收录国际权威机构对黄金市场及国际金价的实质性分析，包括央行购金、投资需求与 ETF 资金流、期货及市场仓位、实际利率、美元、通胀、地缘政治、供需关系及其他重要价格驱动因素。候选文章必须以黄金为核心分析对象，或在更广泛的大宗商品、宏观经济或资产配置文章中包含内容充分、可以独立概括的黄金分析部分。

按以下优先级寻找候选来源：

1. **S+**：World Gold Council / Goldhub、UBS CIO / UBS Investment Research。
2. **S**：Goldman Sachs Research / Insights、J.P. Morgan Global Research。
3. **A+**：BlackRock Investment Institute、Standard Chartered CIO、Morgan Stanley Research。
4. **A**：State Street Global Advisors、WisdomTree Research、Amundi Investment Institute、Schroders，以及具有同等国际研究能力的大型全球资产管理、商品研究或投资机构。

建议将 World Gold Council 持续发布的 Weekly Markets Monitor 作为本市场排序最高的稳定核心源。

### 美国股市 / us_equities

收录国际权威机构对美国股票市场的实质性分析，包括 S&P 500、Nasdaq、Russell 2000、美国大盘股与小盘股、市场估值、企业盈利、市场广度及其他明确界定的美国股票市场范围。候选文章必须以美国股市为核心分析对象，或在更广泛的全球资产配置文章中包含内容充分、可以独立概括的美国股票分析部分。

按以下优先级寻找候选来源：

1. **S+**：BlackRock Investment Institute、UBS CIO / UBS Investment Research、J.P. Morgan Asset Management。
2. **S**：Goldman Sachs Research / Insights、Morgan Stanley Research。
3. **A+**：Fidelity International、Capital Group、State Street Global Advisors、MSCI Research。
4. **A**：Vanguard Investment Strategy Group、Schroders、Amundi Investment Institute、T. Rowe Price，以及具有同等国际研究能力的大型全球资产管理或研究机构。

### 中国股市 / china_equities

收录国际权威机构对中国股票市场的实质性分析，包括 A-shares、H-shares、offshore China equities、MSCI China、China Tech 或其他明确界定的中国股票市场范围。候选文章必须以中国股市为核心分析对象，或在更广泛的全球、亚洲或新兴市场文章中包含内容充分、可以独立概括的中国股票分析部分。

按以下优先级寻找候选来源：

1. **S+**：UBS CIO / UBS Investment Research、HSBC Global Research / HSBC Private Bank、J.P. Morgan Asset Management。
2. **S**：Goldman Sachs Research / Insights、Morgan Stanley Research。
3. **A+**：BlackRock Investment Institute、MSCI Research。
4. **A**：Fidelity International、Schroders、Capital Group、Amundi Investment Institute，以及具有同等国际研究能力的大型全球资产管理或研究机构。

## 3. 来源与核实

- 筛选时遵循 **分析相关性、公开可读性与深度优先，机构权威性用于同等候选之间排序** 的原则。一篇来自较低优先级机构、但深度完整分析美国股票/中国股票/黄金市场的文章，可以优于一篇顶级机构仅顺带提及相关市场的文章；但在相关性和分析深度相当时，应优先收录更高优先级机构。
- 必须直接阅读正文或足够完整的官方原文；不得只依据搜索摘要、转载摘要或二手媒体转述生成。

## 4. 筛选、日期与去重

- 独立执行搜索 → 阅读机构原文 → 来源核实 → 相关性筛选 → 各市场内去重 → 中文摘要 → JSON 输出。
- published_at 使用原始发布时间转换为 UTC 后的 YYYY-MM-DD 日期，必须位于 `[window.start, window.end)`；包含起始日，不包含结束日，不使用检索日期或窗口外文章凑数。
- 每个市场内按分析内容去重，URL 唯一。
- 去除 URL 非必要追踪参数，不破坏有效查询参数。结构校验不能替代内容核查或语义去重。

## 5. 排序与主文选择

- 按机构在该市场的专业权威性、分析的重要性与代表性排序，不按发布时间排序。
- 各市场将最权威且高度相关的机构文章放在第一条，作为顶部单栏主文；其余在下方双栏展示。
- GPT 负责选择与排序；Python 保留数组顺序，不自行评估或重排观点。

## 6. 中文摘要规范

1. 中文内容是忠实的信息摘要，不是逐句机器翻译；使用自然、清晰、完整的中文。
2. original_title 保留来源原始语言和标题，不翻译。
3. 摘要中除通常不作翻译的特殊名词（如 AI、ChatGPT 等），其他内容全部使用中文表述。
4. 摘要说明机构提出了什么判断、依据与主要风险，让读者可以直接了解机构观点。
5. 保留重要数字、单位、时间及统计口径，不扩大原文结论。
6. 保留 may / reportedly / according to 等不确定性，可表述为“可能”“据报道”“据某方称”。
7. 不添加模型自己的分析、推测或投资建议。
8. 每条 summary_zh 建议约 160-300 个中文字符；schema 不严格限制长度。

## 7. JSON 输出规范

- 输出路径：`data/issues/YYYY-MM-DD/markets.json`，不添加 Markdown 代码围栏。
- 顶层必须包含 module（固定为 markets）、issue_date、window、markets；issue_date 与目录一致，window 与本期其他模块一致。
- markets 固定按 gold、us_equities、china_equities 顺序输出；每个市场对象只包含 institutional_views 数组，每个数组 2–4 条。
- 每条观点必须包含下表全部字段。字段类型和额外字段限制以同目录 schema.json 为准，不得自行增添字段。

| 字段 | 要求 |
| --- | --- |
| institution | 发布分析的机构名称 |
| original_title | 机构原文标题，不翻译 |
| published_at | 原始发布的 UTC 日期，必须在观察窗口内 |
| url | 直接指向机构原文的 HTTP(S) 链接，不含用户名或密码 |
| summary_zh | 概括机构判断、理由与风险，明确归属 |

## 8. 完成与失败条件

- 三个市场全部完成研究、去重、排序及输出要求后，才算本模块完成，交由 pipeline 校验与发布。
- 任一市场不足 2 条可靠分析时报告失败，不提交不完整期数，不虚构内容或放宽日期范围。
- 不修改历史数据，不放宽 schema 来通过校验；发现规范与 schema 冲突时报告用户处理。
