import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--mode',choices=['2d','3d'],default='2d')
p.add_argument('--story',default='stories/episode_001.json')
p.add_argument('--width',type=int,default=640)
p.add_argument('--height',type=int,default=360)
p.add_argument('--fps',type=int,default=12)
p.add_argument('--blender',default='blender')
a=p.parse_args()
root=Path(__file__).resolve().parent
story=root/a.story
data=json.loads(story.read_text(encoding='utf-8'))
out=root/'output';out.mkdir(exist_ok=True)
frames=out/('frames_'+a.mode);frames.mkdir(exist_ok=True)
if a.mode=='2d':
 subprocess.run(['python',str(root/'render_2d.py'),'--story',str(story),'--output',str(frames),'--width',str(a.width),'--height',str(a.height),'--fps',str(a.fps)],check=True)
else:
 subprocess.run([a.blender,'-b','--python',str(root/'studio.py'),'--','--story',str(story),'--output',str(frames),'--resolution',str(a.height),'--fps',str(a.fps)],check=True)
def stamp(t):
 ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
t=0; lines=[]
for i,sc in enumerate(data['scenes'],1):
 end=t+float(sc.get('seconds',3))
 lines.extend([str(i),f'{stamp(t)} --> {stamp(end)}',sc['dialogue'],'']);t=end
(out/('episode_'+a.mode+'.srt')).write_text('\n'.join(lines),encoding='utf-8')
dest=out/('episode_'+a.mode+'.mp4')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(a.fps),'-i',str(frames/'%06d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-crf','24',str(dest)],check=True)
print('EPISODE_DONE',dest,'seconds',t)
