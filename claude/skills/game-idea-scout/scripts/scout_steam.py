"""Steam upcoming games by wishlist popularity: daily snapshots and risers.
  python3 scout_steam.py snapshot OUTDIR [--pages 4]     # top ~200 of store 'popular upcoming' -> OUTDIR/YYYY-MM-DD.json
  python3 scout_steam.py risers OUTDIR [--days 30] [--top 15] [--max-rank 200] [--fun]   # biggest rank gains vs oldest snapshot in window
  python3 scout_steam.py fun OUTDIR [--top 40]          # latest snapshot filtered to our kind of game (tags + release date)
--fun keeps games with ≥1 FUN tag and no HEAVY tag, releasing in the next ~18 months or "coming soon"; prints tag names.
Rank in Steam's 'popularwishlist' order is a proxy for wishlist momentum (exact wishlist counts are not public).
The first run has nothing to compare with: run daily (or weekly) so risers appear.
Released games (wishlists miss them once they launch):
  python3 scout_steam.py released OUTDIR [--pages 4] [--days 90]   # topsellers + popularnew, released ≤ N days ago, + current players
  python3 scout_steam.py hot OUTDIR [--top 25] [--all]             # fun released games by current players, change vs previous snapshot"""
import datetime as dt, glob, html, json, os, re, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0', 'Cookie': 'birthtime=0; wants_mature_content=1'}
URL = 'https://store.steampowered.com/search/results/?filter=popularwishlist&infinite=1&count=50&start={}&cc=us&l=english'


FUN = {'Funny', 'Casual', 'Physics', 'Co-op', 'Online Co-Op', 'Simulation', 'Comedy', 'Cute', 'Cartoony', 'Cartoon', 'Party Game',
       'Sandbox', 'Building', 'Management', 'Cozy', 'Family Friendly', 'Colorful', 'Arcade', 'Destruction', 'Parkour', 'Racing', 'Fishing',
       'Cooking', 'Farming Sim', 'Life Sim', 'Clicker', 'Idle', 'Incremental', 'Pets', 'Party', 'Local Co-Op', 'Multiplayer', 'Dark Comedy'}
HEAVY = {'Massively Multiplayer', 'MOBA', 'Tactical', 'Military', 'Hero Shooter', 'Souls-like', 'Grand Strategy', 'Visual Novel',
         'Story Rich', 'Turn-Based Tactics', 'JRPG', 'CRPG', 'Card Battler', 'Sexual Content', 'Nudity', 'Gore', 'Mature', 'Realistic',
         'Open World Survival Craft', 'Space Sim', 'Flight', 'Hunting', 'Wargame', 'Esports',
         'Open World', 'Extraction Shooter', 'MMORPG', 'RTS', 'Action RTS', 'Looter Shooter', 'Action RPG'}


def tagnames(out):
    p = os.path.join(out, 'tags.json')
    if not os.path.exists(p):
        json.dump({str(t['tagid']): t['name'] for t in get('https://store.steampowered.com/tagdata/populartags/english')}, open(p, 'w'))
    return json.load(open(p))


def is_fun(x, names):
    tags = {names.get(str(t), '') for t in x['tags']}
    rel = x['release'].lower()
    soon = (not re.search(r'20(1\d|2[0-5])', rel)) and not re.search(r'202[89]|203', rel)
    return bool(tags & FUN) and not (tags & HEAVY) and soon, sorted(t for t in tags if t)


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


def risers(out, days=30, top=15, max_rank=200, fun=False):
    snaps = sorted(glob.glob(os.path.join(out, '20*.json')))
    if len(snaps) < 2: print('need ≥2 snapshots (run snapshot daily)'); return
    new = json.load(open(snaps[-1])); cut = (dt.date.fromisoformat(new['date']) - dt.timedelta(days=days)).isoformat()
    old = json.load(open(next((s for s in snaps if os.path.basename(s)[:10] >= cut), snaps[0])))
    was = {x['appid']: x['rank'] for x in old['items']}
    cover = max(was.values(), default=0)  # old snapshot depth: below it «new» means «unknown», not «jumped in»
    rows = []
    for x in new['items']:
        if x['rank'] > max_rank: continue
        before = was.get(x['appid'])
        if not before and x['rank'] > cover: continue
        gain = (before - x['rank']) if before else (cover + 1 - x['rank'])  # new entry = jumped in from below the old list
        rows.append((gain, x, before))
    names = tagnames(out)
    if fun: rows = [r for r in rows if is_fun(r[1], names)[0]]
    rows.sort(key=lambda r: -r[0])
    print(f"risers {old['date']} → {new['date']}")
    for gain, x, before in rows[:top]:
        print(f"+{gain:3d}  #{x['rank']:3d} (was {before or 'new'})  {x['name']}  [{x['release']}]  {', '.join(is_fun(x, names)[1][:6])}  https://store.steampowered.com/app/{x['appid']}/")


