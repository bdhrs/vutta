"""CLI entry point.

Usage:
    uv run -m vutta.scan "Bahū devā manussā ca, maṅgalāni acintayuṃ, ..."
    echo "<verse>" | uv run -m vutta.scan -
"""

import sys

from .normalize import clean, metrical, PADA_BREAK
from .pada_split import split_padas
from .syllabify import syllabify_pada
from .weight import weigh
from .match import match
from .display import render_verse


def _slice_map(char_map, start, end):
    """Slice an orig-to-sub map for orig[start:end].

    The returned map gives sub positions relative to that orig slice's sub form.
    """
    # We want to renumber: find the min non-negative sub position in this range.
    sub_positions = [p for p in char_map[start:end] if p >= 0]
    if not sub_positions:
        return [-1] * (end - start)
    base = min(sub_positions)
    return [(p - base) if p >= 0 else -1 for p in char_map[start:end]]


def scan(text: str) -> str:
    cleaned = clean(text)
    sub_full, char_map_full = metrical(cleaned)

    # Split into pādas — operates on cleaned (display) form.
    orig_padas = split_padas(cleaned)

    # For each orig pāda, locate it in `cleaned` and slice the char_map.
    sub_padas = []
    pada_maps = []
    cursor = 0
    for op in orig_padas:
        # Find this pāda in cleaned starting at cursor.
        idx = cleaned.find(op, cursor)
        if idx < 0:
            # Fallback: not found; assume identity (no substitutions in this pāda)
            sub_padas.append(op)
            pada_maps.append(list(range(len(op))))
            continue
        start = idx
        end = idx + len(op)
        cursor = end
        # Build sub_pāda from char_map_full
        sub_chars = []
        local_map = []
        for i in range(start, end):
            sp = char_map_full[i]
            if sp >= 0:
                local_map.append(len(sub_chars))
                sub_chars.append(sub_full[sp])
            else:
                local_map.append(-1)
        sub_padas.append("".join(sub_chars))
        pada_maps.append(local_map)

    # Syllabify + weigh on the substituted form (the metrical truth).
    weights_per_pada = [weigh(syllabify_pada(s)) for s in sub_padas]
    top = match(weights_per_pada)
    if top and top[0][1] == 0:
        analysis = f"metre: {top[0][0]}"
    elif top:
        name, cost = top[0]
        analysis = f"metre: {name} (cost {cost})"
    else:
        analysis = "metre: unmatched"

    return render_verse(orig_padas, sub_padas, pada_maps, weights_per_pada, analysis)


def main():
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read()
    print(scan(text))


if __name__ == "__main__":
    main()
