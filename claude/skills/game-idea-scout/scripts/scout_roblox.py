"""Roblox charts: daily snapshots of Top Trending / Up-and-Coming / Top Playing Now + game ages.
  python3 scout_roblox.py snapshot OUTDIR      # -> OUTDIR/YYYY-MM-DD.json (public explore + games API, no login)
  python3 scout_roblox.py report OUTDIR [--max-age 90] [--top 25]
Report: young games (created ≤ max-age days) ranked by players now, with change vs the previous snapshot,
plus genres that dominate trending. Numbers are concurrent players at snapshot time (they swing by hour/weekday)."""
import re, datetime as dt, glob, json, os, sys, time, urllib.request

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


def pick_prev(snaps, days):
    new_date = dt.date.fromisoformat(os.path.basename(snaps[-1])[:10]); best = None
    for s in snaps[:-1]:  # newest snapshot at least `days` old, else the oldest one
        if (new_date - dt.date.fromisoformat(os.path.basename(s)[:10])).days >= days: best = s
    return best or (snaps[0] if len(snaps) > 1 else None)


def report(out, max_age=90, top=25, days=1):
    snaps = sorted(glob.glob(os.path.join(out, '20*.json')))
    if not snaps: print('no snapshots'); return
    new = json.load(open(snaps[-1])); pp = pick_prev(snaps, days); prev = json.load(open(pp)) if pp else None
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


STOP = set('the a an of for to and in on my your you with game simulator sim tycoon obby new update upd beta alpha revamp event x 2 3 v2 1 best real realistic super mega ultra'.split())


def words(name):
    t = re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', name.lower())
    return {w for w in re.findall(r"[a-z][a-z']+", t) if w not in STOP and len(w) > 2}


def clusters(out, max_age=120, min_games=3):
    """Saturation: words shared by ≥ min_games young chart games (throw/fish/ragdoll/steal…)."""
    new = json.load(open(sorted(glob.glob(os.path.join(out, '20*.json')))[-1])); today = dt.date.fromisoformat(new['date'])
    idx = {}
    for u, g in new['games'].items():
        if (today - dt.date.fromisoformat(g.get('created', new['date']))).days > max_age: continue
        for w in words(g['name']): idx.setdefault(w, []).append(g)
    rows = sorted(((w, gs) for w, gs in idx.items() if len(gs) >= min_games), key=lambda r: -sum(g['playing'] for g in r[1]))
    print(f'saturation clusters on {new["date"]} (young ≤{max_age} d, ≥{min_games} games share a word)')
    for w, gs in rows[:15]:
        gs.sort(key=lambda g: -g['playing'])
        print(f"{w:12s} {len(gs):2d} games  {sum(g['playing'] for g in gs):8d} playing  " + '; '.join(f"{g['name'][:28]} {g['playing']}" for g in gs[:5]))


a = sys.argv[1:]
opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
if a[:1] == ['snapshot']: snapshot(a[1])
elif a[:1] == ['report']: report(a[1], opt('--max-age', 90), opt('--top', 25), opt('--days', 1))
elif a[:1] == ['clusters']: clusters(a[1], opt('--max-age', 120), opt('--min', 3))
else: print(__doc__)
