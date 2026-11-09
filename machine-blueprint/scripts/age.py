"""age.py - turn a crisp light-on-blue render into an aged cyanotype blueprint while keeping text legible.

Usage: python age.py IN.png OUT.png [seed] [--strength 0..1]
Aging (mottling, folds, stains, edge wear, dust) is kept OFF the linework so every label stays readable.
"""

import sys, numpy as np
from PIL import Image, ImageFilter, ImageDraw
def lowfreq(h,w,cell,rng):
    small=rng.random((max(2,h//cell),max(2,w//cell)))
    return np.asarray(Image.fromarray((small*255).astype(np.uint8)).resize((w,h),Image.BICUBIC),dtype=np.float32)/255
def age(src,dst,seed=7,folds=(2,2),stains=None):
    rng=np.random.default_rng(seed)
    im=Image.open(src).convert("RGB"); w,h=im.size
    a=np.asarray(im,dtype=np.float32)/255
    bg=np.array([0x12,0x3f,0x73])/255
    # line mask = distance from background colour
    m=np.clip(np.abs(a-bg).max(axis=2)*2.2,0,1)
    mi=Image.fromarray((m*255).astype(np.uint8))
    bleed=np.asarray(mi.filter(ImageFilter.GaussianBlur(1.6)),dtype=np.float32)/255
    m=np.clip(np.maximum(m,bleed*0.35),0,1)
    m=np.asarray(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.35)),dtype=np.float32)/255
    keep=m.copy()  # protect linework from dirt
    # uneven exposure / line breakup
    m*=0.93+0.07*lowfreq(h,w,120,rng)
    # line colour: desaturated original, cream white
    lum=a.mean(axis=2,keepdims=True)
    lc=np.clip(np.clip(0.6*a+0.4*lum,0,1)*np.array([1.0,0.985,0.95])+0.08,0,1)
    # prussian base with mottling, sun fade, vignette
    base=np.array([0.10,0.24,0.42])
    mott=lowfreq(h,w,180,rng); mott2=lowfreq(h,w,40,rng)
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32); cx,cy=w/2,h/2
    vig=((xx-cx)/cx)**2+((yy-cy)/cy)**2
    fade=np.clip(1-((xx-w*0.85)**2+(yy-h*0.1)**2)/(0.55*w)**2,0,1)
    B=base[None,None,:]*(0.86+0.22*mott[...,None]+0.08*mott2[...,None])
    B=B*(1-0.28*np.clip(vig,0,1.6)[...,None]/1.6)
    B=B+fade[...,None]*np.array([0.07,0.09,0.10])
    # fine paper grain
    B=B+(rng.random((h,w,1))-0.5)*0.035
    out=B*(1-m[...,None])+lc*m[...,None]
    # fold creases
    for k in range(1,folds[0]):
        x=int(w*k/folds[0])+rng.integers(-8,8)
        g=np.exp(-((xx-x)**2)/(2*3.0**2)); s=np.exp(-((xx-x-6)**2)/(2*5.0**2))
        out=out+g[...,None]*0.10-s[...,None]*0.06
    for k in range(1,folds[1]):
        y=int(h*k/folds[1])+rng.integers(-8,8)
        g=np.exp(-((yy-y)**2)/(2*3.0**2)); s=np.exp(-((yy-y-6)**2)/(2*5.0**2))
        out=out+g[...,None]*0.10-s[...,None]*0.06
    # stains (coffee rings / water)
    for _ in range(stains if stains is not None else rng.integers(2,4)):
        sx,sy=rng.uniform(0.1,0.9)*w,rng.uniform(0.1,0.9)*h; r=rng.uniform(0.04,0.09)*min(w,h)
        d=np.sqrt((xx-sx)**2+(yy-sy)**2)
        ring=(np.exp(-((d-r)**2)/(2*(r*0.04)**2))*0.35+np.clip(1-d/r,0,1)*0.08)*(1-keep)
        out=out+ring[...,None]*np.array([0.10,0.08,0.03])
    # edge wear
    edge=np.minimum.reduce([xx,yy,w-xx,h-yy])
    ew=np.clip(1-edge/(0.025*min(w,h)),0,1)*(0.6+0.4*lowfreq(h,w,25,rng))
    out=out+ew[...,None]*np.array([0.18,0.18,0.15])
    out=np.clip(out,0,1)
    img=Image.fromarray((out*255).astype(np.uint8))
    d=ImageDraw.Draw(img)
    # dust, specks, pinholes, scratches
    for _ in range(int(w*h/90000)):
        x,y=int(rng.integers(0,w)),int(rng.integers(0,h)); r=rng.choice([1,1,1,2,3])
        if keep[min(y,h-1),min(x,w-1)]>0.08: continue
        c=(200,212,224) if rng.random()<0.5 else (12,28,52)
        d.ellipse([x-r,y-r,x+r,y+r],fill=c)
    for _ in range(5):
        x,y=int(rng.integers(0,w)),int(rng.integers(0,h)); L=rng.integers(20,int(0.06*w)); ang=rng.uniform(0,np.pi)
        d.line([x,y,x+L*np.cos(ang),y+L*np.sin(ang)],fill=(95,125,160),width=1)
    for (x,y) in ((26,26),(w-26,26),(26,h-26),(w-26,h-26)):
        d.ellipse([x-6,y-6,x+6,y+6],fill=(30,30,30)); d.ellipse([x-9,y-9,x+9,y+9],outline=(200,205,200))
    # torn corner
    d.polygon([(w,h),(w-70,h),(w-40,h-25),(w-55,h-40),(w,h-90)],fill=(40,36,30))
    img=img.filter(ImageFilter.UnsharpMask(1.5,60,2))
    img.save(dst,quality=92)
if __name__=="__main__":
    if len(sys.argv)<3 or sys.argv[1] in ("-h","--help"): print(__doc__); sys.exit(0 if len(sys.argv)>1 else 2)
    if sys.argv[1]=="--check": print("ready"); sys.exit(0)
    age(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 7); print(sys.argv[2])
