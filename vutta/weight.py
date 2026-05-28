"""Assign ⏑ (light) or − (heavy) to each syllable.

Implements Vuttodaya v. 7's five rules:
    HEAVY if any of:
        (1) vowel is long  (ā, ī, ū)
        (2) vowel is e or o in an open syllable
        (3) vowel is followed by a conjunct consonant (closed syllable)
        (4) vowel is followed by niggahīta (ṃ)
        (5) syllable is the last of the pāda
    LIGHT otherwise.

Inputs: a list of syllable strings, as produced by syllabify_pada.
Output: a string of '⏑' / '−' characters, one per syllable.
"""

from typing import List

from ._data.digraphs import DIGRAPHS, NIGGAHITA, VOWELS_LONG, VOWELS_VARIABLE


LIGHT = "˘"
HEAVY = "¯"


def _is_closed(syl: str) -> bool:
    """True if the syllable ends in a consonant (incl. niggahīta)."""
    if not syl:
        return False
    last = syl[-1]
    # Aspirated digraph at the end?
    for d in DIGRAPHS:
        if syl.endswith(d):
            return True
    return last == NIGGAHITA or last not in VOWELS_LONG and last not in "aiueo" + "".join(VOWELS_VARIABLE)


def _vowel_of(syl: str) -> str:
    """Return the (last) vowel in the syllable, or '' if none."""
    # walk backwards skipping niggahīta and trailing consonants
    for ch in reversed(syl):
        if ch in "aiueoāīū":
            return ch
    return ""


def weigh(syllables: List[str]) -> str:
    weights = []
    for syl in syllables:
        v = _vowel_of(syl)
        closed = _is_closed(syl)
        if v in VOWELS_LONG:
            w = HEAVY
        elif v in VOWELS_VARIABLE:
            w = HEAVY      # e, o nearly always heavy; rare exceptions ignored
        elif closed:
            w = HEAVY      # short vowel in closed syllable
        else:
            w = LIGHT
        weights.append(w)
    # Rule 5: last syllable of pāda is always heavy.
    if weights:
        weights[-1] = HEAVY
    return "".join(weights)


if __name__ == "__main__":
    from .syllabify import syllabify_pada
    pada = "bahūdevāmanussāca"
    sylls = syllabify_pada(pada)
    print(sylls, "->", weigh(sylls))
