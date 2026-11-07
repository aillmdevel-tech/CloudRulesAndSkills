"""Moderator: runs the platform rules against the built game and rewrites docs/moderation/REPORT.md live.
Usage: npm run moderate -- --platform playgama|crazygames|all [--no-build] [--dev]
Rules: tools/moderator/rules/<platform>.json (add yandex.json the same way: id, title, type auto|manual, check, needs, fix).
Exit code 0 = can be sent, 1 = not (✗ or unchecked rules)."""
import os, sys, json, time, argparse, datetime, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
from lib.harness import ROOT, build, Server
import probes, checks

ap = argparse.ArgumentParser()
ap.add_argument('--platform', default='all'); ap.add_argument('--no-build', action='store_true'); ap.add_argument('--dev', action='store_true')
a = ap.parse_args()
REPORT = os.path.join(ROOT, 'docs', 'moderation', 'REPORT.md')
ORDER = ['static', 'boot', 'ads', 'pause', 'persist', 'sizes']
ICON = {'pass': '✓', 'fail': '✗', 'manual': '👀 вручную', 'pending': '⏳ ещё не проверено'}

names = sorted(f[:-5] for f in os.listdir(os.path.join(HERE, 'rules')) if f.endswith('.json'))
if a.platform != 'all':
    if a.platform not in names: sys.exit(f'нет rules/{a.platform}.json (есть: {names})')
    names = [a.platform]
RULES = {n: json.load(open(os.path.join(HERE, 'rules', f'{n}.json'), encoding='utf-8')) for n in names}
RES = {n: {r['id']: ('pending', '') for r in RULES[n]['rules']} for n in names}
P = {}
status_line = 'запуск…'


def write_report(final=False):
    L = ['# Отчёт модератора', '',
         f"Обновлён: {datetime.datetime.now():%Y-%m-%d %H:%M:%S} · {'**ПРОГОН ЗАВЕРШЁН**' if final else '⏳ идёт прогон: ' + status_line} · собрано из `dist/` (prod), Chromium + эмуляция Bridge (mock + скриптовая реклама)", '']
    verdicts = []
    for n in names:
        rs, res = RULES[n]['rules'], RES[n]
        cnt = {k: sum(1 for r in rs if res[r['id']][0] == k) for k in ICON}
        fails = [r for r in rs if res[r['id']][0] == 'fail']
        v = 'нельзя отправлять' if fails or cnt['pending'] else ('можно отправлять — после ручных проверок' if cnt['manual'] else 'можно отправлять')
        verdicts.append((n, v))
        L += [f"## {RULES[n]['title']}", f"Источник: {RULES[n]['source']}", ''] + ([f"> {RULES[n]['note']}", ''] if RULES[n].get('note') else [])
        L += [f"✓ {cnt['pass']} · ✗ {cnt['fail']} · 👀 {cnt['manual']} · ⏳ {cnt['pending']} (всего {len(rs)})", '',
              '| № | Правило | Тип | Статус | Детали |', '|---|---|---|---|---|']
        for r in rs:
            st, det = res[r['id']]
            L.append(f"| {r['id']} | {r['title']} | {r['type']} | {ICON[st]} | {(det or r.get('note', '')).replace('|', '/').replace(chr(10), ' ')} |")
        L.append('')
        if fails:
            L += [f"### Замечания — {RULES[n]['title']}", '']
            for r in fails: L.append(f"- **{r['id']}** — {r['title']}: {res[r['id']][1]}. Исправить: `{r.get('fix') or '—'}`")
            L.append('')
        man = [r for r in rs if res[r['id']][0] == 'manual' and r['type'] == 'auto']
        if man:
            L += [f"### Автопроверка не смогла решить — посмотреть вручную ({RULES[n]['title']})", '']
            L += [f"- **{r['id']}** — {r['title']}: {res[r['id']][1]}" for r in man] + ['']
    if final:
        L += ['## Вердикт', ''] + [f"- **{RULES[n]['title']}: {v}**" for n, v in verdicts] + ['']
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, 'w', encoding='utf-8').write('\n'.join(L))
    return verdicts


def evaluate(done):
    for n in names:
        for r in RULES[n]['rules']:
            if RES[n][r['id']][0] != 'pending' or not set(r.get('needs', [])) <= set(done): continue
            if not r.get('check'):
                RES[n][r['id']] = ('manual', r.get('note', '')); continue
            try: RES[n][r['id']] = checks.CHECKS[r['check']](P, r)
            except Exception as e:
                RES[n][r['id']] = ('manual', f'проверка упала: {type(e).__name__}: {e}')
                traceback.print_exc()


def run_probes(url):
    global status_line
    needed = {p for n in names for r in RULES[n]['rules'] for p in r.get('needs', [])}
    for p in ORDER:
        if p not in needed: continue
        status_line = f'проба «{p}»'; write_report()
        print(f'… проба {p}', flush=True)
        try: P[p] = probes.static() if p == 'static' else getattr(probes, p)(url)
        except Exception as e:
            traceback.print_exc(); P[p] = None; print(f'✗ проба {p} упала: {e}')
        if P[p] is not None: evaluate(list(P.keys()) if all(P.get(k) is not None for k in P) else [k for k in P if P[k] is not None])
        write_report()


evaluate([])
write_report()
if not a.no_build and not a.dev:
    status_line = 'сборка (npm run build)'; write_report(); build()
with Server(dev=a.dev) as srv:
    run_probes(srv.url)
# rules whose probes failed stay pending → counted as not checked
verdicts = write_report(final=True)
print(open(REPORT, encoding='utf-8').read().split('## Вердикт')[-1])
print('отчёт:', os.path.relpath(REPORT, ROOT))
sys.exit(0 if all(v.startswith('можно') for _, v in verdicts) else 1)
