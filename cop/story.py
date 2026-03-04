from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Story and tutorial dialogue — Pride of Code
#
# Format: (SPEAKER, text)
# Speaker names should match portrait filenames (lowercase, no spaces).
# Keep individual text blocks short so they wrap in the retro dialogue box.
# ──────────────────────────────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════════════════
# INTRO — Title screen → first practice
# ══════════════════════════════════════════════════════════════════════════════

INTRO_PAGES = [
    (
        "NARRATOR",
        "Casa Grande Union High School.\n"
        "Home of the Cougars.\n\n"
        "The Pride of Code Marching Band has always been\n"
        "fine. Respectable. Forgettable.\n\n"
        "That changes this season."
    ),
    (
        "NARRATOR",
        "You're the new Band Director.\n"
        "Hired mid-summer. No drill software experience.\n"
        "The boosters want results.\n\n"
        "Your section leaders are talented.\n"
        "Your field is waiting.\n\n"
        "State Championships are seventeen weeks away."
    ),
    (
        "NARRATOR",
        "The drill software runs on one idea:\n\n"
        "You write the instructions.\n"
        "The band follows them exactly.\n\n"
        "No guessing. No 'kinda near the hash'.\n"
        "Clean code. Clean show."
    ),
]


# ══════════════════════════════════════════════════════════════════════════════
# CHARACTER INTROS — first appearances (short, before Week 1 briefing)
# Each leader gets one intro beat so they're not strangers when their
# concept week arrives.
# ══════════════════════════════════════════════════════════════════════════════

FIRST_REHEARSAL = [
    (
        "LEAH (DRUM MAJOR)",
        "Director.\n\n"
        "I'm Leah. Drum Major. Third year.\n"
        "I run the rehearsal floor and I keep the standards.\n\n"
        "You'll learn the software. I'll keep everyone on their dots\n"
        "until you do."
    ),
    (
        "JACOB (PERCUSSION)",
        "Jacob. Battery captain.\n\n"
        "We set the tempo. The whole band breathes with us.\n"
        "If you need something to happen in exactly 8 counts,\n"
        "I'm the one who makes sure it does."
    ),
    (
        "ALEXANDER (SAX)",
        "Alexander. Winds captain — mainly sax.\n\n"
        "Lines. Spacing. Intervals.\n"
        "If there's a gap in the form that doesn't belong there,\n"
        "I'll tell you about it. Loudly."
    ),
    (
        "KYLE (HIGH BRASS)",
        "Kyle. Trumpet section.\n\n"
        "I play loud. I march fast.\n"
        "When things get complicated out there,\n"
        "I make the decision that keeps people safe."
    ),
    (
        "DOMINIC (LOW BRASS)",
        "Dominic. Low brass.\n\n"
        "We're the foundation. We set the blocks.\n"
        "You'll want us where the weight of the form has to land.\n\n"
        "We don't rush. We don't drift. We anchor."
    ),
    (
        "ANNA (FLUTE/WW)",
        "Anna. Woodwinds section.\n\n"
        "I care about phrasing. About the arc of a move.\n"
        "Getting from A to B isn't enough\n"
        "— it has to feel right getting there."
    ),
    (
        "MYLEE (COLOR GUARD)",
        "Mylee. Guard captain.\n\n"
        "We tell the story the music can't say alone.\n"
        "Give us space. Give us an arc.\n"
        "We'll make the judges feel something."
    ),
    (
        "TECH CAPTAIN",
        "Just 'Tech'. Props and staging.\n\n"
        "I make the things that break not break.\n"
        "If your code builds something beautiful,\n"
        "I build the stuff it moves around."
    ),
]


# ══════════════════════════════════════════════════════════════════════════════
# WEEK 1 — Dots & Counts (Leah + Jacob)
# Concept: variables, coordinates, step_to, wait
# ══════════════════════════════════════════════════════════════════════════════

