# 市场 / markets

## 1. 模块身份与目标

- module：`markets`；状态：enabled。
- 固定包含美国股市、中国股市、国际金价三个市场；每个市场通常收录 3 条机构观点，允许 2–4 条。
- 仅收录观察窗口内权威机构的最新公开分析，不生成市场现状或模型自己的预测、投资建议、买卖建议、目标仓位与综合“共识”。
- 本文件独立定义本模块的内容要求；执行前读取同目录 `schema.json`。期数、共享窗口和发布流程由 `PIPELINE.md` 定义。

## 2. 内容范围

### 美国股市 / us_equities

重点：机构对美国股票市场、主要指数、估值、盈利前景及风险的分析。不要扩展为个股推荐。

建议优先：BlackRock Investment Institute、Goldman Sachs Research / Insights、UBS CIO、J.P. Morgan Asset Management、MSCI Research 等。

### 中国股市 / china_equities

重点：机构对中国股票市场的分析。不要把香港市场自动等同于中国 A 股；若文章覆盖更广泛的 China equities，摘要中应明确其范围。

建议优先：Goldman Sachs Research / Insights、UBS CIO、BlackRock Investment Institute、MSCI Research、J.P. Morgan Asset Management 等。文章必须实质讨论 China equities / A-shares / Chinese stocks，不因全球资产配置文章仅顺带提及中国就收录。

### 国际金价 / gold

重点：机构对国际金价、供需、驱动因素、前景及风险的分析。

建议优先：World Gold Council / Goldhub、Goldman Sachs Research / Insights、UBS CIO、BlackRock Investment Institute 等。

以上为候选来源，不要求每周所有机构出现。

## 3. 来源与核实

- 必须来自权威研究机构、资产管理机构、投行研究部门、官方行业研究机构或同等可信的 institutional source。
- 本模块仅使用 institutional analysis，不使用 primary / media 来源层级或新闻 items 结构。
- 必须直接阅读正文或足够完整的官方原文；不得只依据搜索摘要、转载摘要或二手媒体转述生成。
- 不使用低质量聚合站、匿名社交媒体、内容农场或无法核实正文的来源。
- 来源可靠性、机构专业权威性和分析是否为最新，均由研究者核实，不能交给结构校验判断。

## 4. 筛选、日期与去重

- 独立执行搜索 → 阅读机构原文 → 来源核实 → 相关性筛选 → 各市场内去重 → 中文摘要 → JSON 输出。
- published_at 使用原始发布时间转换为 UTC 后的 YYYY-MM-DD 日期，必须位于 `[window.start, window.end)`；包含起始日，不包含结束日，不使用检索日期或窗口外文章凑数。
- 同一机构对同一主题的重复或更新分析保留最新一篇，尽量覆盖不同机构。
- 每个市场内按分析内容去重，URL 唯一；同一分析实质涉及多个市场时允许跨市场引用。
- 去除 URL 非必要追踪参数，不破坏有效查询参数。结构校验不能替代内容核查或语义去重。

## 5. 排序与主文选择

- 按机构在该市场的专业权威性、分析的重要性与代表性排序，不按发布时间排序。
- 各市场将最权威且高度相关的机构文章放在 institutional_views 第一条，作为顶部单栏主文；其余在下方双栏展示。
- GPT 负责选择与排序；Python 保留数组顺序，不自行评估或重排观点。

## 6. 中文摘要规范

1. 中文内容是忠实的信息摘要，不是逐句机器翻译；使用自然、清晰、完整的中文。
2. original_title 保留来源原始语言和标题，不翻译；其他语言来源同样保留原文。
3. 摘要说明机构提出了什么判断、依据与主要风险，不只改写标题。
4. 保留重要数字、单位、时间及统计口径，不扩大原文结论。
5. 保留 may / reportedly / according to 等不确定性，可表述为“可能”“据报道”“据某方称”。
6. 明确观点归属，例如“UBS CIO 认为……”。预测、目标价及方向判断必须注明机构，不把预测改成事实或模型建议。
7. 不添加模型自己的分析、推测或投资建议。
8. 每条 summary_zh 建议约 80–250 个中文字符；schema 不严格限制长度。
9. 不同机构观点不一致时分别呈现，不强行合成为“市场共识”。
10. 不添加模型自己的 bullish / bearish 标签、评分或结论，不写“应买入”“应卖出”“适合加仓”等行动建议。

## 7. JSON 输出规范

- 输出路径：`data/issues/YYYY-MM-DD/markets.json`，不添加 Markdown 代码围栏。
- 顶层必须包含 module（固定为 markets）、issue_date、window、markets；issue_date 与目录一致，window 与本期其他模块一致。
- markets 固定包含 us_equities、china_equities、gold；每个市场对象只包含 institutional_views 数组，每个数组 2–4 条。
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
