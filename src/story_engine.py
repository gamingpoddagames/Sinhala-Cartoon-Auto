import random

CHARACTERS = ["Kamal", "Nimal"]

LOCATIONS = [
    "village",
    "road",
    "market",
    "park",
    "house",
    "tree"
]

ACTIONS = [
    "walk",
    "talk",
    "gesture",
    "surprised",
    "wave",
    "run"
]

OPENINGS = [
    "අද මොකද කරන්නෙ?",
    "නිමල්, ඔයා කොහෙද යන්නේ?",
    "කමල්, ඉක්මනට එන්න!",
    "අද නම් හොඳ දවසක් වගේ.",
    "මේක නම් පුදුම වැඩක්!",
]

MIDDLE = [
    "අපි ටිකක් ඉස්සරහට යමු.",
    "එහෙනම් අපි එකට බලමු.",
    "ඒක ඇත්තද?",
    "මට නම් ඒක විශ්වාස කරන්න බෑ.",
    "හරි, අපි යමු.",
]

ENDINGS = [
    "හරි, එහෙනම් යමු!",
    "අද නම් හොඳ විනෝදයක්.",
    "ඊළඟට මොකද කරන්නේ?",
    "අපි ආයෙත් මෙතනට එමු.",
    "හරි, කතාව ඉවරයි!",
]


def make_story(number):

    random.seed(number * 17391)

    location = random.choice(LOCATIONS)
    action = random.choice(ACTIONS)

    opening = random.choice(OPENINGS)
    middle = random.choice(MIDDLE)
    ending = random.choice(ENDINGS)

    if random.choice([True, False]):

        dialogue = [
            {
                "speaker": "Kamal",
                "text": opening
            },
            {
                "speaker": "Nimal",
                "text": middle
            },
            {
                "speaker": "Kamal",
                "text": ending
            }
        ]

    else:

        dialogue = [
            {
                "speaker": "Nimal",
                "text": opening
            },
            {
                "speaker": "Kamal",
                "text": middle
            },
            {
                "speaker": "Nimal",
                "text": ending
            }
        ]

    return {
        "episode": number,
        "location": location,
        "action": action,
        "dialogue": dialogue
    }
