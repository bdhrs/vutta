"""The 18 aspirated digraphs of romanised Pāḷi.

Each represents a single consonantal sound. They must NOT be treated as
conjuncts. Order matters: longer matches first.
"""

DIGRAPHS = (
    "kh", "gh", "ch", "jh", "ñh",
    "ṭh", "ḍh", "ṇh",
    "th", "dh", "nh",
    "ph", "bh", "mh",
    "lh", "ḷh", "yh", "vh",
)

VOWELS_SHORT = set("aiu")
VOWELS_VARIABLE = set("eo")  # heavy in open syllables, light in closed
VOWELS_LONG = set("āīū")
VOWELS = VOWELS_SHORT | VOWELS_VARIABLE | VOWELS_LONG

NIGGAHITA = "ṃ"
