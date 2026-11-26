"""Rebuild DesignLibrary/INDEX.md from the front matter of games/*.md. Usage: python3 tools/index.py"""
import os, re, glob
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []
for p in sorted(glob.glob(os.path.join(LIB, 'games', '*.md'))):
    if os.path.basename(p).startswith('_'): continue
    t = open(p, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---', t, re.S)
    fm = {k.strip(): v.split('#')[0].strip() for k, v in (l.split(':', 1) for l in (m.group(1).splitlines() if m else []) if ':' in l)}
    line = lambda h: (re.search(rf'\*\*{h}[^*]*\*\*\s*(.+)', t) or [None, ''])[1].strip()
    rows.append([f"[[games/{os.path.basename(p)[:-3]}\\|{fm.get('name', '?')}]]", fm.get('platform', ''), fm.get('genre', ''),
                 fm.get('online', ''), fm.get('status', ''), line('Фантазия'), line('Почему жива'), fm.get('verdict', '')])
hdr = ['Игра', 'Площадка', 'Жанр', 'Онлайн', 'Статус', 'Фантазия', 'Почему жива / смерть', 'Вердикт']
out = ['# Индекс игр', '', f'Всего: {len(rows)}. Генерируется `python3 tools/index.py`, руками не править.', '',
       '| ' + ' | '.join(hdr) + ' |', '|' + '---|' * len(hdr)] + ['| ' + ' | '.join(c.replace('|', '/') if not c.startswith('[[') else c for c in r) + ' |' for r in rows]
genres = {}
for r in rows: genres[r[2]] = genres.get(r[2], 0) + 1
out += ['', '## По жанрам'] + [f'- {g or "—"}: {n}' for g, n in sorted(genres.items())]
open(os.path.join(LIB, 'INDEX.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('INDEX.md:', len(rows), 'games')
