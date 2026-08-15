import bpy
import sys
import json
import math
from pathlib import Path


FPS = 24
WIDTH = 1280
HEIGHT = 720


def get(name):

    obj = bpy.data.objects.get(name)

    if obj is None:
        print("WARNING: missing:", name)

    return obj


def rotation_key(obj, frame, x=0, y=0, z=0):

    if obj is None:
        return

    obj.rotation_euler = (
        math.radians(x),
        math.radians(y),
        math.radians(z)
    )

    obj.keyframe_insert(
        data_path="rotation_euler",
        frame=frame
    )


def location_key(obj, frame, x=None, y=None, z=None):

    if obj is None:
        return

    p = obj.location.copy()

    if x is not None:
        p.x = x

    if y is not None:
        p.y = y

    if z is not None:
        p.z = z

    obj.location = p

    obj.keyframe_insert(
        data_path="location",
        frame=frame
    )


def scale_key(obj, frame, scale_z):

    if obj is None:
        return

    s = obj.scale.copy()

    s.z = scale_z

    obj.scale = s

    obj.keyframe_insert(
        data_path="scale",
        frame=frame
    )


def walk(character, start, end, direction=1):

    leg_l = get(f"{character}_Leg_L")
    leg_r = get(f"{character}_Leg_R")

    shoe_l = get(f"{character}_Shoe_L")
    shoe_r = get(f"{character}_Shoe_R")

    arm_l = get(f"{character}_Arm_L")
    arm_r = get(f"{character}_Arm_R")

    hand_l = get(f"{character}_Hand_L")
    hand_r = get(f"{character}_Hand_R")

    torso = get(f"{character}_Torso")
    head = get(f"{character}_Head")

    root = get(f"{character}_ROOT")

    for frame in range(start, end + 1, 12):

        phase = ((frame - start) // 12) % 2

        if phase == 0:

            leg_a = 25 * direction
            leg_b = -25 * direction

            arm_a = -22 * direction
            arm_b = 22 * direction

        else:

            leg_a = -25 * direction
            leg_b = 25 * direction

            arm_a = 22 * direction
            arm_b = -22 * direction

        rotation_key(
            leg_l,
            frame,
            y=leg_a
        )

        rotation_key(
            leg_r,
            frame,
            y=leg_b
        )

        rotation_key(
            shoe_l,
            frame,
            y=leg_a * 0.6
        )

        rotation_key(
            shoe_r,
            frame,
            y=leg_b * 0.6
        )

        rotation_key(
            arm_l,
            frame,
            y=arm_a
        )

        rotation_key(
            arm_r,
            frame,
            y=arm_b
        )

        rotation_key(
            hand_l,
            frame,
            y=arm_a * 0.3
        )

        rotation_key(
            hand_r,
            frame,
            y=arm_b * 0.3
        )

        rotation_key(
            torso,
            frame,
            y=3 if phase == 0 else -3
        )

        rotation_key(
            head,
            frame,
            y=-2 if phase == 0 else 2
        )

        if root:

            base_z = root.location.z

            location_key(
                root,
                frame,
                z=base_z +
                  (0.035 if phase == 0 else 0)
            )


def talk(character, start, end):

    mouth = get(
        f"{character}_Mouth"
    )

    if mouth is None:
        return

    original = mouth.scale.copy()

    for frame in range(
        start,
        end,
        8
    ):

        scale_key(
            mouth,
            frame,
            original.z * 0.35
        )

        scale_key(
            mouth,
            frame + 4,
            original.z * 1.4
        )

    mouth.scale = original

    mouth.keyframe_insert(
        data_path="scale",
        frame=end
    )


def blink(character, frame):

    for side in ["L", "R"]:

        eye = get(
            f"{character}_Eye_{side}"
        )

        if eye is None:
            continue

        original = eye.scale.copy()

        scale_key(
            eye,
            frame,
            original.z
        )

        scale_key(
            eye,
            frame + 2,
            original.z * 0.08
        )

        scale_key(
            eye,
            frame + 5,
            original.z
        )


def gesture(character, start):

    arm = get(
        f"{character}_Arm_R"
    )

    if arm is None:
        return

    rotation_key(
        arm,
        start,
        y=0
    )

    rotation_key(
        arm,
        start + 8,
        y=-35
    )

    rotation_key(
        arm,
        start + 16,
        y=30
    )

    rotation_key(
        arm,
        start + 24,
        y=-25
    )

    rotation_key(
        arm,
        start + 32,
        y=0
    )


def create_animation(story):

    # Kamal walking
    walk(
        "Kamal",
        1,
        160,
        1
    )

    # Nimal walking
    walk(
        "Nimal",
        40,
        200,
        -1
    )

    # Dialogue animation
    talk(
        "Kamal",
        30,
        80
    )

    talk(
        "Nimal",
        90,
        140
    )

    talk(
        "Kamal",
        150,
        200
    )

    # Gestures
    gesture(
        "Kamal",
        70
    )

    gesture(
        "Nimal",
        125
    )

    # Blinking
    for f in [
        35,
        95,
        155,
        205
    ]:

        blink(
            "Kamal",
            f
        )

    for f in [
        55,
        115,
        175,
        225
    ]:

        blink(
            "Nimal",
            f
        )


def main():

    if "--" not in sys.argv:

        raise RuntimeError(
            "Missing output directory."
        )

    index = sys.argv.index("--")

    story_file = Path(
        sys.argv[index + 1]
    )

    frame_directory = Path(
        sys.argv[index + 2]
    )

    story = json.loads(
        story_file.read_text(
            encoding="utf-8"
        )
    )

    frame_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "Generating:",
        story["episode"]
    )

    create_animation(
        story
    )

    scene = bpy.context.scene

    # Blender 5.0 compatible engine
    scene.render.engine = (
        "BLENDER_EEVEE"
    )

    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100

    scene.render.fps = FPS

    scene.frame_start = 1
    scene.frame_end = 240

    # PNG frames -> FFmpeg later
    scene.render.image_settings.file_format = (
        "PNG"
    )

    scene.render.filepath = str(
        frame_directory /
        "frame_"
    )

    camera = get(
        "Main_Camera"
    )

    if camera:

        scene.camera = camera

        camera.data.lens = 50

    print(
        "Rendering animation..."
    )

    bpy.ops.render.render(
        animation=True
    )

    print(
        "Rendering finished."
    )


if __name__ == "__main__":

    main()
