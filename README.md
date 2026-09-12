# Modular AI Newsroom

## What it is

AI-generated modular international news digest. 一个最小可用的国际新闻周报 pipeline，提供中文摘要并保留原始标题与来源。纯静态 HTML + CSS，Python 3.12，唯一直接依赖为 jsonschema。

## Architecture

- ChatGPT：research + selection + deduplication + Chinese summaries。
- Repository：rules + schemas + validation + rendering。
- GitHub Actions：build + deploy。

本仓库不联网搜索新闻，不包含爬虫或 LLM API。三个模块独立生成 JSON，Python 校验全部历史期数，在内存中按固定顺序聚合新期数，保存不可变报告并组装静态发布目录；不额外保存聚合 JSON。

## Modules

- Technology / 科技
- Politics / 时政
- Finance / 宏观经济与金融

入口是 [PIPELINE.md](pipeline/PIPELINE.md)，各模块在 modules/ 下分别拥有 MODULE.md 和 schema.json。三个 schema 独立且结构一致，不使用继承。

## Manual test

```sh
python -m pip install jsonschema
python scripts/build_site.py
python -m unittest discover -s tests
python -m http.server 8000 --directory site
```

浏览器访问 http://localhost:8000。根 URL 直接显示最新一期。完整归档导航通过 HTTP(S) 加载 archive.json；直接打开本地 HTML 时仅保留当期导航。CI 使用 requirements.txt 中的 jsonschema 主版本范围。

正式数据位于 data/issues/YYYY-MM-DD/。每期使用 editorial / newspaper 版式，左侧抽屉按年份和日期倒序展示归档。

发布源为 Git 跟踪的 `reports/YYYY-MM-DD.html`。构建只渲染不存在的报告；已发布 HTML 按原始字节保留，包括内嵌的当期 CSS 与归档脚本，后续模板修改不会改变旧期视觉。不要删除或修改这些快照；本次 2026-09-07 重新生成属于一次明确授权的设计迁移。

`site/` 是不提交 Git 的部署产物，包含最新报告的完整副本 `index.html`、全部报告的字节副本 `reports/`、动态归档清单 `archive.json` 和 `.nojekyll`。历史页每次打开时用少量原生 JavaScript 读取最新清单，因此更新 sidebar 不需要重写任何旧报告。请求失败时保留当期链接。支持 GitHub project Pages 子路径，无额外依赖。

每次新增一期：运行构建，将本期三个 JSON 与新生成的 `reports/YYYY-MM-DD.html` 一起提交。CI 使用 `python scripts/build_site.py --check-published`，缺少报告快照会失败；全新 checkout 也直接使用 Git 中的历史快照，不依赖 Actions cache 或过期 artifact。构建仍会打包上传全部静态文件，但不会重新渲染旧 reports。

校验包含 schema、真实日期、三个模块日期/窗口一致、目录日期一致、7 天 UTC 半开窗口、新闻日期在窗口内、模块内 ID/URL 唯一和 HTTP(S) URL。所有 JSON 字符串在 HTML 中转义。任何数据校验失败都会输出文件与字段信息并非零退出，且不会改写已有 site/。结构校验不会核实新闻真实性或识别不同 URL 对应的同一事件，研究者仍负责语义去重。

## Production workflow

Scheduled Task → reads PIPELINE.md → generates JSON → local validation / aggregate / render → commits → GitHub Actions → GitHub Pages。

最少接入步骤：

1. 将仓库推送到 GitHub 的 main。在 Settings → Pages → Build and deployment 中选择 **GitHub Actions**，运行一次 Pages workflow 并确认部署。
2. 为执行任务的环境提供仓库读取、仅本期数据写入/commit/push、联网阅读、Python 3.12 和 jsonschema、Actions 状态读取能力。确认当前产品、账号和任务模式支持这些工具；本仓库不能赋予普通 ChatGPT Scheduled Task GitHub 写入或 shell 权限。若不支持，需改用具备这些能力的任务执行环境，或人工提交 JSON。
3. 创建每周任务（建议周一 UTC 早间），提供仓库地址和以下 prompt。先手动完整运行一次确认可提交和部署，再启用每周运行。

建议 Scheduled Task prompt：

> 读取本仓库 pipeline/PIPELINE.md 并严格执行完整 weekly newsroom pipeline。根据其中定义依次处理所有 enabled modules，将结构化结果写入本期 data/issues/YYYY-MM-DD/，不得修改历史期数。使用约定 UTC 周一作为 issue_date，并遵循半开观察窗口。完成后运行校验，将三个 JSON 和新生成的本期 reports/YYYY-MM-DD.html 一次性提交 GitHub，并检查对应 commit 的 GitHub Actions 和 Pages 部署状态。成功或失败均向我报告最终结果。若本期已存在，不覆盖；若缺少联网、执行、仓库写入或部署检查权限，明确报告阻断步骤，不声称成功。

没有 cron；定时由外部任务负责。工作流支持 push main 和 workflow_dispatch。Pages 配置参考 [GitHub 官方自定义工作流文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

关于支持插件的计划任务和项目执行模式，参见 [OpenAI 官方计划任务文档](https://learn.chatgpt.com/docs/automations)；仍需在实际账号中验证所需权限与工具。

新建远程仓库示例（先完成 `gh auth login`；按需要选择公开或私有）：

```sh
gh repo create newsroom --private --source=. --remote=origin --push
```

私有仓库使用 Pages 需相应 GitHub 套餐；如需公开仓库请明确选择 `--public`。仓库是否私有与 Pages 网站访问权限是不同设置，发布前检查 Pages 配置。
