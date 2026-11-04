"""Sync reviewed reading-update links; never regenerate historical company prose.

Run with --check to detect stale links/catalogue, or --write after reviewing the
dated Markdown and its index. No web requests, original-data import or deployment.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
READING = ROOT / 'docs/companies'
START = '<!-- reading-updates:start -->'
END = '<!-- reading-updates:end -->'


def block(text, body):
    if (START in text) != (END in text):
        raise ValueError('Incomplete update markers')
    value = START + '\n' + body.strip() + '\n' + END
    if START in text:
        assert text.count(START) == text.count(END) == 1
        return re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: value, text, flags=re.S)
    heading, rest = text.split('\n', 1)
    return heading + '\n\n' + value + '\n' + rest


def plan():
    index = json.loads((READING / 'updates/index.json').read_text(encoding='utf-8'))
    assert index['schemaVersion'] == 1
    catalogue = json.loads((READING / 'catalog.json').read_text(encoding='utf-8'))
    by_code = {row['code']: row for row in catalogue}
    assert len(by_code) == len(catalogue)
    grouped, seen = {}, set()
    for entry in index['entries']:
        code, period = entry['code'], entry['reportPeriod']
        assert re.fullmatch(r'\d{6}\.(SZ|SH|BJ)', code)
        assert re.fullmatch(r'20\d{2}(Q[1-3]|FY|H1)', period)
        assert code in by_code and code != '601138.SH', 'Unknown company or protected benchmark'
        assert by_code[code]['name'] == entry['name']
        assert (code, period) not in seen, 'Duplicate company/period'
        seen.add((code, period))
        relative = Path(entry['path'])
        assert not relative.is_absolute() and relative.as_posix() == f'updates/{period}/{code}.md'
        target = READING / relative
        assert target.is_file() and target.resolve().is_relative_to(READING.resolve())
        assert date.fromisoformat(entry['publishedAt']) <= date.fromisoformat(entry['reviewedAt'])
        assert isinstance(entry['audited'], bool)
        assert re.fullmatch(r'[0-9a-f]{64}', entry['source']['sha256'])
        assert entry['source']['url'].startswith('https://')
        assert entry['source']['pdfPages'] and all(isinstance(p, int) and p > 0 for p in entry['source']['pdfPages'])
        assert entry['source']['url'] in target.read_text(encoding='utf-8')
        grouped.setdefault(code, []).append(entry)
    output, recent = {}, []
    for code, entries in sorted(grouped.items()):
        entries.sort(key=lambda e: (e['publishedAt'], e['reportPeriod']), reverse=True)
        lines = ['## 经营更新', '', '原生意笔记保留原报告期间；以下补充新披露的经营变化。', '']
        for e in entries:
            lines.append(f"- [{e['reportPeriod']}：{e['title']}]({e['path']})（披露 {e['publishedAt']}，核对 {e['reviewedAt']}）")
            recent.append(e)
        path = READING / (code + '.md')
        output[path] = block(path.read_text(encoding='utf-8'), '\n'.join(lines))
        e = entries[0]
        by_code[code]['latestUpdate'] = {k: e[k] for k in ('reportPeriod', 'path', 'publishedAt', 'reviewedAt')}
    for row in catalogue:
        if row['code'] not in grouped and 'latestUpdate' in row:
            raise ValueError('Index removal requires explicit historical review: ' + row['code'])
    recent.sort(key=lambda e: (e['publishedAt'], e['code']), reverse=True)
    lines = ['## 最近核对的经营变化', '', '披露日期与资料核对日期分别标注；其余公司仍沿用原资料日期。', '']
    for e in recent[:20]:
        lines.append(f"- [{e['name']} · {e['reportPeriod']}：{e['title']}]({e['path']})（披露 {e['publishedAt']}，核对 {e['reviewedAt']}）")
    output[READING / 'README.md'] = block((READING / 'README.md').read_text(encoding='utf-8'), '\n'.join(lines))
    output[READING / 'catalog.json'] = json.dumps(catalogue, ensure_ascii=False, indent=2) + '\n'
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--write', action='store_true')
    args = parser.parse_args()
    output = plan()
    changed = [p for p, text in output.items() if p.read_text(encoding='utf-8') != text]
    if args.write:
        for path in changed:
            path.write_text(output[path], encoding='utf-8', newline='\n')
    print(json.dumps({'mode': 'write' if args.write else 'check', 'changed': [p.relative_to(ROOT).as_posix() for p in changed]}, ensure_ascii=True))
    if args.check and changed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
