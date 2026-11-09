"""paper.py - generate aged manila/vellum page backgrounds for the technical order.

Usage: python paper.py OUT_DIR [count]   -> OUT_DIR/paper0.jpg ... (stains kept faint so text stays readable)
"""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
def lowfreq(h,w,cell,rng):
    s=rng.random((max(2,h//cell),max(2,w//cell)))
    return np.asarray(Image.fromarray((s*255).astype(np.uint8)).resize((w,h),Image.BICUBIC),dtype=np.float32)/255
def paper(path,seed,w=1275,h=1650):
    rng=np.random.default_rng(seed)
    base=np.array([0.93,0.88,0.76])
    m=lowfreq(h,w,160,rng); m2=lowfreq(h,w,30,rng)
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    vig=((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2
    out=base*(0.94+0.06*m[...,None]+0.03*m2[...,None])
    out=out-np.clip(vig,0,2)[...,None]*np.array([0.05,0.07,0.10])
    out=out+(rng.random((h,w,1))-0.5)*0.03
    for _ in range(rng.integers(1,3)):
        sx,sy=rng.uniform(.15,.85)*w,rng.uniform(.1,.9)*h; r=rng.uniform(.05,.1)*w
        d=np.sqrt((xx-sx)**2+(yy-sy)**2)
        out=out-(np.exp(-((d-r)**2)/(2*(r*.035)**2))*0.06+np.clip(1-d/r,0,1)*0.015)[...,None]*np.array([0.2,0.45,0.9])
    y=h//2+rng.integers(-10,10); g=np.exp(-((yy-y)**2)/8); s=np.exp(-((yy-y-4)**2)/18)
    out=out+g[...,None]*0.04-s[...,None]*0.05
    edge=np.minimum.reduce([xx,yy,w-xx,h-yy]); ew=np.clip(1-edge/22,0,1)*(0.5+0.5*lowfreq(h,w,12,rng))
    out=out-ew[...,None]*np.array([0.10,0.14,0.22])
    img=Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(img)
    for _ in range(int(w*h/150000)):
        x,y=rng.integers(0,w),rng.integers(0,h); r=rng.choice([1,1,2]); d.ellipse([x-r,y-r,x+r,y+r],fill=(120,100,70))
    for x in (60,): 
        for y in (h*0.2,h*0.5,h*0.8): d.ellipse([x-9,y-9,x+9,y+9],fill=(70,60,45)); d.ellipse([x-12,y-12,x+12,y+12],outline=(160,140,110),width=2)
    img.filter(ImageFilter.GaussianBlur(0.4)).save(path,quality=90)
import sys, os
if __name__=="__main__":
    if len(sys.argv)<2 or sys.argv[1] in ("-h","--help"): print(__doc__); sys.exit(0 if len(sys.argv)>1 else 2)
    if sys.argv[1]=="--check": print("ready"); sys.exit(0)
    os.makedirs(sys.argv[1],exist_ok=True); n=int(sys.argv[2]) if len(sys.argv)>2 else 4
    for i in range(n): paper(os.path.join(sys.argv[1],f"paper{i}.jpg"),100+i)
    print(sys.argv[1])
