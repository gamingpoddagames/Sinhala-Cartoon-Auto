# Sinhala Cartoon Factory (2D + 3D)

2D cartoon rendering + Blender 3D starter + optional Sinhala Piper TTS.

## Run

Install Python, Pillow and FFmpeg, then:

```bash
pip install -r requirements.txt
python factory.py --mode 2d --width 640 --height 360 --fps 12
```

Output: `output/episode_2d.mp4` and `output/episode_2d.srt`.

For 3D, install Blender and run `python factory.py --mode 3d --blender blender`. For narration, install `piper-tts`, obtain a licensed Sinhala Piper ONNX voice, then run `python voice.py --model path/to/si_LK-sinhala-medium.onnx`.

## Verified status

2D MP4 rendering was tested in a separate working environment (13-second episode, H.264). GitHub Actions 2D workflow has been added but its hosted run has **not yet been verified**. 3D rendering and Sinhala Piper speech also require testing on a machine with Blender and the voice model. Current mouth animation is approximate, not audio-derived lip-sync. Daily workflow currently renders the same episode rather than generating fresh scripts automatically.