def fun(out, top=40):
    snap = json.load(open(sorted(glob.glob(os.path.join(out, '20*.json')))[-1])); names = tagnames(out); n = 0
    print(f"fun filter on {snap['date']} ({len(snap['items'])} games)")
    for x in snap['items']:
        ok, tags = is_fun(x, names)
        if ok and n < top:
            n += 1; print(f"#{x['rank']:3d}  {x['name']}  [{x['release']}]  {', '.join(tags[:7])}  https://store.steampowered.com/app/{x['appid']}/")


def released_date(rel):
    for f in ('%b %d, %Y', '%d %b, %Y', '%B %d, %Y', '%d %B, %Y'):
        try: return dt.datetime.strptime(rel.strip(), f).date()
        except ValueError: pass


def players(appid):
    try:
        return get(f'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}')['response'].get('player_count', 0)
    except Exception:
        return None


def released(out, pages=4, days=90):
    os.makedirs(out, exist_ok=True); today = dt.date.today(); seen = {}
    for flt in ('topsellers', 'popularnew'):
        for p in range(pages):
            h = get(URL.replace('popularwishlist', flt).format(p * 50))['results_html']
            for m in re.finditer(r'href="https://store\.steampowered\.com/app/(\d+)/[^"]*".*?data-ds-tagids="\[([^\]]*)\]".*?'
                                 r'<span class="title">(.*?)</span>.*?search_released[^>]*>\s*(.*?)\s*</div>', h, re.S):
                rel = html.unescape(m.group(4)).strip(); d = released_date(rel); appid = int(m.group(1))
                if not d or (today - d).days > days or d > today: continue
                x = seen.setdefault(appid, dict(appid=appid, name=html.unescape(m.group(3)), tags=[int(t) for t in m.group(2).split(',') if t],
                                                release=rel, released=d.isoformat(), lists=[]))
                if flt not in x['lists']: x['lists'].append(flt)
            time.sleep(1)
    for x in seen.values():
        x['players'] = players(x['appid']); time.sleep(0.3)
    items = sorted(seen.values(), key=lambda x: -(x['players'] or 0)); day = today.isoformat()
    json.dump(dict(date=day, source='steam topsellers+popularnew, released ≤ %d d, current players' % days, items=items),
              open(os.path.join(out, f'{day}.json'), 'w'), ensure_ascii=False, indent=0)
    print(f'{day}: {len(items)} released games → {out}/{day}.json')


def hot(out, top=25, show_all=False):
    snaps = sorted(glob.glob(os.path.join(out, '20*.json')))
    if not snaps: print('no snapshot: run released first'); return
    new = json.load(open(snaps[-1])); old = json.load(open(snaps[-2])) if len(snaps) > 1 else None
    was = {x['appid']: x.get('players') for x in old['items']} if old else {}
    names = tagnames(os.path.join(os.path.dirname(out.rstrip('/')), 'steam')); today = dt.date.fromisoformat(new['date']); n = 0
    print(f"steam released hot {new['date']}" + (f" vs {old['date']}" if old else ' (first snapshot, no change yet)'))
    for x in new['items']:
        tags = {names.get(str(t), '') for t in x['tags']}
        if not show_all and (not tags & FUN or tags & HEAVY): continue
        if n >= top: break
        n += 1; b = was.get(x['appid']); pl = x.get('players')
        ch = '' if b is None or pl is None else f" ({'+' if pl >= b else ''}{pl - b})"
        age = (today - dt.date.fromisoformat(x['released'])).days
        print(f"{pl if pl is not None else '?':>7} онлайн{ch}  {age:3d} д  {x['name']}  {', '.join(sorted(t for t in tags if t)[:6])}  https://store.steampowered.com/app/{x['appid']}/")


a = sys.argv[1:]
opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
if a[:1] == ['snapshot']: snapshot(a[1], opt('--pages', 4))
elif a[:1] == ['risers']: risers(a[1], opt('--days', 30), opt('--top', 15), opt('--max-rank', 200), '--fun' in a)
elif a[:1] == ['fun']: fun(a[1], opt('--top', 40))
elif a[:1] == ['released']: released(a[1], opt('--pages', 4), opt('--days', 90))
elif a[:1] == ['hot']: hot(a[1], opt('--top', 25), '--all' in a)
else: print(__doc__)
