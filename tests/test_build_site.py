import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ('scripts', 'modules', 'data', 'assets'):
            if (ROOT / folder).exists():
                shutil.copytree(ROOT / folder, self.root / folder)

    def run_build(self, *args):
        return subprocess.run([sys.executable, '-X', 'utf8', str(self.root / 'scripts/build_site.py'), *args],
                              capture_output=True, text=True, encoding='utf-8')

    def mutate(self, change):
        path = self.root / 'data/issues/2026-09-07/technology.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        change(data)
        path.write_text(json.dumps(data), encoding='utf-8')

    def test_build_and_escape(self):
        self.mutate(lambda d: d['items'][0].update(original_title='<script>alert("x")</script>'))
        result = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = (self.root / 'site/reports/2026-09-07.html').read_text(encoding='utf-8')
        self.assertIn('&lt;script&gt;', report)
        self.assertNotIn('<script>', report)
        self.assertEqual(report.count('<article'), 15)
        self.assertLess(report.index('id="technology"'), report.index('id="politics"'))
        self.assertEqual(report, (self.root / 'site/index.html').read_text(encoding='utf-8'))
        self.assertIn('archive-drawer', report)

    def test_invalid_data_does_not_replace_site(self):
        changes = [
            lambda d: d['items'].pop(),
            lambda d: d['items'][1].update(id=d['items'][0]['id']),
            lambda d: d['items'][1].update(url=d['items'][0]['url']),
            lambda d: d.update(issue_date='2026-09-08'),
            lambda d: d['window'].update(start='2026-08-30'),
            lambda d: d['items'][0].update(url='javascript:alert(1)'),
            lambda d: d['items'][0].update(published_at='2026-02-30'),
            lambda d: d['items'][0].update(published_at='2026-09-07'),
            lambda d: d.update(module='politics'),
            lambda d: d.update(extra=True),
        ]
        path = self.root / 'data/issues/2026-09-07/technology.json'
        original = path.read_text(encoding='utf-8')
        for change in changes:
            with self.subTest(change=changes.index(change)):
                path.write_text(original, encoding='utf-8')
                self.mutate(change)
                result = self.run_build()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('ERROR:', result.stderr)
                self.assertFalse((self.root / 'site').exists())

    def test_missing_module(self):
        (self.root / 'data/issues/2026-09-07/finance.json').unlink()
        result = self.run_build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('finance.json', result.stderr)
        self.assertIn('ERROR:', result.stderr)

    def test_failure_preserves_existing_output(self):
        self.assertEqual(self.run_build().returncode, 0)
        index = self.root / 'site/index.html'
        before = index.read_bytes()
        self.mutate(lambda d: d['items'].clear())
        self.assertNotEqual(self.run_build().returncode, 0)
        self.assertEqual(index.read_bytes(), before)

    def test_existing_reports_are_reused_and_archive_updates(self):
        self.assertEqual(self.run_build().returncode, 0)
        existing = self.root / 'reports/2026-09-07.html'
        before = existing.read_bytes()
        modified = existing.stat().st_mtime_ns
        older = self.root / 'data/issues/2026-08-31'
        older.mkdir()
        for path in (self.root / 'data/issues/2026-09-07').glob('*.json'):
            data = json.loads(path.read_text(encoding='utf-8'))
            data.update(issue_date='2026-08-31', window={'start': '2026-08-24', 'end': '2026-08-31'})
            for item in data['items']:
                item['published_at'] = '2026-08-25'
            (older / path.name).write_text(json.dumps(data), encoding='utf-8')
        self.assertEqual(self.run_build().returncode, 0)
        archive = json.loads((self.root / 'site/archive.json').read_text(encoding='utf-8'))
        self.assertEqual(archive, ['2026-09-07', '2026-08-31'])
        self.assertEqual(existing.read_bytes(), before)
        self.assertEqual(existing.stat().st_mtime_ns, modified)
        shutil.rmtree(older)
        self.assertEqual(self.run_build().returncode, 0)
        self.assertTrue((self.root / 'site/reports/2026-08-31.html').exists())
        # A clean CI output and a changed template must not re-render history.
        shutil.rmtree(self.root / 'site')
        (self.root / 'assets/report.html').write_text('CHANGED TEMPLATE', encoding='utf-8')
        self.assertEqual(self.run_build().returncode, 0)
        self.assertEqual((self.root / 'site/reports/2026-09-07.html').read_bytes(), before)

    def test_new_issue_becomes_home_without_changing_old_report(self):
        self.assertNotEqual(self.run_build('--check-published').returncode, 0)
        self.assertEqual(self.run_build().returncode, 0)
        existing = self.root / 'reports/2026-09-07.html'
        original = existing.read_bytes()
        newer = self.root / 'data/issues/2026-09-14'
        newer.mkdir()
        for path in (self.root / 'data/issues/2026-09-07').glob('*.json'):
            data = json.loads(path.read_text(encoding='utf-8'))
            data.update(issue_date='2026-09-14', window={'start': '2026-09-07', 'end': '2026-09-14'})
            for item in data['items']:
                item['published_at'] = '2026-09-08'
            (newer / path.name).write_text(json.dumps(data), encoding='utf-8')
        result = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Rendered 1 new report(s); preserved 1 report(s)', result.stdout)
        self.assertEqual(existing.read_bytes(), original)
        self.assertEqual((self.root / 'site/index.html').read_bytes(),
                         (self.root / 'reports/2026-09-14.html').read_bytes())
        self.assertEqual(json.loads((self.root / 'site/archive.json').read_text()),
                         ['2026-09-14', '2026-09-07'])
        self.assertEqual(self.run_build('--check-published').returncode, 0)

    def test_existing_report_can_be_edited_or_regenerated(self):
        self.assertEqual(self.run_build().returncode, 0)
        report = self.root / 'reports/2026-09-07.html'
        original = report.read_bytes()
        edited = original + b'\n<!-- editorial update -->'
        report.write_bytes(edited)
        self.assertEqual(self.run_build('--check-published').returncode, 0)
        self.assertEqual((self.root / 'site/index.html').read_bytes(), edited)
        report.unlink()
        self.assertEqual(self.run_build().returncode, 0)
        self.assertEqual(report.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
