import argparse,json,subprocess,shutil,sys
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--mode',choices=['2d','3d'],default='2d')
p.add_argument('--story',default='stories/episode_001.json')
p.add_argument('--width',type=int,default=640);p.add_argument('--height',type=int,default=360)
p.add_argument('--fps',type=int,default=12);p.add_argument('--blender',default='blender')
p.add_argument('--voice-model');p.add_argument('--audio')
a=p.parse_args()
if a.voice_model and a.audio:raise SystemExit('Choose either --voice-model or --audio')
root=Path(__file__).resolve().parent
story=root/a.story
out=root/'output';out.mkdir(exist_ok=True)
frames=out/('frames_'+a.mode);frames.mkdir(exist_ok=True)
for old in frames.glob('*.png'):old.unlink()
cues=None;audio=a.audio
if a.voice_model:
 from audio_sync import scene_voice
 story,audio,cues=scene_voice(story,Path(a.voice_model).resolve(),out/'audio',a.fps)
data=json.loads(Path(story).read_text(encoding='utf-8'))
if a.mode=='2d':
 cmd=[sys.executable,str(root/'render_2d.py'),'--story',str(story),'--output',str(frames),'--width',str(a.width),'--height',str(a.height),'--fps',str(a.fps)]
else:
 cmd=[a.blender,'-b','--python',str(root/'studio.py'),'--','--story',str(story),'--output',str(frames),'--resolution',str(a.height),'--fps',str(a.fps)]
if cues:cmd+=['--cues',str(cues)]
subprocess.run(cmd,check=True)
def stamp(t):
 ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
t=0;lines=[];count=0
for i,sc in enumerate(data['scenes'],1):
 seconds=round(float(sc.get('seconds',3))*a.fps)/a.fps
 end=t+seconds;count+=round(seconds*a.fps)
 lines.extend([str(i),f'{stamp(t)} --> {stamp(end)}',sc['dialogue'],'']);t=end
if len(list(frames.glob('*.png')))!=count:raise RuntimeError('Frame count mismatch')
dest=out/('episode_'+a.mode+'.mp4')
dest.with_suffix('.srt').write_text('\n'.join(lines),encoding='utf-8')
command=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(a.fps),'-i',str(frames/'%06d.png')]
if audio:command+=['-i',str(audio)]
command+=['-c:v','libx264','-pix_fmt','yuv420p','-crf','24']
if audio:command+=['-c:a','aac','-af','apad','-t',str(t)]
else:command+=['-an']
command+=[str(dest)]
subprocess.run(command,check=True)
print('EPISODE_DONE',dest,'seconds',t,'audio',bool(audio),'mouth cues',bool(cues))
