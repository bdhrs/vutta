"""Aligned monospace display, Ānandajoti-style.

Per pāda, two lines:
    line 1 — scan marks (· / −) above the first letter of each syllable
    line 2 — the verse text (original spelling, original word spacing)

The scan marks align column-for-column with the verse text. Where a
character was dropped by a prosody substitution (e.g. the medial 'i' of
'ariya' or the leading 'b' of 'brāhmaṇa'), that column is blank — visually
showing that the character does not participate in scansion.
"""

from typing import List

from .syllabify import syllabify_pada


def _syllable_start_columns_in_sub(sub_text: str) -> List[int]:
    """For each syllable in sub_text, return its start column."""
    syllables = syllabify_pada(sub_text)
    if not syllables:
        return []
    cols: List[int] = []
    syl_idx = 0
    syl_pos = 0
    cur_len = len(syllables[0])
    for i, ch in enumerate(sub_text):
        if ch == " ":
            continue
        if syl_pos == 0:
            cols.append(i)
        syl_pos += 1
        if syl_pos >= cur_len:
            syl_idx += 1
            syl_pos = 0
            if syl_idx >= len(syllables):
                break
            cur_len = len(syllables[syl_idx])
    return cols


def render_pada(orig: str, sub: str, char_map: List[int], weights: str) -> str:
    """Return two-line block: scan line + verse line.

    orig: the clean original-spelling pāda (lowercase, spaced).
    sub:  the post-substitution metrical-form pāda (same spacing).
    char_map: char_map[i] = position in sub of orig char i, or -1 if dropped.
    weights: '·' / '−' per syllable.
    """
    sub_starts = _syllable_start_columns_in_sub(sub)
    if len(sub_starts) != len(weights):
        return f"[mismatch: {len(sub_starts)} syllables vs {len(weights)} weights]\n" \
               f"{weights}\n{orig}"

    # Map from sub-column → weight.
    sub_to_weight = {col: weights[i] for i, col in enumerate(sub_starts)}

    # For each orig position, look up its sub column and check if it's a start.
    scan_chars: List[str] = []
    for i, ch in enumerate(orig):
        if ch == " ":
            scan_chars.append(" ")
            continue
        sub_pos = char_map[i] if i < len(char_map) else -1
        if sub_pos in sub_to_weight:
            scan_chars.append(sub_to_weight[sub_pos])
        else:
            scan_chars.append(" ")
    return "".join(scan_chars) + "\n" + orig


def render_verse(orig_padas: List[str], sub_padas: List[str],
                 char_maps: List[List[int]], pada_weights: List[str],
                 analysis: str = "") -> str:
    blocks = [render_pada(o, s, cm, w)
              for o, s, cm, w in zip(orig_padas, sub_padas, char_maps, pada_weights)]
    out = "\n".join(blocks)
    if analysis:
        out += "\n" + analysis
    return out
