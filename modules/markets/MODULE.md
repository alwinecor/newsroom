# 市场 / markets

状态：enabled。每周固定生成三个市场板块：美国股市、中国股市、国际金价。

## 目标

每个市场只收录 **2–3 条机构观点（institutional_views）**，来自观察窗口内发布的权威机构最新公开分析，忠实概括机构自身判断。

Markets 不提供模型自己的市场预测、投资建议、买卖建议、目标仓位或综合“共识”。

## 固定市场

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

## Institutional views 规则

每个市场筛选 2–3 条机构观点：

- 必须来自权威研究机构、资产管理机构、投行研究部门、官方行业研究机构或同等可信的 institutional source。
- 必须直接阅读正文或足够完整的官方原文；不得只根据搜索结果摘要、转载摘要或二手媒体转述生成。
- `published_at` 必须在 UTC 观察窗口 `[window.start, window.end)` 内，包含起始日、不包含结束日。使用真实发布日期，不使用检索日期；不得回溯窗口外文章凑数。
- 在相关且可靠的分析中优先选择最新文章。同一机构对同一主题的重复或更新分析保留最新一篇；按发布日期倒序输出，尽量覆盖不同机构。
- 每个市场内按分析内容去重，URL 唯一。分析实质涉及多个市场时允许跨市场引用。
- 必须保存 institution、original_title、published_at、url、summary_zh；URL 直接指向机构原文。
- `original_title` 保留来源原始标题，不翻译。
- `summary_zh` 忠实概括该机构的判断、理由与主要风险，不把机构预测改写为已确认事实。
- 预测、目标价、市场方向判断必须明确归属，例如“Goldman Sachs Research 预计……”“UBS CIO 认为……”。
- 不同机构观点不一致时分别呈现，不强行合成为“市场共识”。
- 不添加模型自己的 bullish / bearish 标签、评分或结论。

## 写作与来源规则

`pipeline/EDITORIAL_POLICY.md` 对新闻模块定义的 `primary / media` 层级不直接套用到机构观点。本模块仅使用 institutional analysis。

不要使用低质量聚合站、匿名社交媒体、内容农场或无法核实正文的来源。不要提供投资建议，不写“应买入”“应卖出”“适合加仓”等行动建议。

## 输出

输出 `data/issues/YYYY-MM-DD/markets.json`；`module` 必须为 `markets`。

固定包含 `markets.us_equities`、`markets.china_equities`、`markets.gold`，每个市场对象只包含 `institutional_views` 数组。

`issue_date`、`window` 与其他模块保持一致，遵循 `pipeline/PIPELINE.md`。三个市场全部生成成功后才算本模块完成。任一市场在窗口内不足 2 条可靠分析时报告失败，不提交不完整期数，不虚构内容或放宽日期范围。
