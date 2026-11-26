"""YouTube trend probe for game trailers and viral gameplay (yt-dlp, no API key, no login).
  python3 scout_youtube.py OUTDIR [--per 15] [--queries "q1|q2"] [--detail 12]
Each query searches videos uploaded THIS MONTH sorted by view count; top --detail results get upload date and
views/day. Output OUTDIR/YYYY-MM-DD.json + table. Shorts appear as normal results. TikTok/Instagram are not
scriptable without login: the agent covers them with web search (see SKILL.md)."""
import datetime as dt, json, os, subprocess, sys, urllib.parse

YTDLP = os.path.expanduser('~/.local/bin/yt-dlp')
QUERIES = ['new steam game trailer', 'steam demo funny coop', 'indie game trailer wishlist', 'roblox new game',
           'roblox game trend', 'funny physics game', 'friendslop game', 'viral indie game', 'new mobile game trend',
           'crazygames new game']
SP = 'CAMSBAgEEAE%3D'   # sort: view count · upload date: this month · type: video


def run(args):
    r = subprocess.run([YTDLP, *args], capture_output=True, text=True, timeout=300)
    return [json.loads(l) for l in r.stdout.splitlines() if l.startswith('{')]


a = sys.argv[1:]
opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
if not a: print(__doc__); raise SystemExit
out = a[0]; os.makedirs(out, exist_ok=True)
per, detail = opt('--per', 15), opt('--detail', 12)
qs = opt('--queries', '|'.join(QUERIES)).split('|')
seen, rows = set(), []
for q in qs:
    url = f'https://www.youtube.com/results?search_query={urllib.parse.quote(q)}&sp={SP}'
    for d in run(['--flat-playlist', '-j', '--playlist-end', str(per), url]):
        if d.get('id') in seen: continue
        seen.add(d.get('id'))
        rows.append(dict(q=q, id=d.get('id'), title=d.get('title', ''), channel=d.get('channel') or d.get('uploader'),
                         views=d.get('view_count') or 0, url=d.get('url') or f"https://www.youtube.com/watch?v={d.get('id')}"))
rows.sort(key=lambda r: -r['views'])
today = dt.date.today()
for r in rows[:detail]:
    j = run(['-j', '--skip-download', '--no-warnings', r['url']])
    if j and j[0].get('upload_date'):
        up = dt.datetime.strptime(j[0]['upload_date'], '%Y%m%d').date(); days = max(1, (today - up).days)
        r.update(uploaded=up.isoformat(), views_per_day=round(r['views'] / days), duration=j[0].get('duration'))
json.dump(dict(date=today.isoformat(), queries=qs, videos=rows), open(os.path.join(out, f'{today}.json'), 'w'), ensure_ascii=False, indent=0)
for r in rows[:40]:
    print(f"{r['views']:>10,} {('%s/d' % format(r['views_per_day'], ',')) if 'views_per_day' in r else '':>11} {r.get('uploaded', ''):10s} "
          f"{(r['channel'] or '')[:18]:18s} {r['title'][:60]:60s} [{r['q']}] {r['url']}")
print(f'{len(rows)} videos from {len(qs)} queries → {out}/{today}.json')
