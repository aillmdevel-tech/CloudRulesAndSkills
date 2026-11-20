"""Usage: python3 -I fetch_steam.py <StyleLibrary> <appid> [appid...]  -> _raw/app_<id>.json, page_<id>.html, data/summary.json"""
import sys,os,json,re,html,urllib.request
lib=sys.argv[1]; raw=lib+'/_raw'; os.makedirs(raw,exist_ok=True)
H={'Cookie':'birthtime=0; wants_mature_content=1','User-Agent':'Mozilla/5.0'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30).read()
sp=lib+'/data/summary.json'; out=json.load(open(sp)) if os.path.exists(sp) else {}
for id in sys.argv[2:]:
    j=json.loads(get(f'https://store.steampowered.com/api/appdetails?appids={id}&l=english'))[id]
    if not j.get('success'): print(id,'FAIL'); continue
    x=j['data']; p=get(f'https://store.steampowered.com/app/{id}/?l=english').decode('utf8','ignore')
    open(f'{raw}/page_{id}.html','w').write(p)
    tags=[html.unescape(t.strip()) for t in re.findall(r'class="app_tag"[^>]*>\s*([^<]+?)\s*<',p)]
    out[id]=dict(name=x['name'],dev=x.get('developers'),date=x.get('release_date',{}).get('date'),genres=[g['description'] for g in x.get('genres',[])],tags=tags[:15],short=x.get('short_description'),shots=[s['path_full'] for s in x.get('screenshots',[])],header=x.get('header_image'),movies=[{k:m.get(k) for k in ('name','mp4','webm','hls_h264','dash_h264')} for m in x.get('movies',[])])
    print(id,x['name'],'|',', '.join(tags[:12]),'| movies:',[m['name'] for m in out[id]['movies']])
json.dump(out,open(sp,'w'),indent=1)
