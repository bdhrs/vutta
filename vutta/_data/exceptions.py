"""Conjuncts that systematically fail to make position.

Per Ānandajoti, Outline §1.5. These conjuncts at the start of specific words
do NOT lengthen the preceding syllable.
"""

NON_POSITION_CONJUNCTS = {
    "br": ("brāhmaṇ", "brahma", "brūti", "brūhi", "anubrūhaye"),
    "by": (),       # often fails throughout
    "vy": (),       # often fails throughout
    "tv": ("tvaṃ",),
    "dv": ("dvāra",),
    "nh": ("nhātaka",),
}

# Words that scan as fewer syllables than they look — sarabhatti (svarabhakti).
# Format: written form -> (light/heavy weights, syllable count)
# Loaded as a tsv at runtime; this stub shows the shape.
SARABHATTI_HINT = (
    "ariya",     # scan ·· not ···
    "iriya",
    "cariya",
    "viriya",
    "araha",
    "kayira",
)
