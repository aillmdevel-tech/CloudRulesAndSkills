"""Usage: FFMPEG=<ffmpeg> python3 -I grab_media.py <StyleLibrary> [slug...]  -> _raw/<slug>/shots, frames (1 fps, 640px)"""
import json,sys,os,subprocess,urllib.request
lib=sys.argv[1]; raw=lib+'/_raw'; d=json.load(open(lib+'/data/summary.json'))
pick=json.load(open(lib+'/data/picks.json'))  # appid: [trailer index, slug]
only=sys.argv[2:] 
for id,(mi,slug) in pick.items():
    if only and slug not in only: continue
    w=f"{raw}/{slug}"; os.makedirs(w+'/shots',exist_ok=True); os.makedirs(w+'/frames',exist_ok=True)
    g=d[id]
    for i,u in enumerate(g['shots'][:10]):
        p=f"{w}/shots/s{i:02d}.jpg"
        if not os.path.exists(p): urllib.request.urlretrieve(u,p)
    m=g['movies'][mi]; url=m.get('hls_h264') or m.get('mp4',{}).get('max')
    if not os.listdir(w+'/frames'):
        r=subprocess.run([os.environ.get('FFMPEG','ffmpeg'),'-loglevel','error','-y','-i',url,'-vf','fps=1,scale=640:-2','-q:v','4',f"{w}/frames/f%03d.jpg"],capture_output=True,text=True)
        if r.returncode: print(slug,'ERR',r.stderr[-300:])
    print(slug,'shots',len(os.listdir(w+'/shots')),'frames',len(os.listdir(w+'/frames')))
