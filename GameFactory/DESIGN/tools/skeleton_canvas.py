"""Turn docs/GAME_SKELETON.md into an Obsidian Canvas board (17 columns in 5 coloured groups).
Usage: python3 skeleton_canvas.py docs/GAME_SKELETON.md [out.canvas]
Column = a '### NN Title' heading; its text up to the next heading = the card body. Empty card = hole in the game."""
import json, os, re, sys

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + '.canvas'
text = open(src, encoding='utf-8').read()
GROUPS = [('1 · Вход', range(1, 4), '4'), ('2 · Ядро', range(4, 9), '6'), ('3 · Цели', range(9, 13), '3'),
          ('4 · Удержание', range(13, 17), '2'), ('5 · Проверка', range(17, 18), '1')]
cols = {}
for m in re.finditer(r'^###\s+(\d{2})\s+(.+?)\s*$(.*?)(?=^##|\Z)', text, re.S | re.M):
    cols[int(m.group(1))] = (m.group(2), m.group(3).strip())
W, H, GAP = 320, 520, 30
nodes, x, holes = [], 0, []
for gname, rng, color in GROUPS:
    gx = x
    for n in rng:
        title, body = cols.get(n, (f'колонка {n}', ''))
        filled = re.sub(r'[-*\s>_]|\[пробел\]', '', body)
        if not filled: holes.append(f'{n:02d} {title}')
        nodes.append({'id': f'c{n}', 'type': 'text', 'x': x, 'y': 80, 'width': W, 'height': H,
                      'color': color if filled else '1',
                      'text': f'## {n:02d} {title}\n\n' + (body or '**[пробел] — дыра в игре**')})
        x += W + GAP
    nodes.append({'id': f'g{gname[0]}', 'type': 'group', 'label': gname, 'x': gx - 15, 'y': 30,
                  'width': x - gx - GAP + 30, 'height': H + 70, 'color': color})
    x += GAP * 2
json.dump({'nodes': nodes, 'edges': []}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(out, '| holes:', ', '.join(holes) or 'none')
