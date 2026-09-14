# Modular AI Newsroom

## What it is

AI-generated modular international news digest. 一个最小可用的国际新闻周报 pipeline，提供中文摘要并保留原始标题与来源。纯静态 HTML + CSS，支持 Python 3.12 / 3.13，唯一直接依赖为 jsonschema。

## Architecture

- ChatGPT：research + selection + deduplication + Chinese summaries。
- Repository：rules + schemas + validation + rendering。
- GitHub Actions：test + validate + render + commit reports + deploy。

本仓库不联网搜索新闻，不包含爬虫或 LLM API。四个模块独立生成 JSON，Python 校验全部历史期数，在内存中按固定顺序聚合新期数，复用已有报告并组装静态发布目录；不额外保存聚合 JSON。

## Modules

- Technology / 科技
- Politics / 时政
- Finance / 宏观经济与金融
- Markets / 国际金价、美国股市、中国股市

入口是 [PIPELINE.md](PIPELINE.md)，各模块在 modules/ 下分别拥有 MODULE.md 和 schema.json。前三个新闻模块使用相同的 items 结构，通常各 7 条（校验保留 5–8 条以兼容已有数据）；markets 使用独立结构，固定包含三个市场，institutional_views 收录观察窗口内发布的权威机构最新公开分析：国际金价与美国股市通常 3 篇、允许 2–4 篇，中国股市允许 1–3 篇，详见 [Markets 规范](modules/markets/MODULE.md)。

阅读路径为 `PIPELINE.md → modules/<module>/MODULE.md → schema.json`。Pipeline 只定义期数、共享窗口、模块执行顺序和发布流程；各 MODULE.md 独立包含该模块的完整编辑与中文摘要规范，不继承全局内容政策，也不依赖其他模块。

MODULE.md 统一采用八节格式：模块身份与目标、内容范围、来源与核实、筛选/日期/去重、排序与主文选择、中文摘要规范、JSON 输出规范、完成与失败条件。可以复制该章节结构编写新模块，但需按模块内容重新定义规则；涉及字段或条数变化时同步修改对应 schema。新增模块还需接入 pipeline 列表、构建脚本的校验/渲染与测试，不会仅凭新增文件自动启用。

接入代码不会自动刷新已有 HTML；经授权补齐数据后，若需更新旧页面，可移除对应报告并运行构建。

## Manual test

```sh
python -m pip install -r requirements.txt
python scripts/build_site.py
python -m unittest discover -s tests
python -m http.server 8000 --directory site
```

浏览器访问 http://localhost:8000。根 URL 直接显示最新一期。完整归档导航通过 HTTP(S) 加载 archive.json；直接打开本地 HTML 时仅保留当期导航。CI 使用 requirements.txt 中的 jsonschema 主版本范围。

正式数据位于 data/issues/YYYY-MM-DD/。每期按科技、时政、财经、市场顺序使用 editorial / newspaper 版式，左侧抽屉按年份和日期倒序展示归档。Markets 沿用衬线标题、分隔线及双列布局，三个市场分别展示机构观点及原文链接，各以首条为顶部单栏主文，其余在下方双栏展示，不再显示重复的机构观点副标题。所有模块按重要性与权威性排序；前三模块首条是最重要的代表性新闻，每个市场首条是最权威的机构文章。GPT 写入数组顺序，Python 保留顺序，不按日期重排。顶部新闻条数和新闻来源统计仅计算前三个模块，另列市场板块数与机构观点数，避免混淆来源角色。

发布源为 Git 跟踪的 `reports/YYYY-MM-DD.html`。默认构建只渲染不存在的报告，已有网页直接复用，避免发布新一期时重复渲染历史。历史 HTML 可以修改；也可以移除需要重新生成的那一期 HTML，再运行构建，使用现有 JSON 和当前模板重新生成该期。其他报告仍直接复用。CSS 与归档脚本继续内嵌在报告中，因此模板调整在该期重新生成后生效。

