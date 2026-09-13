# 市场 / markets

状态：enabled。每周固定生成三个市场板块：美国股市、中国股市、国际金价。

## 目标

每个市场板块必须同时包含：

1. **市场现状（snapshot）**：仅依据 primary sources，对观察窗口内截至最新可用交易日的市场状态进行中文事实摘要。
2. **机构观点（institutional_views）**：筛选 1-2 篇可直接读取、与该市场高度相关的权威机构公开分析，忠实概括机构自身判断。

Markets 不提供模型自己的市场预测、投资建议、买卖建议、目标仓位或综合“共识”。

## 固定市场

### 美国股市 / us_equities

重点：S&P 500 等主要美国股票指数的周度表现、年内表现、市场广度或其他能够由一手数据直接支持的重要状态变化。不要扩展为个股推荐。

Primary sources 建议优先：S&P Dow Jones Indices、Nasdaq、NYSE 及其他官方指数提供商、交易所或监管机构。

Institutional analysis 建议优先：BlackRock Investment Institute、Goldman Sachs Research / Insights、UBS CIO、J.P. Morgan Asset Management、MSCI Research 等。

### 中国股市 / china_equities

重点：A 股主要指数及中国股票市场的周度表现和可由一手来源直接支持的重要市场状态。不要把香港市场自动等同于中国 A 股；若分析文章覆盖更广泛的 China equities，摘要中应明确其范围。

Primary sources 建议优先：上海证券交易所（SSE）、深圳证券交易所（SZSE）、中证指数有限公司（CSI）及其他官方交易所或指数提供商。

Institutional analysis 建议优先：Goldman Sachs Research / Insights、UBS CIO、BlackRock Investment Institute、MSCI Research、J.P. Morgan Asset Management 等。文章必须实质讨论 China equities / A-shares / Chinese stocks，不因全球资产配置文章仅顺带提及中国就收录。

### 国际金价 / gold

重点：国际黄金价格的周度变化及能够由一手来源直接支持的重要市场状态；必要时可补充 COMEX 黄金期货仓位、上海金基准价等事实信息。

Primary sources 建议优先：LBMA、Shanghai Gold Exchange（SGE）、U.S. Commodity Futures Trading Commission（CFTC）及其他官方 benchmark、交易所或监管机构。

Institutional analysis 建议优先：World Gold Council / Goldhub、Goldman Sachs Research / Insights、UBS CIO、BlackRock Investment Institute 等。World Gold Council 属于行业研究 / institutional analysis，不与交易所或监管机构的 primary data 混为同一来源角色。

## Snapshot 规则

每个市场必须生成一个 snapshot：

- `as_of`：观察窗口内最新可用市场数据对应的日期，格式 YYYY-MM-DD；通常为 issue_date 前最后一个有效交易日。
- `summary_zh`：使用自然中文说明“当前市场发生了什么”，重点描述本周表现和重要状态，不加入模型推测。
- `sources`：1–3 个直接支持 snapshot 的 primary sources。
- Snapshot source 可以是持续更新的数据页、指数页、官方统计页或 benchmark 页面，因此不强制要求来源本身有 `published_at`。
- 每个 source 必须保存 `source_name`、`source_title` 和直接 HTTP(S) URL。
- 若不同 primary sources 的口径不同，摘要必须说明指标口径，不能混合成一个未经来源支持的数字。
- 不使用媒体报道替代能够直接取得的一手市场数据。

## Institutional views 规则

每个市场筛选 1-2 条机构观点：

- 必须来自研究机构、资产管理机构、投行研究部门、官方行业研究机构或同等可信的 institutional source。
- 必须能够直接读取正文或足够完整的官方原文；不得只根据搜索结果摘要、转载摘要或二手媒体转述生成。
- 优先选择观察窗口内发布的文章；若观察窗口内没有足够相关、可直接读取的高质量机构分析，可以使用 issue_date 前最近 30 天内的最新相关公开分析。
- 必须保存 institution、original_title、published_at、url、summary_zh。
- `original_title` 保留来源原始标题，不翻译。
- `summary_zh` 忠实概括该机构的判断、理由与主要风险，不把机构预测改写为已确认事实。
- 预测、目标价、市场方向判断必须明确归属，例如“Goldman Sachs Research 预计……”“UBS CIO 认为……”。
- 不同机构观点不一致时分别呈现，不强行合成为“市场共识”。
- 不添加模型自己的 bullish / bearish 标签、评分或结论。

## 写作与来源规则

`pipeline/EDITORIAL_POLICY.md` 对新闻模块定义的 `primary / media` 层级不直接套用到 institutional views。本模块通过结构本身区分：

- `snapshot.sources` = primary sources
- `institutional_views` = institutional analysis

不要使用低质量聚合站、匿名社交媒体、内容农场或无法核实正文的来源。

不要提供投资建议，不写“应买入”“应卖出”“适合加仓”等行动建议。

## 输出

输出 `data/issues/YYYY-MM-DD/markets.json`；`module` 必须为 `markets`。

固定包含：

- `markets.us_equities`
- `markets.china_equities`
- `markets.gold`

三个市场全部生成成功后才算本模块完成。不得为了填满结构虚构数据、来源或机构观点。

`issue_date`、`window` 与其他模块保持一致，遵循 `pipeline/PIPELINE.md`。Snapshot 的 `as_of` 必须位于观察窗口 `[window.start, window.end)` 内。

机构观点的 `published_at` 优先位于观察窗口内；若使用本文件允许的 30 天回溯规则，必须保留真实发布日期，不得改写为观察窗口内日期。
