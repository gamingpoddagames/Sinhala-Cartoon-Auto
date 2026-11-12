import argparse,json,math
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser()
p.add_argument('--story',required=True);p.add_argument('--output',required=True)
p.add_argument('--width',type=int,default=640);p.add_argument('--height',type=int,default=360)
p.add_argument('--fps',type=int,default=12);p.add_argument('--cues',default=None)
a=p.parse_args()
data=json.loads(Path(a.story).read_text(encoding='utf-8'))
cues=json.loads(Path(a.cues).read_text(encoding='utf-8'))['mouth'] if a.cues else None
W,H=a.width,a.height;out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
def circ(d,box,color):d.ellipse(tuple(int(z) for z in box),fill=color)
def frame(f,k,n,action,mouth_open):
 im=Image.new('RGB',(W,H),'#87cefa');d=ImageDraw.Draw(im)
 d.ellipse((-W//4,H//3,W//2,H),fill='#69b77f')
 d.ellipse((W//4,H//3,W+W//4,H),fill='#55a96a')
 d.rectangle((0,int(H*.74),W,H),fill='#8bc967')
 for xx in [int(W*.12),int(W*.72)]:
  d.rectangle((xx,int(H*.36),xx+int(W*.025),int(H*.75)),fill='#865f3c')
  circ(d,(xx-int(W*.05),H*.2,xx+int(W*.1),H*.48),'#34804b')
 d.rectangle((int(W*.78),int(H*.47),int(W*.95),int(H*.74)),fill='#f4d298')
 d.polygon([(int(W*.75),int(H*.47)),(int(W*.865),int(H*.31)),(int(W*.98),int(H*.47))],fill='#c35351')
 progress=k/max(1,n-1)
 cx=int(W*(.34+.33*progress if action=='walk' else .46))
 lift=int(H*.14*max(0,math.sin(math.pi*progress))) if action=='jump' else 0
 cy=int(H*.78)-lift
 z=min(W/640,H/360); Z=lambda q:int(q*z)
 swing=Z(8*math.sin(k*.7)) if action=='walk' else 0
 d.line([(cx-Z(12),cy-Z(57)),(cx-Z(12)+swing,cy-Z(8))],fill='#243d6f',width=max(2,Z(12)))
 d.line([(cx+Z(12),cy-Z(57)),(cx+Z(12)-swing,cy-Z(8))],fill='#243d6f',width=max(2,Z(12)))
 d.line([(cx-Z(23),cy-Z(102)),(cx-Z(35),cy-Z(78)+swing)],fill='#b87752',width=max(2,Z(10)))
 d.line([(cx+Z(23),cy-Z(102)),(cx+Z(35),cy-Z(78)-swing)],fill='#b87752',width=max(2,Z(10)))
 d.rounded_rectangle((cx-Z(25),cy-Z(118),cx+Z(25),cy-Z(52)),radius=max(2,Z(9)),fill='#ffad44')
 circ(d,(cx-Z(35),cy-Z(178),cx+Z(35),cy-Z(112)),'#c9865f')
 circ(d,(cx-Z(31),cy-Z(181),cx+Z(31),cy-Z(160)),'#302d37')
 for ex in [-Z(13),Z(13)]:
  circ(d,(cx+ex-Z(8),cy-Z(151),cx+ex+Z(8),cy-Z(132)),'white')
  circ(d,(cx+ex-Z(2),cy-Z(146),cx+ex+Z(3),cy-Z(137)),'#242637')
 if mouth_open: circ(d,(cx-Z(10),cy-Z(119),cx+Z(10),cy-Z(100)),'#78343d')
 else:d.arc((cx-Z(13),cy-Z(123),cx+Z(13),cy-Z(104)),0,180,fill='#78343d',width=max(1,Z(3)))
 return im
f=0
for sc in data['scenes']:
 n=round(float(sc.get('seconds',3))*a.fps)
 for k in range(n):
  f+=1;frame(f,k,n,sc.get('action','talk'),(cues[f-1]>.13 if cues and f-1<len(cues) else sc.get('action','talk')=='talk' and k//3%2==0)).save(out/f'{f:06d}.png')
print('RENDER_DONE',f)
