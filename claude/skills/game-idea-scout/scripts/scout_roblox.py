"""Roblox charts: daily snapshots of Top Trending / Up-and-Coming / Top Playing Now + game ages.
  python3 scout_roblox.py snapshot OUTDIR      # -> OUTDIR/YYYY-MM-DD.json (public explore + games API, no login)
  python3 scout_roblox.py report OUTDIR [--max-age 90] [--top 25]
Report: young games (created ≤ max-age days) ranked by players now, with change vs the previous snapshot,
plus genres that dominate trending. Numbers are concurrent players at snapshot time (they swing by hour/weekday)."""
import datetime as dt, glob, json, os, sys, time, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
SORTS = ('top-trending', 'up-and-coming', 'top-playing-now', 'fun-with-friends')


def get(u):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read())


def snapshot(out):
    os.makedirs(out, exist_ok=True)
    d = get('https://apis.roblox.com/explore-api/v1/get-sorts?sessionId=gf-scout&device=computer&country=all')
    games, lists = {}, {}
    for s in d['sorts']:
        if s.get('sortId') not in SORTS: continue
        lists[s['sortId']] = []
        for i, g in enumerate(s.get('games') or []):
            if g.get('isSponsored'): continue
            u = g['universeId']; lists[s['sortId']].append(u)
            games.setdefault(u, dict(name=g['name'], place=g['rootPlaceId'], playing=g.get('playerCount', 0),
                                     up=g.get('totalUpVotes', 0), down=g.get('totalDownVotes', 0), genre=g.get('genreL1', '')))
    ids = list(games)
    for k in range(0, len(ids), 50):
        for x in get('https://games.roblox.com/v1/games?universeIds=' + ','.join(map(str, ids[k:k + 50])))['data']:
            games[x['id']].update(created=x['created'][:10], updated=x['updated'][:10], visits=x['visits'], genre=x.get('genre_l1') or games[x['id']]['genre'])
        time.sleep(0.5)
    day = dt.date.today().isoformat()
    json.dump(dict(date=day, lists=lists, games={str(k): v for k, v in games.items()}), open(os.path.join(out, f'{day}.json'), 'w'), ensure_ascii=False, indent=0)
    print(f'{day}: {len(games)} games in {", ".join(f"{k} {len(v)}" for k, v in lists.items())}')


def report(out, max_age=90, top=25):
    snaps = sorted(glob.glob(os.path.join(out, '20*.json')))
    if not snaps: print('no snapshots'); return
    new = json.load(open(snaps[-1])); prev = json.load(open(snaps[-2])) if len(snaps) > 1 else None
    today = dt.date.fromisoformat(new['date']); where = {}
    for s, ids in new['lists'].items():
        for i, u in enumerate(ids): where.setdefault(str(u), []).append(f'{s}#{i + 1}')
    rows = []
    for u, g in new['games'].items():
        age = (today - dt.date.fromisoformat(g.get('created', new['date']))).days
        if age > max_age: continue
        was = prev['games'].get(u, {}).get('playing') if prev else None
        like = round(100 * g['up'] / max(1, g['up'] + g['down']))
        rows.append((g['playing'], age, like, was, u, g))
    rows.sort(key=lambda r: -r[0])
    print(f"young Roblox games (≤{max_age} d) on {new['date']}" + (f" vs {prev['date']}" if prev else ' (no previous snapshot)'))
    for playing, age, like, was, u, g in rows[:top]:
        delta = f' ({playing - was:+d})' if was is not None else ''
        print(f"{playing:7d}{delta:10s} age {age:3d}d  like {like:3d}%  {g['genre']:14s} {g['name'][:42]:42s} {','.join(where.get(u, []))}  https://www.roblox.com/games/{g['place']}")
    gen = {}
    for u in new['lists'].get('top-trending', []) + new['lists'].get('up-and-coming', []):
        gn = new['games'][str(u)]['genre'] or '—'; gen[gn] = gen.get(gn, 0) + 1
    print('genres in trending+up-and-coming:', ', '.join(f'{k} {v}' for k, v in sorted(gen.items(), key=lambda x: -x[1])[:10]))


a = sys.argv[1:]
opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
if a[:1] == ['snapshot']: snapshot(a[1])
elif a[:1] == ['report']: report(a[1], opt('--max-age', 90), opt('--top', 25))
else: print(__doc__)
