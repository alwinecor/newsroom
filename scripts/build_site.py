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


def render_story(item, lead=False):
    text = {key: escape(value, quote=True) for key, value in item.items()}
    level = 'PRIMARY SOURCE' if item['source_level'] == 'primary' else 'MEDIA SOURCE'
    return f'''<article class="story{' lead-story' if lead else ''}">
      <div class="story-kicker"><span>{text['category']}</span><span class="dot">•</span><span>{level}</span></div>
      <h3>{text['original_title']}</h3>
      <div class="story-meta"><span>{text['source_name']}</span><time datetime="{text['published_at']}">{text['published_at']}</time></div>
      <p class="story-summary">{text['summary_zh']}</p>
      <a class="source-link" href="{text['url']}" target="_blank" rel="noopener noreferrer">READ ORIGINAL <span>↗</span></a>
    </article>'''


def render_report(issue_date, modules, number):
    sections = []
    for index, module in enumerate(modules, 1):
        name = module['module']
        items = module['items']
        sections.append(f'''<section class="news-section" id="{name}">
      <div class="section-rule"></div>
      <header class="section-header">
        <div class="section-number">{index:02d}</div>
        <div class="section-title-wrap"><div class="section-en">{name.upper()}</div><h2>{MODULES[name]}</h2></div>
        <div class="section-count">{len(items):02d} STORIES</div>
      </header>
      <div class="lead-grid"><div class="lead-index">A</div>{render_story(items[0], lead=True)}</div>
      <div class="secondary-grid">{''.join(render_story(item) for item in items[1:])}</div>
    </section>''')
    items = [item for module in modules for item in module['items']]
    window = modules[0]['window']
    values = {
        'style': (ROOT / 'assets/style.css').read_text(encoding='utf-8'),
        'archive_script': (ROOT / 'assets/archive.js').read_text(encoding='utf-8'),
        'date': escape(issue_date),
        'number': f'{number:03d}',
        'window': escape(f'{window["start"]} — {window["end"]}'),
        'count': str(len(items)),
        'primary': str(sum(item['source_level'] == 'primary' for item in items)),
        'sources': str(len({item['source_name'] for item in items})),
        'sections': '\n'.join(sections),
        'archive_fallback': f'''<section><h2 class="archive-year">{issue_date[:4]}</h2>
          <ul class="archive-dates"><li><a href="#page-top" aria-current="page">{issue_date[5:].replace('-', '.')}</a></li></ul></section>
          <noscript>完整归档导航需要启用 JavaScript。</noscript>''',
    }
    template = (ROOT / 'assets/report.html').read_text(encoding='utf-8')
    # A single substitution pass keeps news containing template markers literal.
    return re.sub(r'\{\{([a-z_]+)\}\}', lambda match: values[match[1]], template)


def build(check_published=False):
    issues = load_issues()  # Existing data validation is unchanged.
    reports = ROOT / 'reports'
    output = ROOT / 'site'
    for path in (reports, output):
        if path.is_symlink() or path.resolve().parent != ROOT:
            raise ValueError(f'Unsafe output directory: {path}')
    published = {}
    if reports.exists():
        for path in reports.glob('*.html'):
            if path.is_symlink() or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', path.stem):
                raise ValueError(f'Invalid published report: {path}')
            date.fromisoformat(path.stem)
            published[path.stem] = path.read_bytes()
    missing = [(day, modules) for day, modules in issues if day not in published]
    if check_published and missing:
        raise ValueError('Unpublished reports: run build locally and commit reports/ with the issue JSON: '
                         + ', '.join(day for day, _ in missing))
    dates = sorted(set(published) | {day for day, _ in missing})
    # Render only missing reports, and finish preparation before writing files.
    new = {day: render_report(day, modules, dates.index(day) + 1).encode('utf-8')
           for day, modules in missing}
    published.update(new)
    if not published:
        raise ValueError('No published reports or issue data found')
    reports.mkdir(exist_ok=True)
    for day, content in new.items():
        with (reports / f'{day}.html').open('xb') as file:
            file.write(content)
    # Only replace the disposable deployment bundle; never delete reports/.
    if output.exists():
        shutil.rmtree(output)
    (output / 'reports').mkdir(parents=True)
    for day, content in published.items():
        (output / 'reports' / f'{day}.html').write_bytes(content)
    (output / 'index.html').write_bytes(published[max(published)])
    (output / 'archive.json').write_text(json.dumps(sorted(published, reverse=True), indent=2) + '\n', encoding='utf-8')
    (output / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Rendered {len(new)} new report(s); preserved {len(published) - len(new)} report(s); '
          f'latest {max(published)} -> {output}')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-published', action='store_true',
                        help='CI: require all report snapshots to have been generated and committed')
    args = parser.parse_args()
    try:
        build(check_published=args.check_published)
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
