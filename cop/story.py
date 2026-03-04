from __future__ import annotations

# Story and tutorial dialogue.
# Keep lines short so they wrap cleanly in the retro UI.

INTRO_PAGES = [
    (
        "NARRATOR",
        "Hey! Welcome.\n\n"
        "You’re the new Band Director of the Pride of Code Marching Band.\n"
        "Your job is half music, half logistics… and 100% vibes.\n\n"
        "Listen to your section leaders, write clean instructions,\n"
        "and build a show that looks sharp from the cheap seats."
    ),
]

# Week 1: Variables + counts + step_to (DM move)
WEEK1_BRIEFING = [
    (
        "LEAH (DRUM MAJOR)",
        "Director. Welcome to the top of the ladder. 🙂\n\n"
        "Out there, a shape looks clean because everyone agrees on one truth: their dot.\n"
        "Not ‘kinda near the 35’. Not ‘about here’. A dot."
    ),
    (
        "LEAH (DRUM MAJOR)",
        "Code works the same way.\n\n"
        "When you name something, you pin it down.\n"
        "No guessing, no ‘close enough’, no marching into traffic cones."
    ),
    (
        "JACOB (PERCUSSION)",
        "And timing is the other half.\n\n"
        "If you tell the front ensemble ‘move sometime soon’, we revolt.\n"
        "Counts are the contract: 8 means 8. Everyone lands together."
    ),
    (
        "JACOB (PERCUSSION)",
        "So today is simple:\n"
        "Pick the dot. Set the counts. Move clean.\n\n"
        "Let’s make the field look like it’s snapping to a grid."
    ),
]

WEEK1_LESSON = [
    (
        "LEAH (DRUM MAJOR)",
        "Lesson: VARIABLES.\n\n"
        "A variable is a name taped to a clipboard.\n"
        "Once it’s written down, you stop re-explaining it every rep.\n\n"
        "x_target and y_target beat ‘that spot over there’ every time."
    ),
    (
        "JACOB (PERCUSSION)",
        "Lesson: COUNTS.\n\n"
        "counts = 8 is an 8-count phrase.\n"
        "Not faster because you feel brave. Not slower because it’s hot.\n\n"
        "When the number is right, the move feels right."
    ),
    (
        "LEAH + JACOB",
        "Your task:\n"
        "Move the Drum Major (DM) to the target dot\n"
        "in exactly 8 counts.\n\n"
        "You’ll get a starter script.\n"
        "You set the numbers and make the move land."
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