WEEK1_BRIEFING = [
    (
        "LEAH (DRUM MAJOR)",
        "Director. Welcome to the top of the ladder.\n\n"
        "Out there, a show looks clean because everyone agrees\n"
        "on one truth: their dot.\n\n"
        "Not 'kinda near the 35'.\n"
        "Not 'about here'.\n"
        "A dot."
    ),
    (
        "LEAH (DRUM MAJOR)",
        "Code works the same way.\n\n"
        "When you name something, you pin it down.\n"
        "No guessing. No 'close enough'.\n"
        "No marching into the tuba section.\n\n"
        "x_target and y_target beat 'that spot over there'\n"
        "every single time."
    ),
    (
        "JACOB (PERCUSSION)",
        "And timing is the other half.\n\n"
        "If you tell the front ensemble\n"
        "'move sometime soon' — we revolt.\n\n"
        "Counts are the contract:\n"
        "8 means 8. Everyone lands together."
    ),
    (
        "JACOB (PERCUSSION)",
        "So this week is simple.\n\n"
        "Pick the dot.\n"
        "Set the counts.\n"
        "Move clean.\n\n"
        "Let's make the field snap to a grid."
    ),
]

WEEK1_LESSON = [
    (
        "LEAH (DRUM MAJOR)",
        "VARIABLES.\n\n"
        "A variable is a name taped to a clipboard.\n"
        "Once it's written, you stop re-explaining it\n"
        "every rep.\n\n"
        "  x_target = 20\n"
        "  y_target = 11\n\n"
        "That's a dot. Named. Pinned down."
    ),
    (
        "JACOB (PERCUSSION)",
        "COUNTS.\n\n"
        "counts=8 is an 8-count phrase.\n"
        "Not faster because you feel brave.\n"
        "Not slower because it's hot outside.\n\n"
        "When the number is right,\n"
        "the move feels right."
    ),
    (
        "LEAH (DRUM MAJOR)",
        "step_to() is your main tool this week.\n\n"
        "  band.step_to(\"DM\", x, y, counts=8)\n\n"
        "That says:\n"
        "  • move the player named 'DM'\n"
        "  • to position (x, y)\n"
        "  • taking exactly 8 counts to get there"
    ),
    (
        "JACOB (PERCUSSION)",
        "wait() is mark time.\n\n"
        "  band.wait(counts=8)\n\n"
        "Nobody moves. The music keeps going.\n"
        "The beat never stops.\n\n"
        "You'll use this to build phrase structure\n"
        "before the week is out."
    ),
]

WEEK1_DAY1_WIN  = "Leah: That's a dot. Clean and exact."
WEEK1_DAY2_WIN  = "Leah: Two moves. You're charting a show now."
WEEK1_DAY3_WIN  = "Jacob: 8 then 4. Same distance. Different energy. Feel that?"
WEEK1_DAY4_WIN  = "Leah: Move, hold, move. That's a phrase. Lock it in."

WEEK1_BATTLE_PRE = [
    (
        "LEAH (DRUM MAJOR)",
        "Copper Ridge is up first.\n\n"
        "They call themselves 'The Beginners' like it's a brand.\n"
        "They're clean, they're cautious,\n"
        "and they've never lost a Week 1 battle.\n\n"
        "Until now, I guess."
    ),
    (
        "JACOB (PERCUSSION)",
        "Two moves. Sixteen counts. End at (20, 11).\n\n"
        "The 50-yard line.\n"
        "Center of the field.\n"
        "That's the power position in any show.\n\n"
        "Hit it clean and the judges will remember it."
    ),
]

WEEK1_BATTLE_WIN = [
    (
        "LEAH (DRUM MAJOR)",
        "There it is.\n\n"
        "Two moves. Sixteen counts. Center of the field.\n\n"
        "Copper Ridge scored 71.\n"
        "You scored higher.\n\n"
        "Week 1 is ours."
    ),
    (
        "JACOB (PERCUSSION)",
        "I want to point something out:\n"
        "your code was readable.\n\n"
        "Clean variable names.\n"
        "Counts that matched the music.\n\n"
        "That's going to matter\n"
        "when the shows get complicated."
    ),
]

