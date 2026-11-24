# Découpe de la planche de Hrolf (6 × 7) : chaque image alignée sur ses pieds, toutes tournées vers la droite.
import sys, collections, colorsys
from PIL import Image, ImageFilter, ImageOps, ImageDraw
src, dst, dbg = sys.argv[1], sys.argv[2], sys.argv[3]
im=Image.open(src).convert('RGBA');W,H=im.size;C,R=6,7;cw,ch=W/C,H/R;K=0.58
NOMS=['idle','walk','atk','furie','cri','sol','mort']
MIROIR={0:{0,1,2,3,4,5},2:{0,4,5},3:{0,4,5},4:{5},5:{5}}  # images qui regardent à gauche sur la planche
m=im.getchannel('A').point(lambda v:255 if v>20 else 0).filter(ImageFilter.MaxFilter(3));px=m.load();vu=set();cells=collections.defaultdict(list)
for y in range(H):
  for x in range(W):
    if px[x,y] and (x,y) not in vu:
      q=collections.deque([(x,y)]);vu.add((x,y));pts=[]
      while q:
        u,v=q.popleft();pts.append((u,v))
        for a,b in ((u+1,v),(u-1,v),(u,v+1),(u,v-1)):
          if 0<=a<W and 0<=b<H and px[a,b] and (a,b) not in vu: vu.add((a,b));q.append((a,b))
      if len(pts)>=15:
        cx=sum(u for u,v in pts)/len(pts);cy=sum(v for u,v in pts)/len(pts);cells[(int(cy//ch),int(cx//cw))]+=pts
S=im.load()
def gris(p):  # pierre du marteau : peu saturée et claire
  h,s,v=colorsys.rgb_to_hsv(p[0]/255,p[1]/255,p[2]/255);return s<.18 and v>.33
frames={}
for (r,c),pts in cells.items():
  x0=min(u for u,v in pts);y0=min(v for u,v in pts);x1=max(u for u,v in pts);y1=max(v for u,v in pts)
  f=Image.new('RGBA',(x1-x0+1,y1-y0+1));fp=f.load()
  for u,v in pts: fp[u-x0,v-y0]=S[u,v]
  if c in MIROIR.get(r,()): f=ImageOps.mirror(f)
  frames[(r,c)]=f
# Ancre horizontale : les pieds pour les gestes sur place ; la tête pour la marche (la planche fait tanguer
# le corps de ±5 px d'une image à l'autre : calé sur les pieds, il flotte). Ancre verticale : le pied le plus bas.
def ancre(f,tete):
  a=f.load();w,h=f.size;ok=[(x,y) for y in range(h) for x in range(w) if a[x,y][3]>60 and not gris(a[x,y])]
  bas=max(y for x,y in ok);haut=min(y for x,y in ok)
  if tete: bande=[x for x,y in ok if y<=haut+(bas-haut)*.16]
  else: bande=[x for x,y in ok if y>=bas-h*.12 and y>=h*.5] or [x for x,y in ok]
  return sum(bande)/len(bande),(haut if tete else bas)
A={k:ancre(f,k[0]==1) for k,f in frames.items()}
# Marche : la tête est calée en hauteur aussi (la planche la fait sauter de ±2 px) ; le jeu ajoute un balancement régulier.
hw=[f.size[1] for k,f in frames.items() if k[0]==1];hw.sort();Dm=hw[len(hw)//2]-1
for k in list(A):
  if k[0]==1:A[k]=(A[k][0],A[k][1]+Dm)
L=max(ax for (ax,ay) in A.values());Rt=max(f.size[0]-A[k][0] for k,f in frames.items());Hh=max(A[k][1] for k in frames);Bb=max(f.size[1]-A[k][1] for k,f in frames.items())
half=int(max(L,Rt))+2;FW,FH=2*half,int(Hh+Bb)+4;base=int(Hh)+1
ow,oh=round(FW*K),round(FH*K);print('image',ow,oh,'pieds',round(base/FH,3))
dbgim=Image.new('RGBA',(ow*6,oh*7),(60,70,60,255));d=ImageDraw.Draw(dbgim)
for r,n in enumerate(NOMS):
  strip=Image.new('RGBA',(ow*6,oh))
  for c in range(6):
    fr=Image.new('RGBA',(FW,FH));ax,ay=A[(r,c)];fr.alpha_composite(frames[(r,c)],(int(round(half-ax)),int(round(base-ay))))
    t=fr.resize((ow,oh),Image.LANCZOS);strip.paste(t,(c*ow,0));dbgim.alpha_composite(t,(c*ow,r*oh))
  strip.save(f'{dst}/hrolf_{n}.webp',lossless=True)
for c in range(6): d.line([(c*ow+ow/2,0),(c*ow+ow/2,oh*7)],fill=(255,0,0,160))
for r in range(7): d.line([(0,r*oh+base*K),(ow*6,r*oh+base*K)],fill=(255,0,0,160))
dbgim.resize((ow*12,oh*14),Image.NEAREST).save(dbg)
