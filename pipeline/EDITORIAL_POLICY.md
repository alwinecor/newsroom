# Editorial policy

以下新闻筛选、primary/media 层级和 item 字段规则适用于 technology、politics、finance。Markets 遵循 modules/markets/MODULE.md 的专用规则：snapshot 使用一手市场数据；institutional_views 使用可直接阅读的机构分析，允许明确归属的观点和预测。机构分析不自动归为 primary 或 media；World Gold Council / Goldhub 等行业研究不等同于交易所或监管机构的一手市场数据。机构观点优先观察窗口内，不足时可回溯至 issue_date 前 30 天；snapshot 来源页无需 published_at。来源可靠、直接阅读、保留不确定性和不得虚构的原则仍适用。

选择在观察窗口内首次发布、具有国际意义的具体事件。优先事实进展与重大政策、产品或数据发布；不收录纯观点、重复跟进或营销噪声。阅读原始来源后才写摘要。

## 来源优先级

Tier A（source_level: primary）：政府、国际组织、官方统计机构、央行、公司官方公告、官方研究机构、GitHub 官方 repository / release、官方博客。

Tier B（source_level: media）：Reuters、AP、BBC、Financial Times、Bloomberg、WSJ 和其他高可信主流国际媒体。TechCrunch 等专业媒体需按其报道质量和可核实依据判断，不将转载自动视为原始来源。

低质量转载站、匿名社交媒体、内容农场不得作为重要新闻的唯一来源。官方来源也可能仅表达其自身立场；声明、预测和争议说法必须明确归属。无法读取或核实的内容不得仅凭搜索摘要写成已确认事实。

## 每条新闻必须保存

- original_title：来源原始标题，保留原文。
- source_name：来源名称。
- published_at：原始发布时间对应的 UTC 日期。
- url：直接指向报道或公告的 HTTP(S) 原始链接。
- summary_zh：忠实中文摘要。

同时按 schema 提供 id、category、source_level。每个模块独立按事件去重，URL 和 id 在模块内唯一；URL 去除非必要追踪参数后再保存，勿破坏有效查询参数。结构校验不替代事实核查或语义去重。
