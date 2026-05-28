"""Split a normalised verse into pādas while preserving internal word spacing.

Strategies, in order:
    1. Explicit PADA_BREAK ('|') markers from normalize.py.
    2. Line breaks in the input.
    3. Syllable-count fallback: if a candidate segment scans to 2N syllables
       where N ∈ {8, 11, 12, 14}, halve it at the syllable level.
    4. If we still have only 1 or 2 segments and the total scans to 4N
       syllables, split into four equal-syllable pādas.

When a syllable-level split falls inside a word, the resulting pāda loses
its internal space at the cut point (acceptable — the underlying assumption
is that compounds may span pāda boundaries).
"""

from typing import List

from .normalize import PADA_BREAK
from .syllabify import syllabify_pada


def _syl_count(text: str) -> int:
    return len(syllabify_pada(text))


def _slice_at_syllable(text: str, n: int) -> List[str]:
    """Return [head, tail] where head has n syllables (counted across spaces).

    Walks character-by-character, tracking syllable boundaries via the
    syllabifier applied to the running letter stream. Spaces are preserved.
    """
    # Build a map from character position → syllable index.
    letters = text.replace(" ", "")
    syllables = syllabify_pada(letters)
    if n >= len(syllables):
        return [text]
    # Find the character offset (in letters-only) where syllable n begins.
    cut_in_letters = sum(len(s) for s in syllables[:n])
    # Walk the original text counting non-space chars until we hit cut_in_letters.
    seen = 0
    for i, ch in enumerate(text):
        if seen == cut_in_letters:
            head = text[:i].rstrip()
            tail = text[i:].lstrip()
            return [head, tail]
        if ch != " ":
            seen += 1
    return [text]


def _split_segment(segment: str) -> List[str]:
    syl = _syl_count(segment)
    for target in (8, 11, 12, 14):
        if syl == 2 * target:
            return _slice_at_syllable(segment, target)
    return [segment]


def _split_into_four(text: str) -> List[str]:
    syl = _syl_count(text)
    for n in (8, 11, 12, 14):
        if syl == 4 * n:
            out: List[str] = []
            cur = text
            for k in range(1, 4):
                head_tail = _slice_at_syllable(cur, n)
                if len(head_tail) != 2:
                    return []
                out.append(head_tail[0])
                cur = head_tail[1]
            out.append(cur)
            return out
    return []


def split_padas(normalised: str) -> List[str]:
    if PADA_BREAK in normalised:
        segments = [p.strip() for p in normalised.split(PADA_BREAK) if p.strip()]
    elif "\n" in normalised:
        segments = [p.strip() for p in normalised.splitlines() if p.strip()]
    else:
        segments = [normalised]

    refined: List[str] = []
    for seg in segments:
        refined.extend(_split_segment(seg))

    if len(refined) in (1, 2):
        whole = _split_into_four(" ".join(refined))
        if whole:
            return whole

    return refined


if __name__ == "__main__":
    from .normalize import normalize
    s1 = "Uttamaṃ uttamaṅgena namassitvā Mahesino, Nibbānamadhudaṃ pādapaṅkajaṃ sajjanālinaṃ."
    s2 = "Bahū devā manussā ca, maṅgalāni acintayuṃ, Ākaṅkhamānā sotthānaṃ, brūhi maṅgalam-uttamaṃ."
    for s in (s1, s2):
        print(repr(split_padas(normalize(s))))
