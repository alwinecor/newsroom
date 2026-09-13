# Translation policy

中文内容不是逐句机器翻译，而是忠实的中文信息摘要。

1. 保留英文原始标题，不翻译 original_title 字段；来源使用其他语言时也保留原文。
2. summary_zh 使用自然、清晰、完整的中文。
3. 摘要必须说明“具体发生了什么”。
4. 不只改写标题。
5. 保留重要数字、单位和时间。
6. 不扩大原文结论。
7. 保留 may / reportedly / according to 等不确定性，例如“可能”“据报道”“据某方称”。
8. 官方声明要说明是谁说的。
9. 不添加模型自己的分析、推测或投资建议。
10. 每条摘要建议约 80–250 个中文字符；schema 不严格限制长度。

Markets 补充：snapshot.summary_zh 描述一手数据支持的市场现状，并保留指标口径及截至日期；institutional_views[].summary_zh 概括该机构自身判断、理由和风险，明确归属，不能把预测改成事实或模型建议。机构文章的 original_title 及 snapshot 来源的 source_title 均保留原文。
