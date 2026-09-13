# 时政 / politics

## 1. 模块身份与目标

- module：`politics`；状态：enabled。
- 每周通常筛选 7 条具有国际意义的重要新闻，允许轻度浮动；schema 校验范围为 5–8 条。
- 本文件独立定义本模块的内容要求；执行前读取同目录 `schema.json`。期数、共享窗口和发布流程由 `PIPELINE.md` 定义。

## 2. 内容范围

重点：major powers、international relations、wars and conflicts、sanctions、diplomacy、elections with international significance、NATO / EU / UN、international security。

建议来源：官方政府、UN、EU、NATO、国际组织、Reuters、AP、BBC、FT。政府或军方声明必须明确归属；争议事件不得将单方说法当作已确认事实。

## 3. 来源与核实

- Tier A（source_level: primary）：政府、国际组织、UN、EU、NATO、官方统计与研究机构。官方来源的单方立场仍须明确归属。
- Tier B（source_level: media）：Reuters、AP、BBC、Financial Times、Bloomberg、WSJ 和其他高可信主流国际媒体。专业媒体按报道质量和可核实依据判断；TechCrunch 等不因专业定位自动视为原始来源。
- 优先使用最直接、可靠的原始公告；只有媒体有可靠报道时可使用 Tier B。不要要求每周所有候选来源出现。
- 必须阅读原始来源后再写摘要；无法读取或核实的内容，不得只凭搜索摘要生成。
- 低质量转载站、匿名社交媒体、内容农场不得作为重要新闻的唯一来源。
- 官方来源也可能只表达自身立场；声明、预测与争议说法必须明确归属。

## 4. 筛选、日期与去重

- 独立执行搜索 → 阅读原文 → 来源核实 → 重要性筛选 → 模块内去重 → 中文摘要 → JSON 输出。
- 选择在观察窗口内首次发布、具有国际意义的具体事件；优先事实进展和重大政策、产品或数据发布，不收录纯观点、重复跟进或营销噪声。
- published_at 为原始发布时间转换为 UTC 后的 YYYY-MM-DD 日期，必须位于 `[window.start, window.end)`；不得用检索日期替代。
- 同一事件的多篇报道合并为一个 item；保留最直接、可靠的原始链接。模块内 id 和 URL 唯一，跨模块允许同一事件。
- 去除 URL 的非必要追踪参数，但不得破坏有效查询参数。结构校验不能替代事实核查或语义去重。

## 5. 排序与主文选择

- 按新闻重要性与来源权威性排序，不按发布时间排序。
- 将最重要且最具代表性的新闻放在 items 第一条，作为顶部单栏主文；其余按优先级在下方双栏展示。
- GPT 负责选择与排序；Python 保留 JSON 数组顺序，不自行评估内容。

## 6. 中文摘要规范

1. 中文内容是忠实的信息摘要，不是逐句机器翻译；使用自然、清晰、完整的中文。
2. original_title 保留来源原始语言和标题，不翻译。
3. 摘要中除通常不作翻译的特殊名词（如 AI、ChatGPT 等），其他内容全部使用中文表述。
4. 摘要说明具体发生了什么，让读者可以直接了解原文内容。
5. 保留重要数字、单位、时间及统计口径，不扩大原文结论。
6. 保留 may / reportedly / according to 等不确定性，可表述为“可能”“据报道”“据某方称”。
7. 不添加模型自己的分析、推测或投资建议。
8. 每条 summary_zh 建议约 160-300 个中文字符；schema 不严格限制长度。

## 7. JSON 输出规范

- 输出路径：`data/issues/YYYY-MM-DD/politics.json`，不添加 Markdown 代码围栏。
- 顶层必须包含 module（固定为 `politics`）、issue_date、window、items；issue_date 与目录日期一致，window 与本期其他模块一致。
- 每条 item 必须包含下表全部字段。字段类型、数量和额外字段限制以同目录 schema.json 为准，不得自行增添字段。

| 字段 | 要求 |
| --- | --- |
| id | 模块内唯一，建议 `politics-001` 等 |
| category | 具体主题分类 |
| original_title | 来源原始标题，不翻译 |
| source_name | 原始来源名称 |
| source_level | primary 或 media，按本模块来源规则选择 |
| published_at | 原始发布的 UTC 日期，必须在观察窗口内 |
| url | 直接指向原文的 HTTP(S) 链接，不含用户名或密码 |
| summary_zh | 符合本模块摘要规范的中文内容 |

## 8. 完成与失败条件

- 完成本模块全部研究、去重、排序及输出要求后，交由 pipeline 执行校验与发布。
- 不得为凑数虚构事实、日期、来源或链接；不足 5 条可靠新闻时报告失败，不提交不完整期数。
- 不修改历史数据，不放宽 schema 或日期范围来通过校验；发现规范与 schema 冲突时报告用户处理。
