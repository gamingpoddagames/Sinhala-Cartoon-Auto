import json
import subprocess
import sys
from pathlib import Path

from story_engine import make_story


ROOT = Path(
    __file__
).resolve().parent.parent

CHARACTER_FILE = (
    ROOT /
    "characters" /
    "cartoon_character_v2.blend"
)

OUTPUT = (
    ROOT /
    "output"
)

BLENDER = Path(
    "/opt/blender/blender"
)

FFMPEG = "ffmpeg"


def episode_number():

    state = ROOT / "episode.txt"

    if state.exists():

        try:

            number = int(
                state.read_text().strip()
            )

        except Exception:

            number = 0

    else:

        number = 0

    number += 1

    state.write_text(
        str(number)
    )

    return number


def main():

    number = episode_number()

    episode = OUTPUT / (
        f"episode_{number:05d}"
    )

    episode.mkdir(
        parents=True,
        exist_ok=True
    )

    story = make_story(
        number
    )

    story_file = (
        episode /
        "story.json"
    )

    story_file.write_text(
        json.dumps(
            story,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    frames = (
        episode /
        "frames"
    )

    frames.mkdir(
        exist_ok=True
    )

    video = (
        episode /
        f"cartoon_{number:05d}.mp4"
    )

    print(
        "================================"
    )

    print(
        "CREATING EPISODE:",
        number
    )

    print(
        "LOCATION:",
        story["location"]
    )

    print(
        "ACTION:",
        story["action"]
    )

    print(
        "================================"
    )

    render_script = (
        ROOT /
        "src" /
        "render.py"
    )

    subprocess.run(
        [
            str(BLENDER),
            "--background",
            str(CHARACTER_FILE),
            "--python",
            str(render_script),
            "--",
            str(story_file),
            str(frames)
        ],
        check=True
    )

    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-framerate",
            "24",
            "-i",
            str(
                frames /
                "frame_%04d.png"
            ),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(video)
        ],
        check=True
    )

    print()
    print(
        "EPISODE COMPLETE:"
    )

    print(
        video
    )


if __name__ == "__main__":

    main()
