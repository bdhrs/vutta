"""Metre profile library.

Each profile is a list of pāda-shapes. A pāda-shape is a string of:
    '˘'  light
    '¯'  heavy
    '⏓'  light or heavy (anceps)
    '×'  any (but counted heavy by pāda-end rule)

Plus optional resolution markers. The match scorer treats ⏓ and × as wildcards
and accepts ˘˘ in place of ¯ (resolution) or vice versa (replacement) at a
configurable cost.

This stub lists the main canonical/classical metres. The Vuttodaya describes
72 of them; only the ~30 listed here account for >99% of attested verse.
"""

# fmt: off
SILOKA_PATHYA = {
    "name": "Siloka (Pathyāvatta)",
    "family": "vutta",
    "syllables_per_pada": 8,
    "padas": [
        "⏓⏓⏓⏓˘¯¯×",   # odd
        "⏓⏓⏓⏓˘¯˘×",   # even
        "⏓⏓⏓⏓˘¯¯×",
        "⏓⏓⏓⏓˘¯˘×",
    ],
}

SILOKA_NAVIPULA = {  # odd-line variation 1
    "name": "Siloka (Navipulā)",
    "family": "vutta",
    "syllables_per_pada": 8,
    "padas": ["⏓⏓⏓⏓˘˘˘×", "⏓⏓⏓⏓˘¯˘×",
              "⏓⏓⏓⏓˘¯¯×", "⏓⏓⏓⏓˘¯˘×"],
}

SILOKA_BHAVIPULA = {
    "name": "Siloka (Bhavipulā)",
    "family": "vutta",
    "syllables_per_pada": 8,
    "padas": ["⏓⏓⏓⏓¯˘˘×", "⏓⏓⏓⏓˘¯˘×",
              "⏓⏓⏓⏓˘¯¯×", "⏓⏓⏓⏓˘¯˘×"],
}

SILOKA_MAVIPULA = {
    "name": "Siloka (Mavipulā)",
    "family": "vutta",
    "syllables_per_pada": 8,
    "padas": ["⏓⏓⏓⏓¯¯¯×", "⏓⏓⏓⏓˘¯˘×",
              "⏓⏓⏓⏓˘¯¯×", "⏓⏓⏓⏓˘¯˘×"],
}

SILOKA_RAVIPULA = {
    "name": "Siloka (Ravipulā)",
    "family": "vutta",
    "syllables_per_pada": 8,
    "padas": ["⏓⏓⏓⏓¯˘¯×", "⏓⏓⏓⏓˘¯˘×",
              "⏓⏓⏓⏓˘¯¯×", "⏓⏓⏓⏓˘¯˘×"],
}

TUTTHUBHA = {
    "name": "Tuṭṭhubha",
    "family": "vutta",
    "syllables_per_pada": 11,
    "padas": ["⏓¯⏓¯⏓˘⏓¯˘¯×"] * 4,
}

JAGATI = {
    "name": "Jagatī",
    "family": "vutta",
    "syllables_per_pada": 12,
    "padas": ["⏓¯⏓¯⏓˘⏓¯˘¯˘×"] * 4,
}

INDAVAJIRA = {
    "name": "Indavajirā",
    "family": "vutta-fixed",
    "syllables_per_pada": 11,
    "padas": ["¯¯˘¯¯˘˘¯˘¯×"] * 4,
}

UPINDAVAJIRA = {
    "name": "Upindavajirā",
    "family": "vutta-fixed",
    "syllables_per_pada": 11,
    "padas": ["˘¯˘¯¯˘˘¯˘¯×"] * 4,
}

VAMSATTHA = {
    "name": "Vaṃsaṭṭhā",
    "family": "vutta-fixed",
    "syllables_per_pada": 12,
    "padas": ["˘¯˘¯¯˘˘¯˘¯˘×"] * 4,
}

RUCIRA = {
    "name": "Rucirā",
    "family": "vutta-fixed",
    "syllables_per_pada": 13,
    "padas": ["˘¯˘¯˘˘˘˘¯˘¯˘×"] * 4,
}

VASANTATILAKA = {
    "name": "Vasantatilakā",
    "family": "vutta-fixed",
    "syllables_per_pada": 14,
    "padas": ["¯¯˘¯˘˘˘¯˘˘¯˘¯×"] * 4,
}

# Measure metres: matched by mātrā count + cadence, not by syllable pattern.
# Profile is the *cadence* alone; the opening is fluid.
VETALIYA = {
    "name": "Vetālīya",
    "family": "matta",
    "matta_per_pada": [14, 16, 14, 16],
    "cadence": "¯˘¯˘×",  # last 5 syllables
}

OPACCHANDASAKA = {
    "name": "Opacchandasaka",
    "family": "matta",
    "matta_per_pada": [16, 18, 16, 18],
    "cadence": "¯˘¯˘¯×",
}

APATALIKA = {
    "name": "Āpātalikā",
    "family": "matta",
    "matta_per_pada": [14, 16, 14, 16],
    "cadence": "¯˘˘¯×",
}

# Bar metres: matched by 4-mattā gaṇa structure.
ARIYA = {
    "name": "Ariyā",
    "family": "gana",
    "matta_total": [30, 27],
}

GITI = {"name": "Gīti", "family": "gana", "matta_total": [30, 30]}
UGGITI = {"name": "Uggīti", "family": "gana", "matta_total": [27, 30]}
UPAGITI = {"name": "Upagīti", "family": "gana", "matta_total": [27, 27]}
# fmt: on

ALL_METRES = [
    SILOKA_PATHYA, SILOKA_NAVIPULA, SILOKA_BHAVIPULA,
    SILOKA_MAVIPULA, SILOKA_RAVIPULA,
    TUTTHUBHA, JAGATI,
    INDAVAJIRA, UPINDAVAJIRA, VAMSATTHA, RUCIRA, VASANTATILAKA,
    VETALIYA, OPACCHANDASAKA, APATALIKA,
    ARIYA, GITI, UGGITI, UPAGITI,
]
