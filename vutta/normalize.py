"""Clean raw verse text into a flat lowercase string with pāda markers.

Two layers:

  1. `clean(text)` — lowercase, NFC, strip non-Pāḷi characters, collapse
     punctuation to PADA_BREAK, preserve word spacing. This is the
     "display form" — what we want to show in the verse line.

  2. `metrical(clean_text)` — apply prosody-aware substitutions
     (sarabhatti + br/dv/tv non-position) and return both the substituted
     text and a position map: char_map[i] = index of original char i in
     the substituted text, or -1 if that char was dropped.

`normalize(text)` keeps the legacy single-string API (returns metrical
form only). Callers that need alignment use `clean()` + `metrical()`.
"""

import re
import unicodedata
from typing import List, Tuple


PADA_BREAK = "|"
PAUSES = ",;.|"


_SARABHATTI = [
    ("ariya", "arya"),
    ("iriya", "irya"),
    ("cariya", "carya"),
    ("viriya", "virya"),
    ("araha", "arha"),
    ("kayira", "kayra"),
]


_NON_POSITION = [
    ("brāhmaṇ", "rāhmaṇ"),
    ("brahma", "rahma"),
    ("brūti", "rūti"),
    ("brūhi", "rūhi"),
    ("anubrūhaye", "anurūhaye"),
    ("tvaṃ", "vaṃ"),
    ("dvāra", "vāra"),
    ("nhātaka", "hātaka"),
]


def clean(text: str) -> str:
    """Step 1: lowercase, strip non-Pāḷi punctuation, mark pāda breaks.

    No prosody substitutions are performed; the result preserves the
    original orthography of every Pāḷi letter.
    """
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    text = text.replace("ṁ", "ṃ")
    text = re.sub(r"\([^)]*\)", " ", text)
    for ch in "‘’“”'\"-–—*":
        text = text.replace(ch, " ")
    for ch in PAUSES:
        text = text.replace(ch, PADA_BREAK)
    keep = re.compile(r"[a-zāīūṁṃṅñṭḍṇḷ\s" + re.escape(PADA_BREAK) + "]")
    text = "".join(ch for ch in text if keep.match(ch))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def metrical(text: str) -> Tuple[str, List[int]]:
    """Apply sarabhatti and br-exception substitutions on a cleaned string.

    Returns (substituted, orig_to_sub) where orig_to_sub[i] is the index
    in the substituted string of original char i, or -1 if dropped.

    Non-position substitutions are applied only when the prefix occurs
    at a word boundary. Sarabhatti substitutions may occur anywhere.
    """
    out: List[str] = []
    char_map: List[int] = [-1] * len(text)
    i = 0
    while i < len(text):
        at_word_start = (i == 0) or (text[i - 1] == " ")

        # Word-initial non-position prefix?
        emitted = False
        if at_word_start:
            for orig, sub in _NON_POSITION:
                if text[i : i + len(orig)] == orig:
                    drop = len(orig) - len(sub)
                    # First `drop` chars of orig are dropped (the leading 'b' etc.)
                    for k in range(drop):
                        char_map[i + k] = -1
                    for k in range(drop, len(orig)):
                        char_map[i + k] = len(out)
                        out.append(text[i + k])
                    i += len(orig)
                    emitted = True
                    break
        if emitted:
            continue

        # Sarabhatti anywhere in a word?
        for orig, sub in _SARABHATTI:
            if text[i : i + len(orig)] == orig:
                # Walk both strings; chars present in both get mapped, chars
                # only in orig get -1.
                oi = 0
                si = 0
                while oi < len(orig) and si < len(sub):
                    if orig[oi] == sub[si]:
                        char_map[i + oi] = len(out)
                        out.append(orig[oi])
                        oi += 1
                        si += 1
                    else:
                        char_map[i + oi] = -1
                        oi += 1
                while oi < len(orig):
                    char_map[i + oi] = -1
                    oi += 1
                i += len(orig)
                emitted = True
                break
        if emitted:
            continue

        # Default: copy character.
        char_map[i] = len(out)
        out.append(text[i])
        i += 1

    return "".join(out), char_map


def normalize(text: str) -> str:
    """Legacy single-string API: returns the substituted (metrical) form."""
    cleaned = clean(text)
    sub, _ = metrical(cleaned)
    return sub


if __name__ == "__main__":
    for s in [
        "Tapo ca brahmacariyañ-ca, ariyasaccāna' dassanaṃ,",
        "Bahū devā manussā ca, maṅgalāni acintayuṃ, brūhi maṅgalam-uttamaṃ.",
    ]:
        c = clean(s)
        sub, m = metrical(c)
        print("orig :", c)
        print("sub  :", sub)
        print("map  :", m)
        print()
