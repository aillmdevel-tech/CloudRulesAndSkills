#!/usr/bin/env python3
"""Competition check for an idea on Roblox, Steam and the web portals (CrazyGames, Playgama).

usage: scout_compete.py "kw1|kw2|kw3" [--out FILE.json] [--top 8]
  keywords = the fantasy and the main verb in English, as players would search them
  ("raccoon steal|steal from house|monster hotel|clean hotel").
Per keyword and platform: how many games exist, the leaders with their numbers, how young the
successful ones are, and a verdict:
  пусто    — nobody strong: the fantasy is free (check demand elsewhere: Steam wishlists, Roblox charts)
  лидер    — 1–2 strong games: demand is proven, we enter with our twist
  забито   — ≥ 3 strong games: only a new verb/fantasy, or skip
Strong = Roblox ≥ 5 000 playing now · Steam ≥ 1 000 reviews released in the last 2 years (older hits shown as
«+старые хиты» = evergreen demand) · CrazyGames ≥ 50 000 votes. Multi-word CrazyGames queries fall back to single words.
Only games whose name matches the keyword (1 word) or ≥ 2 of its words count as strong on CrazyGames/Playgama;
other search hits are listed as «(не по теме?)».
Numbers are as seen at run time; Roblox search can return popular unrelated games — read the names.
"""
import datetime as dt, html, json, re, sys, time, urllib.parse, urllib.request, uuid

H = {'User-Agent': 'Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/130 Safari/537.36', 'Accept-Language': 'en'}
TODAY = dt.date.today()


def get(u, as_json=False):
    for i in range(3):
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=25).read().decode('utf8', 'replace')
            return json.loads(b) if as_json else b
        except Exception as e:
            err = e; time.sleep(1.5 * (i + 1))
    print(f'  ! {u[:80]}: {err}', file=sys.stderr); return None


def kw(q):
    return [w for w in re.findall(r'[a-z]+', q.lower()) if len(w) > 2]


def relevant(name, q):
    """Name shares the keyword (1-word query) or ≥ 2 of its words (longer queries)."""
    ws = kw(q); n = sum(w in name.lower().replace('-', ' ') for w in ws)
    return n >= (1 if len(ws) == 1 else 2) or q.lower() in name.lower()


def verdict(strong):
    return 'забито' if strong >= 3 else 'лидер' if strong else 'пусто'


def roblox(q, top):
    d = get('https://apis.roblox.com/search-api/omni-search?searchQuery=' + urllib.parse.quote(q) + f'&sessionId={uuid.uuid4()}&pageType=all', True)
    games = [c for g in (d or {}).get('searchResults', []) if g.get('contentGroupType') == 'Game' for c in g.get('contents', [])]
    games = [g for g in games if not g.get('isSponsored')][:max(top, 12)]
    ids = ','.join(str(g['universeId']) for g in games)
    meta = {x['id']: x for x in (get('https://games.roblox.com/v1/games?universeIds=' + ids, True) or {}).get('data', [])} if ids else {}
    rows = []
    for g in games:
        m = meta.get(g['universeId'], {}); cr = m.get('created', '')[:10]
        age = (TODAY - dt.date.fromisoformat(cr)).days if cr else None
        like = round(100 * g['totalUpVotes'] / max(1, g['totalUpVotes'] + g['totalDownVotes']))
        rows.append({'name': g['name'], 'playing': g['playerCount'], 'like': like, 'age_d': age, 'visits': m.get('visits'),
                     'url': f"https://www.roblox.com/games/{g['rootPlaceId']}"})
    strong = [r for r in rows if r['playing'] >= 5000]
    young = [r for r in strong if r['age_d'] is not None and r['age_d'] <= 90]
    return {'found': len(rows), 'strong': len(strong), 'young_strong': len(young), 'verdict': verdict(len(strong)),
            'top': sorted(rows, key=lambda r: -r['playing'])[:top]}


def steam(q, top):
    d = get('https://store.steampowered.com/search/results/?term=' + urllib.parse.quote(q) + '&infinite=1&count=25&json=1&cc=us&l=english', True)
    if not d: return {'found': 0, 'verdict': 'нет данных', 'top': []}
    rows = []
    for blk in re.split(r'<a href="https://store\.steampowered\.com/app/', d['results_html'].replace('\\/', '/'))[1:]:
        appid = re.match(r'(\d+)', blk).group(1)
        name = html.unescape((re.search(r'class="title">([^<]+)', blk) or [None, '?'])[1])
        rel = (re.search(r'search_released[^>]*>\s*([^<]*?)\s*<', blk) or [None, ''])[1]
        tip = html.unescape(html.unescape((re.search(r'data-tooltip-html="([^"]+)"', blk) or [None, ''])[1]))
        m = re.search(r'(\d+)% of the ([\d,]+) user reviews', tip)
        pos, n = (int(m[1]), int(m[2].replace(',', ''))) if m else (None, 0)
        date = None
        for f in ('%d %b, %Y', '%b %d, %Y', '%d %B, %Y', '%B %d, %Y'):
            try: date = dt.datetime.strptime(rel, f).date(); break
            except ValueError: pass
        rows.append({'name': name, 'reviews': n, 'positive': pos, 'release': rel or '—', 'released': bool(date and date <= TODAY),
                     'recent': bool(date and (TODAY - date).days <= 730), 'url': f'https://store.steampowered.com/app/{appid}/'})
    strong = [r for r in rows if r['reviews'] >= 1000]
    recent = sum(r['recent'] for r in strong)  # saturation = strong games of the last 2 years; older hits = evergreen demand
    return {'found': d.get('total_count', len(rows)), 'strong': len(strong), 'strong_recent': recent,
            'upcoming': sum(not r['released'] for r in rows), 'verdict': verdict(recent) + (' (+старые хиты)' if len(strong) > recent else ''),
            'top': sorted(rows, key=lambda r: -r['reviews'])[:top]}


