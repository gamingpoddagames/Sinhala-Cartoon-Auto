import json
import subprocess
from pathlib import Path

from story_engine import make_story


ROOT = Path(__file__).resolve().parent.parent

CHARACTER_FILE = (
    ROOT / "characters" / "cartoon_character_v2.blend"
)

OUTPUT_DIR = ROOT / "output"

BLENDER = Path("/opt/blender/blender")

FFMPEG = "ffmpeg"


def prepare_output():

    # If output exists as a FILE, remove the bad file.
    if OUTPUT_DIR.exists() and not OUTPUT_DIR.is_dir():

        print("Removing invalid output file:")
        print(OUTPUT_DIR)

        OUTPUT_DIR.unlink()

    # Create output directory.
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def get_episode_number():

    # GitHub Actions provides a unique run number.
    import os

    run_number = os.environ.get(
        "GITHUB_RUN_NUMBER"
    )

    if run_number:

        return int(run_number)

    # Local testing fallback.
    state = ROOT / ".episode_state"

    if state.exists():

        try:
            number = int(
                state.read_text(
                    encoding="utf-8"
                )
            ) + 1

        except Exception:

            number = 1

    else:

        number = 1

    state.write_text(
        str(number),
        encoding="utf-8"
    )

    return number


def main():

    print()
    print("=" * 60)
    print(" SINHALA CARTOON FACTORY")
    print("=" * 60)

    prepare_output()

    # Check character
    if not CHARACTER_FILE.exists():

        raise FileNotFoundError(
            f"""
Character file missing:

{CHARACTER_FILE}

Make sure this file exists in GitHub:

characters/cartoon_character_v2.blend
"""
        )

    episode = get_episode_number()

    episode_dir = (
        OUTPUT_DIR /
        f"episode_{episode:05d}"
    )

    episode_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    frames_dir = (
        episode_dir / "frames"
    )

    frames_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------
    # STORY
    # --------------------------------------------------

    story = make_story(
        episode
    )

    story_file = (
        episode_dir /
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

    print()
    print("Episode:", episode)
    print("Location:", story["location"])
    print("Action:", story["action"])

    # --------------------------------------------------
    # BLENDER
    # --------------------------------------------------

    render_script = (
        ROOT /
        "src" /
        "render.py"
    )

    if not render_script.exists():

        raise FileNotFoundError(
            f"Missing:

{render_script}"
        )

    print()
    print("Starting Blender...")

    command = [
        str(BLENDER),
        "--background",
        str(CHARACTER_FILE),
        "--python",
        str(render_script),
        "--",
        str(story_file),
        str(frames_dir)
    ]

    subprocess.run(
        command,
        check=True
    )

    # --------------------------------------------------
    # CHECK FRAMES
    # --------------------------------------------------

    frames = list(
        frames_dir.glob(
            "frame_*.png"
        )
    )

    if not frames:

        raise RuntimeError(
            "Blender created no PNG frames."
        )

    print(
        f"Frames created: {len(frames)}"
    )

    # --------------------------------------------------
    # FFMPEG
    # --------------------------------------------------

    video = (
        episode_dir /
        f"cartoon_{episode:05d}.mp4"
    )

    print()
    print("Starting FFmpeg...")

    ffmpeg_command = [
        FFMPEG,
        "-y",
        "-framerate",
        "24",
        "-i",
        str(
            frames_dir /
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
    ]

    subprocess.run(
        ffmpeg_command,
        check=True
    )

    if not video.exists():

        raise RuntimeError(
            "FFmpeg did not create the MP4."
        )

    print()
    print("=" * 60)
    print(" EPISODE COMPLETE")
    print("=" * 60)

    print()
    print(video)
    print()


if __name__ == "__main__":
    main()
