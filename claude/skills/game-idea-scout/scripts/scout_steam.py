"""Steam upcoming games by wishlist popularity: daily snapshots and risers.
  python3 scout_steam.py snapshot OUTDIR [--pages 4]     # top ~200 of store 'popular upcoming' -> OUTDIR/YYYY-MM-DD.json
  python3 scout_steam.py risers OUTDIR [--days 30] [--top 15] [--max-rank 200]   # biggest rank gains vs oldest snapshot in window
Rank in Steam's 'popularwishlist' order is a proxy for wishlist momentum (exact wishlist counts are not public).
The first run has nothing to compare with: run daily (or weekly) so risers appear."""
import datetime as dt, glob, html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0', 'Cookie': 'birthtime=0; wants_mature_content=1'}
URL = 'https://store.steampowered.com/search/results/?filter=popularwishlist&infinite=1&count=50&start={}&cc=us&l=english'


def get(u):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read())


def snapshot(out, pages=4):
    os.makedirs(out, exist_ok=True); items, rank = [], 0
    for p in range(pages):
        h = get(URL.format(p * 50))['results_html']
        for m in re.finditer(r'href="https://store\.steampowered\.com/app/(\d+)/[^"]*".*?data-ds-tagids="\[([^\]]*)\]".*?'
                             r'<span class="title">(.*?)</span>.*?search_released[^>]*>\s*(.*?)\s*</div>', h, re.S):
            rank += 1
            items.append(dict(rank=rank, appid=int(m.group(1)), name=html.unescape(m.group(3)),
                              tags=[int(t) for t in m.group(2).split(',') if t], release=html.unescape(m.group(4)).strip()))
        time.sleep(1)
    day = dt.date.today().isoformat()
    json.dump(dict(date=day, source='steam popularwishlist', items=items), open(os.path.join(out, f'{day}.json'), 'w'), ensure_ascii=False, indent=0)
    print(f'{day}: {len(items)} games → {out}/{day}.json')


def risers(out, days=30, top=15, max_rank=200):
    snaps = sorted(glob.glob(os.path.join(out, '*.json')))
    if len(snaps) < 2: print('need ≥2 snapshots (run snapshot daily)'); return
    new = json.load(open(snaps[-1])); cut = (dt.date.fromisoformat(new['date']) - dt.timedelta(days=days)).isoformat()
    old = json.load(open(next((s for s in snaps if os.path.basename(s)[:10] >= cut), snaps[0])))
    was = {x['appid']: x['rank'] for x in old['items']}
    rows = []
    for x in new['items']:
        if x['rank'] > max_rank: continue
        before = was.get(x['appid'])
        gain = (before - x['rank']) if before else (max_rank + 1 - x['rank'])  # new entry = jumped in from outside the list
        rows.append((gain, x, before))
    rows.sort(key=lambda r: -r[0])
    print(f"risers {old['date']} → {new['date']}")
    for gain, x, before in rows[:top]:
        print(f"+{gain:3d}  #{x['rank']:3d} (was {before or 'new'})  {x['appid']}  {x['name']}  [{x['release']}]  https://store.steampowered.com/app/{x['appid']}/")


a = sys.argv[1:]
opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
if a[:1] == ['snapshot']: snapshot(a[1], opt('--pages', 4))
elif a[:1] == ['risers']: risers(a[1], opt('--days', 30), opt('--top', 15), opt('--max-rank', 200))
else: print(__doc__)