WEEK1_BATTLE_LOSS = [
    (
        "LEAH (DRUM MAJOR)",
        "We lost. That's fine.\n\n"
        "More important: look at the judge sheets.\n"
        "Find the line that costs you the most points.\n"
        "Fix that line.\n\n"
        "That's rehearsal."
    ),
]


# ══════════════════════════════════════════════════════════════════════════════
# WEEK 2 — Clean Lines (Alexander)
# Concept: loops (for), spacing math
# ══════════════════════════════════════════════════════════════════════════════

WEEK2_BRIEFING = [
    (
        "ALEXANDER (SAX)",
        "Director. Sax section reporting.\n\n"
        "We're the shiny glue between rhythm and melody.\n"
        "If we're together, the whole show feels smooth.\n"
        "If we're not — everyone can hear it."
    ),
    (
        "ALEXANDER (SAX)",
        "In jazz, an interval is the space between notes.\n"
        "On the field, it's the space between marchers.\n\n"
        "Bad spacing looks like bad intonation:\n"
        "instantly obvious. Immediately embarrassing."
    ),
    (
        "ALEXANDER (SAX)",
        "We're building a clean sax line this week.\n\n"
        "Five winds. Same row. Same gap.\n"
        "Every marcher placed with a formula,\n"
        "not by hand.\n\n"
        "That's what a loop does."
    ),
]

WEEK2_LESSON = [
    (
        "ALEXANDER (SAX)",
        "LOOPS.\n\n"
        "A loop is a chorus you play again.\n\n"
        "  for i in range(5):\n"
        "      ...\n\n"
        "That block runs 5 times.\n"
        "i starts at 0, ends at 4."
    ),
    (
        "ALEXANDER (SAX)",
        "SPACING MATH.\n\n"
        "  x = x0 + i * spacing\n\n"
        "Start at x0.\n"
        "Add a gap each time i increases.\n\n"
        "That's your groove grid.\n"
        "Even spacing. Every time."
    ),
    (
        "ALEXANDER (SAX)",
        "Naming each player:\n\n"
        "  name = f\"W{i+1}\"\n\n"
        "That makes: W1, W2, W3, W4, W5.\n\n"
        "Now your loop can spawn each one\n"
        "and the code can find them later."
    ),
    (
        "ALEXANDER (SAX)",
        "Your task:\n\n"
        "Spawn 5 wind players on y=11,\n"
        "starting at x=14, with spacing=2.\n\n"
        "Same gap. Same feel.\n"
        "Clean line."
    ),
]


# ══════════════════════════════════════════════════════════════════════════════
# RIVAL — Director Voss (Obsidian Regiment)
# Appears at specific story beats — not full briefings, just sharp moments.
# ══════════════════════════════════════════════════════════════════════════════

VOSS_WEEK1_SIGHTING = (
    "DIRECTOR VOSS",
    "Interesting first invitational.\n\n"
    "A little rough around the edges, but…\n"
    "potential, maybe.\n\n"
    "I'm sure we'll see each other at State."
)

VOSS_WEEK8_MIDSEASON = (
    "DIRECTOR VOSS",
    "You've been improving.\n\n"
    "I noticed the spacing work at Regionals.\n"
    "Very… adequate.\n\n"
    "I do hope you're not peaking early."
)

VOSS_WEEK13_WAVE = (
    "DIRECTOR VOSS",
    "...\n\n"
    "[He watches your wave drill from the press box.\n"
    " Slow clap. Twice. Then nothing.]\n\n"
    "That's worse than trash talk."
)

VOSS_WEEK16_SEMI = (
    "DIRECTOR VOSS",
    "See you at State, Director.\n\n"
    "I mean that literally.\n"
    "We'll both be there.\n\n"
    "The question is where\n"
    "you'll be standing when the scores post."
)

VOSS_WEEK17_FINAL = (
    "DIRECTOR VOSS",
    "That…\n\n"
    "…was a real show.\n\n"
    "I mean it.\n\n"
    "[He pauses. Then reaches out to shake your hand.]\n\n"
    "Trade drill notes sometime?"
)