`site/` 是不提交 Git 的部署产物，包含最新报告的完整副本 `index.html`、全部报告的字节副本 `reports/`、动态归档清单 `archive.json` 和 `.nojekyll`。历史页每次打开时用少量原生 JavaScript 读取最新清单，因此更新 sidebar 不需要重写任何旧报告。请求失败时保留当期链接。支持 GitHub project Pages 子路径，无额外依赖。

每次新增一期：GPT 只提交本期四个 JSON。Actions 运行测试和构建检查，使用 Python 生成缺失报告。机器人仅将 reports/ 的新增报告提交回 main，然后部署 site/；没有新报告时跳过自动 commit，仍可重新部署。已有报告直接复用，不依赖缓存或过期 artifact。`--check-published` 保留为可选本地检查。

报告回写使用 GITHUB_TOKEN 的 contents: write 权限，自动提交不会再次触发 push workflow。发布任务串行执行；若 main 在构建期间变化，则停止该次发布，等待后续运行或手动重跑。普通 git push 也会拒绝并发更新，不强推或覆盖。分支保护规则必须允许机器人直接提交 reports/；如果组织策略禁止，回写会失败并停止部署，需要管理员调整策略。测试、数据校验或回写失败时不会部署，线上继续保留上次成功版本。

校验包含 schema、真实日期、四个模块日期/窗口一致、目录日期一致、7 天 UTC 半开窗口、新闻日期在窗口内、模块内 ID/URL 唯一和 HTTP(S) URL。所有 JSON 字符串在 HTML 中转义。任何数据校验失败都会输出文件与字段信息并非零退出，且不会改写已有 site/。结构校验不会核实新闻真实性或识别不同 URL 对应的同一事件，研究者仍负责语义去重。Markets 额外检查国际金价与美国股市各有 2–4 条观点、中国股市有 1–3 条观点、机构文章 published_at 位于 `[window.start, window.end)`，以及每个市场的观点 URL 唯一；同一分析跨市场复用是允许的。机构权威性、是否为最新分析和观点归属仍由研究者核实。

## Production workflow

Scheduled Task → reads PIPELINE.md → generates JSON → commits JSON → GitHub Actions tests / validates / renders → commits reports → GitHub Pages。

最少接入步骤：

1. 将仓库推送到 GitHub 的 main。在 Settings → Pages → Build and deployment 中选择 **GitHub Actions**，运行一次 Pages workflow 并确认部署。
2. 为 GPT 执行环境提供仓库读取、本期 JSON 写入/commit/push、联网阅读和 Actions 状态读取能力。确保仓库允许 Actions 使用 contents: write 将生成报告提交到 main。
3. 创建每周任务（建议周一 UTC 早间），提供仓库地址和以下 prompt。先手动完整运行一次确认可提交和部署，再启用每周运行。

建议 Scheduled Task prompt：

> 读取 alwinecor/newsroom 仓库 PIPELINE.md 并严格执行完整 weekly newsroom pipeline。根据其中定义依次处理所有 enabled modules，将结构化结果写入本期 data/issues/YYYY-MM-DD/，不得修改历史期数。使用约定 UTC 周一作为 issue_date，并遵循半开观察窗口。完成后将本期四个 JSON 一次性提交 GitHub。等待对应 GitHub Actions 自动测试、校验、生成并提交 reports 及部署 Pages，检查最终状态。成功或失败均向我报告最终结果。若本期已存在，不覆盖；若缺少联网、仓库写入或部署检查权限，明确报告阻断步骤，不声称成功。

没有 cron；定时由外部任务负责。工作流支持 push main 和 workflow_dispatch。Pages 配置参考 [GitHub 官方自定义工作流文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

关于支持插件的计划任务和项目执行模式，参见 [OpenAI 官方计划任务文档](https://learn.chatgpt.com/docs/automations)；仍需在实际账号中验证所需权限与工具。

新建远程仓库示例（先完成 `gh auth login`；按需要选择公开或私有）：

```sh
gh repo create newsroom --private --source=. --remote=origin --push
```

私有仓库使用 Pages 需相应 GitHub 套餐；如需公开仓库请明确选择 `--public`。仓库是否私有与 Pages 网站访问权限是不同设置，发布前检查 Pages 配置。
