"""Usage: python -I sheets.py <StyleLibrary>/_raw  -> frames_sheet.jpg, shots_sheet.jpg, palettes.json (needs Pillow)"""
import sys,os,glob,json
from PIL import Image
raw=sys.argv[1]
def pal(imgs,k=8):
    px=[]
    for p in imgs:
        im=Image.open(p).convert('RGB').resize((64,36));px+=list(im.getdata())
    big=Image.new('RGB',(len(px),1));big.putdata(px)
    q=big.quantize(colors=k,method=Image.Quantize.MEDIANCUT)
    cnt=sorted(q.getcolors(),reverse=True);pl=q.getpalette()
    tot=sum(c for c,_ in cnt)
    out=[('#%02x%02x%02x'%tuple(pl[i*3:i*3+3]),round(100*c/tot)) for c,i in cnt]
    lum=[0.2126*r+0.7152*g+0.0722*b for r,g,b in px];m=sum(lum)/len(lum)
    sat=[(max(p)-min(p))/255 for p in px]
    return out,round(m),round(100*sum(sat)/len(sat))
res={}
for w in sorted(glob.glob(raw+'/*/')):
    slug=os.path.basename(w[:-1]);fr=sorted(glob.glob(w+'frames/*.jpg'));sh=sorted(glob.glob(w+'shots/*.jpg'))
    if not sh: continue
    # contact sheet of frames, 30 evenly spaced, 6 cols, with second label
    if fr:
        n=min(30,len(fr));sel=[fr[int(i*len(fr)/n)] for i in range(n)]
        tw,th=320,180;cols=6;rows=(n+cols-1)//cols
        cs=Image.new('RGB',(cols*tw,rows*th))
        from PIL import ImageDraw
        d=ImageDraw.Draw(cs)
        for i,p in enumerate(sel):
            im=Image.open(p).convert('RGB').resize((tw,th));cs.paste(im,((i%cols)*tw,(i//cols)*th))
            sec=int(os.path.basename(p)[1:4])-1;d.text(((i%cols)*tw+4,(i//cols)*th+4),f"{sec//60}:{sec%60:02d}",fill=(255,255,0))
        cs.save(w+'frames_sheet.jpg',quality=82)
    # screenshot sheet
    tw,th=480,270;cols=3;rows=(len(sh)+2)//3
    ss=Image.new('RGB',(cols*tw,rows*th))
    for i,p in enumerate(sh): ss.paste(Image.open(p).convert('RGB').resize((tw,th)),((i%cols)*tw,(i//cols)*th))
    ss.save(w+'shots_sheet.jpg',quality=82)
    p,l,s=pal(sh+fr[::5])
    res[slug]=dict(palette=p,mean_luma=l,mean_sat_pct=s,frames=len(fr),shots=len(sh))
    print(slug,len(fr),'frames | luma',l,'sat%',s,'|',' '.join(f"{h}:{c}%" for h,c in p))
json.dump(res,open(raw+'/palettes.json','w'),indent=1)
