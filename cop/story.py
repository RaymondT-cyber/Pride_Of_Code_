from __future__ import annotations

# Story and tutorial dialogue.
# IMPORTANT: All coding instructions are delivered by section leaders.
# Keep lines short so they wrap cleanly in retro UI.

INTRO_PAGES = [
    (
        "NARRATOR",
        "Hey! Welcome.\n\n"
        "You’re the new Band Director of the Pride of Code Marching Band.\n"
        "Time to make this band the greatest.\n\n"
        "Listen to your team, work together, and build the greatest show ever."
    ),
]

# Week 1: Variables + counts + step_to (DM move)
WEEK1_BRIEFING = [
    (
        "LEAH (DRUM MAJOR)",
        "Director, keeping the band together starts with clarity.\n\n"
        "On the field we use DOTS: everyone has a precise spot.\n"
        "In code, we do the same thing by naming the spot."
    ),
    (
        "JACOB (PERCUSSION)",
        "And we move on COUNTS.\n\n"
        "Think of counts like a cadence: everyone locks in together.\n"
        "In code, counts are a number we pass into the move."
    ),
]

WEEK1_LESSON = [
    (
        "LEAH (DRUM MAJOR)",
        "Lesson: VARIABLES.\n\n"
        "A variable is like writing a dot on a card.\n"
        "Instead of shouting the coordinates every time,\n"
        "you store them once and reuse them."
    ),
    (
        "JACOB (PERCUSSION)",
        "Lesson: COUNTS.\n\n"
        "counts=8 means an 8-count phrase.\n"
        "If the band moves in 8, the band arrives in 8.\n"
        "No drifting, no guessing."
    ),
    (
        "LEAH + JACOB",
        "Your task: Move the Drum Major (DM) to the target dot\n"
        "in exactly 8 counts.\n\n"
        "You’ll get the structure.\n"
        "You must set the right numbers and make it work."
    ),
]
# Week 2: Loops + intervals (clean sax line)
WEEK2_BRIEFING = [
    (
        "ALEXANDER (SAX)",
        "Director. Sax section reportin’.\n\n"
        "We’re the shiny glue between rhythm and melody.\n"
        "If we’re together, the whole show feels smooth."
    ),
    (
        "ALEXANDER (SAX)",
        "In jazz, an INTERVAL is the space between notes.\n"
        "On the field, it’s the space between marchers.\n\n"
        "Bad spacing looks like bad intonation: instantly obvious."
    ),
    (
        "ALEXANDER (SAX)",
        "We’re building a clean sax line today.\n\n"
        "Five winds. Same row. Same gap.\n"
        "A tight horn section, but… with sneakers."
    ),
]

WEEK2_LESSON = [
    (
        "ALEXANDER (SAX)",
        "Lesson: LOOPS.\n\n"
        "A loop is a chorus you play again.\n"
        "for i in range(5): means 5 repeats."
    ),
    (
        "ALEXANDER (SAX)",
        "Lesson: PATTERNS.\n\n"
        "Start at x0. Add spacing each time.\n"
        "x = x0 + i * spacing\n\n"
        "That’s your groove grid."
    ),
    (
        "ALEXANDER (SAX)",
        "Naming matters.\n\n"
        "name = f\"W{i+1}\" makes W1, W2, W3…\n"
        "So your code can talk to each player."
    ),
    (
        "ALEXANDER (SAX)",
        "Your task: Spawn 5 winds on y=11\n"
        "starting at x=14, with spacing=2.\n\n"
        "Same gap. Same feel. Clean line."
    ),
]

# Week 1 Battle: Copper Ridge HS
WEEK1_BATTLE_PRE = [
    (
        "LEAH (DRUM MAJOR)",
        "Director, our first invitational is today.\n"
        "Copper Ridge HS goes on right before us.\n"
        "They’re called ‘The Beginners’.",
    ),
    (
        "DIRECTOR VOSS",
        "Ah, Casa Grande. I’m Director Voss of the Obsidian Regiment.\n"
        "Just wanted to wish you luck. Copper Ridge is... well, they try.\n"
        "Let’s see if your kids can at least hit their dots on time.",
    ),
    (
        "JACOB (PERCUSSION)",
        "Ignore him.\n\n"
        "Goal: a clean 16-count phrase.\n"
        "Two distinct moves. Exact timing.\n"
        "No overshoot.",
    ),
]

WEEK1_BATTLE_POST_WIN = [
    (
        "LEAH (DRUM MAJOR)",
        "Forms held. Timing locked.\n"
        "Copper Ridge didn’t stand a chance.",
    ),
    (
        "DIRECTOR VOSS",
        "Beginner’s luck.\n"
        "Enjoy the minor leagues, Director.\n"
        "I’ll be watching.",
    ),
]

WEEK1_BATTLE_POST_LOSS = [
    (
        "JACOB (PERCUSSION)",
        "We drifted. The phrase fell apart.\n\n"
        "Check the Judge’s sheet, clean the code, and rep it again.",
    )
]
