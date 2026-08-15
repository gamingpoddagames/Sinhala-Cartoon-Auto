import json
import os
import subprocess
from pathlib import Path

from story_engine import make_story


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

CHARACTER_FILE = (
    ROOT / "characters" / "cartoon_character_v2.blend"
)

OUTPUT_DIR = ROOT / "output"

BLENDER = Path("/opt/blender/blender")

FFMPEG = "ffmpeg"


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

def prepare_output():

    # GitHub does not need to contain an output folder.
    # The runner creates it automatically.

    if OUTPUT_DIR.exists():

        if OUTPUT_DIR.is_file():

            print(
                "Removing invalid output file:"
            )

            print(
                OUTPUT_DIR
            )

            OUTPUT_DIR.unlink()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# EPISODE NUMBER
# ============================================================

def get_episode_number():

    # GitHub Actions gives every workflow run
    # a unique number.

    run_number = os.environ.get(
        "GITHUB_RUN_NUMBER"
    )

    if run_number:

        try:

            return int(run_number)

        except ValueError:

            pass

    # Local fallback

    state_file = (
        ROOT / ".episode_state"
    )

    if state_file.exists():

        try:

            number = int(
                state_file.read_text(
                    encoding="utf-8"
                ).strip()
            )

            number += 1

        except Exception:

            number = 1

    else:

        number = 1

    state_file.write_text(
        str(number),
        encoding="utf-8"
    )

    return number


# ============================================================
# CHECK CHARACTER
# ============================================================

def check_character():

    if not CHARACTER_FILE.exists():

        raise FileNotFoundError(
            "\n"
            "Character file is missing.\n"
            "\n"
            f"Expected file:\n{CHARACTER_FILE}\n"
            "\n"
            "Upload your Blender character as:\n"
            "characters/cartoon_character_v2.blend\n"
        )


# ============================================================
# CHECK BLENDER
# ============================================================

def check_blender():

    if not BLENDER.exists():

        raise FileNotFoundError(
            "\n"
            "Blender was not found.\n"
            "\n"
            f"Expected:\n{BLENDER}\n"
        )


# ============================================================
# GENERATE STORY
# ============================================================

def create_story(
    episode_number,
    episode_dir
):

    story = make_story(
        episode_number
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
    print(
        "Story generated."
    )

    print(
        "Episode:",
        episode_number
    )

    print(
        "Location:",
        story.get(
            "location",
            "unknown"
        )
    )

    print(
        "Action:",
        story.get(
            "action",
            "unknown"
        )
    )

    return story, story_file


# ============================================================
# BLENDER
# ============================================================

def run_blender(
    story_file,
    frames_dir
):

    render_script = (
        ROOT /
        "src" /
        "render.py"
    )

    if not render_script.exists():

        raise FileNotFoundError(
            "\n"
            "Blender render script is missing.\n"
            "\n"
            f"Expected:\n{render_script}\n"
        )

    print()
    print(
        "=" * 60
    )

    print(
        "STARTING BLENDER"
    )

    print(
        "=" * 60
    )

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


# ============================================================
# CHECK FRAMES
# ============================================================

def check_frames(
    frames_dir
):

    frames = sorted(
        frames_dir.glob(
            "frame_*.png"
        )
    )

    if not frames:

        raise RuntimeError(
            "\n"
            "Blender finished but no PNG frames were created.\n"
            f"Frames directory:\n{frames_dir}\n"
        )

    print()
    print(
        f"PNG frames created: {len(frames)}"
    )

    return frames


# ============================================================
# FFMPEG
# ============================================================

def run_ffmpeg(
    frames_dir,
    video_file
):

    print()
    print(
        "=" * 60
    )

    print(
        "STARTING FFMPEG"
    )

    print(
        "=" * 60
    )

    command = [

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

        str(video_file)
    ]

    subprocess.run(
        command,
        check=True
    )


# ============================================================
# VERIFY VIDEO
# ============================================================

def verify_video(
    video_file
):

    if not video_file.exists():

        raise RuntimeError(
            "\n"
            "FFmpeg completed but the MP4 was not created.\n"
            f"Expected:\n{video_file}\n"
        )

    size = (
        video_file.stat().st_size
    )

    if size <= 0:

        raise RuntimeError(
            "\n"
            "The generated MP4 is empty.\n"
            f"File:\n{video_file}\n"
        )

    size_mb = (
        size /
        (1024 * 1024)
    )

    print()
    print(
        f"Video size: {size_mb:.2f} MB"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "=" * 60
    )

    print(
        "SINHALA CARTOON FACTORY"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Prepare directories
    # --------------------------------------------------------

    prepare_output()

    # --------------------------------------------------------
    # Check required files
    # --------------------------------------------------------

    check_character()

    check_blender()

    # --------------------------------------------------------
    # Episode number
    # --------------------------------------------------------

    episode_number = (
        get_episode_number()
    )

    print()
    print(
        f"Creating Episode {episode_number}"
    )

    # --------------------------------------------------------
    # Episode directory
    # --------------------------------------------------------

    episode_dir = (
        OUTPUT_DIR /
        f"episode_{episode_number:05d}"
    )

    episode_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Frames
    # --------------------------------------------------------

    frames_dir = (
        episode_dir /
        "frames"
    )

    frames_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Story
    # --------------------------------------------------------

    story, story_file = create_story(
        episode_number,
        episode_dir
    )

    # --------------------------------------------------------
    # Blender
    # --------------------------------------------------------

    run_blender(
        story_file,
        frames_dir
    )

    # --------------------------------------------------------
    # Verify PNG frames
    # --------------------------------------------------------

    check_frames(
        frames_dir
    )

    # --------------------------------------------------------
    # MP4
    # --------------------------------------------------------

    video_file = (
        episode_dir /
        f"cartoon_{episode_number:05d}.mp4"
    )

    run_ffmpeg(
        frames_dir,
        video_file
    )

    # --------------------------------------------------------
    # Verify MP4
    # --------------------------------------------------------

    verify_video(
        video_file
    )

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "CARTOON EPISODE COMPLETE"
    )

    print(
        "=" * 60
    )

    print()
    print(
        f"Episode: {episode_number}"
    )

    print(
        f"Video: {video_file}"
    )

    print()
    print(
        "SUCCESS"
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()