def crazygames(q, top):
    games, seen = [], set()
    for qq in [q] + ([w for w in q.split() if len(w) > 3] if ' ' in q else []):  # phrase often finds nothing: then each word
        d = get('https://api.crazygames.com/v3/en_US/search?q=' + urllib.parse.quote(qq), True)
        for x in (d or {}).get('result', []):
            if x.get('recordType') == 'game' and x['slug'] not in seen: seen.add(x['slug']); games.append(x)
        if games and qq == q: break
    words = [w for w in q.lower().split() if len(w) > 3]
    if len(words) > 1:  # several words searched separately: games matching more words first
        games.sort(key=lambda x: -sum(w in x['name'].lower() for w in words))
    rows = []
    for g in games[:top]:
        b = get(f"https://www.crazygames.com/game/{g['slug']}") or ''
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', b, re.S)
        p = json.loads(m.group(1))['props']['pageProps'].get('game', {}) if m else {}
        votes = (p.get('upvotes') or 0) + (p.get('downvotes') or 0)
        rows.append({'name': g['name'], 'rating': p.get('rating'), 'votes': votes, 'mobile': g.get('mobileFriendly'),
                     'url': f"https://www.crazygames.com/game/{g['slug']}"})
        time.sleep(0.3)
    for r in rows: r['match'] = relevant(r['name'], q)
    strong = [r for r in rows if r['votes'] >= 50000 and r['match']]  # loosely related search hits are shown but not counted
    return {'found': len(games), 'matching': sum(r['match'] for r in rows), 'strong': len(strong), 'verdict': verdict(len(strong)),
            'top': sorted(rows, key=lambda r: (-r['match'], -r['votes']))}


def playgama(q, top):
    b = get('https://playgama.com/search?q=' + urllib.parse.quote(q)) or ''
    slugs = list(dict.fromkeys(re.findall(r'href="/game/([a-z0-9-]+)"', b)))
    rel = [s for s in slugs if relevant(s, q)]  # search page also lists unrelated featured games
    return {'found': len(rel), 'verdict': 'забито' if len(rel) >= 10 else 'лидер' if len(rel) >= 3 else 'пусто',
            'top': [{'name': s, 'url': f'https://playgama.com/game/{s}'} for s in rel[:top]]}


def main():
    a = sys.argv[1:]
    if not a or a[0].startswith('-'): print(__doc__); return
    opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    top, out = opt('--top', 8), opt('--out', '')
    res = {'date': TODAY.isoformat(), 'keywords': {}}
    for q in [k.strip() for k in a[0].split('|') if k.strip()]:
        r = {'roblox': roblox(q, top), 'steam': steam(q, top), 'crazygames': crazygames(q, top), 'playgama': playgama(q, top)}
        res['keywords'][q] = r
        print(f'\n## «{q}»')
        x = r['roblox']; print(f"Roblox: {x['verdict']} · найдено {x['found']}, сильных (≥5k онлайн) {x['strong']}, из них моложе 90 д {x['young_strong']}")
        for g in x['top'][:5]: print(f"   {g['playing']:>7} онлайн  {g['like']}%  {g['age_d']} д  {g['name'][:40]}  {g['url']}")
        x = r['steam']; print(f"Steam: {x['verdict']} · найдено {x['found']}, сильных (≥1000 отзывов) {x.get('strong', 0)}, из них за 2 года {x.get('strong_recent', 0)}, не вышли {x.get('upcoming', 0)}")
        for g in x['top'][:5]: print(f"   {g['reviews']:>7} отз  {g['positive'] or '—'}%  {g['release']:>12}  {g['name'][:40]}  {g['url']}")
        x = r['crazygames']; print(f"CrazyGames: {x['verdict']} · найдено {x['found']}, по названию {x['matching']}, сильных (≥50k голосов) {x['strong']}")
        for g in x['top'][:5]: print(f"   {g['votes']:>8} гол  {g['rating']}  {'' if g['match'] else '(не по теме?) '}{g['name'][:40]}  {g['url']}")
        x = r['playgama']; print(f"Playgama: {x['verdict']} · совпадений по названию {x['found']}: " + ', '.join(g['name'] for g in x['top'][:5]))
    if out:
        json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1); print(f'\n→ {out}')


main()
