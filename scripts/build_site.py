"""Validate all issues, aggregate modules in memory, and render static HTML."""
from datetime import date, timedelta
from html import escape
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MODULES = {'technology': '科技', 'politics': '时政', 'finance': '财经'}


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError(f'{path}: {exc}') from exc


def load_issues():
    validators = {}
    for module in MODULES:
        schema = read_json(ROOT / 'modules' / module / 'schema.json')
        Draft202012Validator.check_schema(schema)
        validators[module] = Draft202012Validator(schema, format_checker=FormatChecker())
    issues = []
    for folder in sorted((ROOT / 'data/issues').iterdir(), reverse=True):
        if not folder.is_dir():
            continue
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', folder.name):
            raise ValueError(f'{folder}: expected YYYY-MM-DD issue directory')
        date.fromisoformat(folder.name)
        modules = []
        for module in MODULES:
            path = folder / f'{module}.json'
            data = read_json(path)
            errors = list(validators[module].iter_errors(data))
            if errors:
                details = '; '.join(f'{"/".join(map(str, e.absolute_path)) or "$"}: {e.message}' for e in errors)
                raise ValueError(f'{path}: {details}')
            if data['issue_date'] != folder.name:
                raise ValueError(f'{path}: issue_date must match directory {folder.name}')
            start, end = (date.fromisoformat(data['window'][key]) for key in ('start', 'end'))
            if end.isoformat() != folder.name or end - start != timedelta(days=7):
                raise ValueError(f'{path}: window must be [issue_date - 7 days, issue_date)')
            if modules and data['window'] != modules[0]['window']:
                raise ValueError(f'{path}: module observation windows differ')
            for key in ('url', 'id'):
                values = [item[key] for item in data['items']]
                if len(values) != len(set(values)):
                    raise ValueError(f'{path}: duplicate {key} within module')
            for index, item in enumerate(data['items']):
                url = urlsplit(item['url'])
                if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password:
                    raise ValueError(f'{path}: items/{index}/url must be an HTTP(S) URL without credentials')
                if not start <= date.fromisoformat(item['published_at']) < end:
                    raise ValueError(f'{path}: items/{index}/published_at outside observation window')
            modules.append(data)
        issues.append((folder.name, modules))
    return issues


def page(title, body, prefix=''):
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="模块化国际新闻周报：科技、时政与财经。">
<title>{escape(title)} · Newsroom</title>
<link rel="stylesheet" href="{prefix}assets/style.css"></head>
<body><header><a class="brand" href="{prefix}index.html">NEWSROOM <span>/ 国际新闻周报</span></a>
<span class="edition">WEEKLY DIGEST</span></header><main>{body}</main>
<footer>AI 辅助整理 · 请以原始来源为准 · Technology / Politics / Finance</footer></body></html>'''


def render_report(issue_date, modules):
    demo = any(urlsplit(item['url']).hostname == 'example.com' for module in modules for item in module['items'])
    body = f'<a class="back" href="../index.html">← 所有期数</a><p class="eyebrow">THE WEEK IN CONTEXT</p><h1>国际新闻周报</h1><p class="intro">{escape(issue_date)} · 科技 / 时政 / 财经</p>'
    window = modules[0]['window']
    body += f'<p class="muted">观察窗口：{escape(window["start"])} 至 {escape(window["end"])}（UTC，不含结束日）</p>'
    if demo:
        body += '<aside class="notice">DEMO / 本期全部为虚构示例新闻，仅用于展示网站与验证流程。链接为占位地址。</aside>'
    body += '<nav aria-label="模块导航">' + ''.join(f'<a href="#{name}">{title}</a>' for name, title in MODULES.items()) + '</nav>'
    for module in modules:
        name = module['module']
        body += f'<section id="{name}"><div class="section-heading"><h2>{MODULES[name]}</h2><span>{name.upper()} · {len(module["items"]):02d}</span></div><div class="cards">'
        for item in module['items']:
            text = {key: escape(value, quote=True) for key, value in item.items()}
            body += f'''<article><p class="category">{text['category']}</p>
<h3>{text['original_title']}</h3><p class="meta">{text['source_name']} · <time datetime="{text['published_at']}">{text['published_at']}</time></p>
<p class="summary">{text['summary_zh']}</p><a class="source" href="{text['url']}" rel="noopener noreferrer">查看原文 ↗</a></article>'''
        body += '</div></section>'
    return page(f'{issue_date} 国际新闻周报', body, '../')


def build():
    issues = load_issues()  # Validate every historical issue before writing anything.
    outputs = {f'reports/{day}.html': render_report(day, modules) for day, modules in issues}
    body = '<p class="eyebrow">THREE LENSES. ONE WEEK.</p><h1>把一周世界动态，<br>读成清晰的脉络。</h1><p class="intro">聚焦科技、时政与财经。中文信息摘要，保留原始标题与来源。</p>'
    if issues:
        latest = issues[0][0]
        body += f'<a class="latest" href="reports/{latest}.html"><span>最新一期 / LATEST ISSUE</span><strong>{latest}</strong><span>阅读本期 →</span></a>'
    else:
        body += '<p class="notice">暂无期数，等待第一份周报。</p>'
    body += '<section><div class="section-heading"><h2>历史期数</h2><span>ARCHIVE</span></div><ul class="archive">'
    body += ''.join(f'<li><a href="reports/{day}.html"><time>{day}</time><span>科技 · 时政 · 财经 ↗</span></a></li>' for day, _ in issues)
    outputs['index.html'] = page('国际新闻周报', body + '</ul></section>')
    css = (ROOT / 'assets/style.css').read_text(encoding='utf-8')
    output = ROOT / 'site'
    # Only remove our dedicated generated directory, never source data.
    if output.is_symlink() or output.resolve().parent != ROOT:
        raise ValueError(f'Unsafe output directory: {output}')
    if output.exists():
        shutil.rmtree(output)
    for relative, content in {**outputs, 'assets/style.css': css, '.nojekyll': ''}.items():
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding='utf-8')
    print(f'Built {len(issues)} issue(s), {len(outputs)} HTML page(s) -> {output}')


if __name__ == '__main__':
    try:
        build()
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
