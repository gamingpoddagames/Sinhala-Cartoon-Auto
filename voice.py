"""Local optional Sinhala Piper voice synthesis. Requires model downloaded by user."""
import argparse,json,subprocess,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--story',default='stories/episode_001.json')
p.add_argument('--model',required=True);p.add_argument('--output',default='output/voice.wav')
a=p.parse_args()
if not shutil.which('piper'):raise SystemExit('Install piper-tts to enable narration')
if not Path(a.model).exists():raise SystemExit('Piper Sinhala voice model missing')
data=json.loads(Path(a.story).read_text(encoding='utf-8'))
Path(a.output).parent.mkdir(exist_ok=True,parents=True)
subprocess.run(['piper','--model',a.model,'--output_file',a.output],input=' '.join(s['dialogue'] for s in data['scenes']),text=True,check=True)
print('Voice file created:',a.output)
