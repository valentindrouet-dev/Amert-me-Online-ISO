# Découpe des planches d'interface : chaque élément (composante connexe) recadré, listé par position.
import sys, collections
from PIL import Image, ImageFilter
def elements(path):
  im=Image.open(path).convert('RGBA');W,H=im.size
  m=im.getchannel('A').point(lambda v:255 if v>24 else 0).filter(ImageFilter.MaxFilter(5));px=m.load();vu=set();out=[]
  for y in range(0,H,2):
    for x in range(0,W,2):
      if px[x,y] and (x,y) not in vu:
        q=collections.deque([(x,y)]);vu.add((x,y));x0=x1=x;y0=y1=y;n=0
        while q:
          u,v=q.popleft();n+=1;x0=min(x0,u);x1=max(x1,u);y0=min(y0,v);y1=max(y1,v)
          for a,b in ((u+1,v),(u-1,v),(u,v+1),(u,v-1)):
            if 0<=a<W and 0<=b<H and px[a,b] and (a,b) not in vu: vu.add((a,b));q.append((a,b))
        if n>400: out.append((y0,x0,x1,y1))
  out.sort(key=lambda b:(round(b[0]/60),b[1]))
  return im,[(x0,y0,x1+1,y1+1) for y0,x0,x1,y1 in out]
if __name__=='__main__':
  for p in sys.argv[1:]:
    im,bs=elements(p);print(p,len(bs))
    for i,b in enumerate(bs):print(' ',i,b,(b[2]-b[0],b[3]-b[1]),'centre alpha',im.getpixel(((b[0]+b[2])//2,(b[1]+b[3])//2))[3])
