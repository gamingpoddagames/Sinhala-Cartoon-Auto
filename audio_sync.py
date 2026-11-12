"""Scene-wise Sinhala Piper speech + WAV amplitude mouth cues."""
import json,subprocess,shutil,wave,math
from array import array
from pathlib import Path
RATE=22050
def scene_voice(story_path,model,outdir,fps=12):
 if not shutil.which('piper'):raise RuntimeError('Piper not installed')
 if not Path(model).is_file():raise FileNotFoundError(model)
 d=json.loads(Path(story_path).read_text(encoding='utf-8'));out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
 data=array('h');scenes=[];cues=[]
 for i,s in enumerate(d['scenes']):
  raw=out/f'raw_{i}.wav';norm=out/f'voice_{i}.wav'
  subprocess.run(['piper','--model',str(model),'--output_file',str(raw)],input=s['dialogue'],text=True,check=True)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw),'-ar',str(RATE),'-ac','1','-c:a','pcm_s16le',str(norm)],check=True)
  with wave.open(str(norm),'rb') as w:
   samples=array('h');samples.frombytes(w.readframes(w.getnframes()))
  frames=max(round(float(s.get('seconds',3))*fps),math.ceil((len(samples)/RATE+.35)*fps))
  scenes.append({**s,'seconds':frames/fps})
  data.extend(samples);data.extend([0]*max(0,round(frames*RATE/fps)-len(samples)))
  for k in range(frames):
   lo=round(k*RATE/fps);hi=min(len(samples),round((k+1)*RATE/fps))
   seg=samples[lo:hi] if lo<len(samples) else []
   rms=math.sqrt(sum(v*v for v in seg)/len(seg))/32768 if seg else 0
   cues.append(round(min(1,rms*10),3))
 dest=out/'narration.wav'
 with wave.open(str(dest),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(data.tobytes())
 timed=out/'timed_story.json';timed.write_text(json.dumps({**d,'scenes':scenes},ensure_ascii=False),encoding='utf-8')
 cue=out/'mouth_cues.json';cue.write_text(json.dumps({'fps':fps,'mouth':cues}),encoding='utf-8')
 return timed,dest,cue
