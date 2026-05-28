"""Match a scanned verse against the metre profile library.

Three family-level detectors + one fixed-profile fallback:

A) Siloka detector – accepts any even-count of 8-or-9-or-10-syllable pādas,
   with resolution collapsing extra syllables, identifies per-odd-pāda vipulā.
B) Tuṭṭhubha / Jagatī detector – by terminal cadence and 10–13 syllable count.
C) Mātrā-metre detector – Vetālīya, Opacchandasaka, Āpātalikā by total mātrā.
D) Fixed-profile scorer for Indavajirā, Vasantatilakā, etc.

Returns up to 3 (name, cost) tuples; lowest cost first. Cost 0 = exact match.
"""

from typing import List, Tuple, Optional

from ._data.metres import ALL_METRES
from .weight import LIGHT, HEAVY


_VIPULA_BY_CADENCE = {
    LIGHT + HEAVY + HEAVY: "pathyā",
    LIGHT + LIGHT + LIGHT: "navipulā",
    HEAVY + LIGHT + LIGHT: "bhavipulā",
    HEAVY + HEAVY + HEAVY: "mavipulā",
    HEAVY + LIGHT + HEAVY: "ravipulā",
    LIGHT + LIGHT + HEAVY: "savipulā",
    HEAVY + HEAVY + LIGHT: "tavipulā",
    LIGHT + HEAVY + LIGHT: "javipulā",
}
_SILOKA_EVEN_CADENCE = LIGHT + HEAVY + LIGHT
_PATHYĀ_CADENCE = LIGHT + HEAVY + HEAVY


# --------------------------------------------------------------------------- A
def _try_resolve_with_cadence(p: str, target_len: int, even_pāda: bool) -> Optional[str]:
    """Collapse ··→– pairs in p until len == target_len AND cadence is valid."""
    if len(p) == target_len:
        return p
    if len(p) < target_len:
        return None
    valid_odd = set(_VIPULA_BY_CADENCE.keys())
    valid_even = {_SILOKA_EVEN_CADENCE}
    queue = [p]
    seen = {p}
    best: Optional[str] = None
    while queue:
        cur = queue.pop(0)
        if len(cur) == target_len:
            cad = cur[4:7]
            ok = cad in (valid_even if even_pāda else valid_odd)
            if ok:
                if even_pāda and cad == _SILOKA_EVEN_CADENCE:
                    return cur
                if not even_pāda and cad == _PATHYĀ_CADENCE:
                    return cur
                if best is None:
                    best = cur
            continue
        if len(cur) < target_len:
            continue
        for i in range(len(cur) - 1):
            if cur[i] == LIGHT and cur[i + 1] == LIGHT:
                new = cur[:i] + HEAVY + cur[i + 2:]
                if new not in seen:
                    seen.add(new)
                    queue.append(new)
    return best


def _detect_siloka(weights: List[str]) -> Optional[Tuple[str, float]]:
    n = len(weights)
    if n < 2 or n % 2 != 0:
        return None
    normalised = []
    res_count = 0
    for idx, p in enumerate(weights):
        if len(p) == 8:
            normalised.append(p)
        elif 9 <= len(p) <= 10:
            even = (idx % 2 == 1)
            r = _try_resolve_with_cadence(p, 8, even)
            if r is None:
                return None
            normalised.append(r)
            res_count += len(p) - 8
        else:
            return None
    if not all(len(p) == 8 for p in normalised):
        return None

    cost = 0.0
    odd_tags = []
    for i, p in enumerate(normalised):
        cadence = p[4:7]
        if i % 2 == 1:
            if cadence != _SILOKA_EVEN_CADENCE:
                diff = sum(1 for a, b in zip(cadence, _SILOKA_EVEN_CADENCE) if a != b)
                cost += 2.0 * diff
        else:
            tag = _VIPULA_BY_CADENCE.get(cadence, f"?({cadence})")
            odd_tags.append(tag)
    if cost > 4.0:
        return None
    cost += 0.25 * res_count
    if all(t == "pathyā" for t in odd_tags):
        return ("Siloka (Pathyāvatta)", cost)
    if all(t.startswith("?") for t in odd_tags):
        return None
    return ("Siloka [" + " / ".join(odd_tags) + "]", cost)


# --------------------------------------------------------------------------- B
def _detect_tutthubha(weights: List[str]) -> Optional[Tuple[str, float]]:
    """Tuṭṭhubha (11 syll, cadence –·–×); Jagatī (12 syll, cadence –·–·×);
    or mixed Tuṭṭhubha/Jagatī (Upajāti-style). Allow ±1 syllable per pāda.
    """
    n = len(weights)
    if n < 2 or n % 2 != 0:
        return None
    lens = [len(p) for p in weights]
    if not all(10 <= L <= 13 for L in lens):
        return None
    cad_t = HEAVY + LIGHT + HEAVY        # –·–
    cad_j = HEAVY + LIGHT + HEAVY + LIGHT  # –·–·
    tags = []
    cost = 0.0
    for p, L in zip(weights, lens):
        if p[-5:-1] == cad_j:
            tags.append("J")
            if L != 12:
                cost += 0.5
        elif p[-4:-1] == cad_t:
            tags.append("T")
            if L != 11:
                cost += 0.5
        else:
            return None
    if all(t == "T" for t in tags):
        return ("Tuṭṭhubha", cost)
    if all(t == "J" for t in tags):
        return ("Jagatī", cost)
    return ("Tuṭṭhubha/Jagatī mix", cost)


# --------------------------------------------------------------------------- C
def _matta_count(p: str) -> int:
    return sum(2 if w == HEAVY else 1 for w in p)


def _detect_matta(weights: List[str]) -> Optional[Tuple[str, float]]:
    n = len(weights)
    if n < 2 or n % 2 != 0:
        return None
    mattas = [_matta_count(p) for p in weights]

    cad_op = HEAVY + LIGHT + HEAVY + LIGHT + HEAVY       # –·–·–
    cad_ve = HEAVY + LIGHT + HEAVY + LIGHT               # –·–·
    cad_ap = HEAVY + LIGHT + LIGHT + HEAVY               # –··–

    expected_op = [16, 18] * (n // 2)
    if mattas == expected_op and all(p[-6:-1] == cad_op for p in weights):
        return ("Opacchandasaka", 0.0)
    if all(abs(m - e) <= 1 for m, e in zip(mattas, expected_op)) and \
       all(p[-6:-1] == cad_op for p in weights):
        return ("Opacchandasaka", 1.0)

    expected_ve = [14, 16] * (n // 2)
    if mattas == expected_ve and all(p[-5:-1] == cad_ve for p in weights):
        return ("Vetālīya", 0.0)
    if all(abs(m - e) <= 1 for m, e in zip(mattas, expected_ve)) and \
       all(p[-5:-1] == cad_ve for p in weights):
        return ("Vetālīya", 1.0)

    if mattas == expected_ve and all(p[-5:-1] == cad_ap for p in weights):
        return ("Āpātalikā", 0.0)
    if all(abs(m - e) <= 1 for m, e in zip(mattas, expected_ve)) and \
       all(p[-5:-1] == cad_ap for p in weights):
        return ("Āpātalikā", 1.0)
    return None


# --------------------------------------------------------------------------- D
def _score_pada(observed: str, profile: str) -> float:
    if len(observed) != len(profile):
        return 10.0
    cost = 0.0
    for o, p in zip(observed, profile):
        if p in "⏓×":
            continue
        if o == p:
            continue
        cost += 1.0
    return cost


def _score_fixed(weights: List[str]) -> List[Tuple[str, float]]:
    out = []
    for metre in ALL_METRES:
        if metre["family"] != "vutta-fixed":
            continue
        profile = metre["padas"]
        if len(weights) != len(profile):
            continue
        cost = sum(_score_pada(o, p) for o, p in zip(weights, profile))
        out.append((metre["name"], cost))
    out.sort(key=lambda x: x[1])
    return out


def match(weights: List[str]) -> List[Tuple[str, float]]:
    candidates: List[Tuple[str, float]] = []
    for fn in (_detect_siloka, _detect_tutthubha, _detect_matta):
        c = fn(weights)
        if c is not None:
            candidates.append(c)
    fixed = _score_fixed(weights)
    fixed = [(n, c) for n, c in fixed if c < 10.0]
    candidates.extend(fixed)
    candidates.sort(key=lambda x: x[1])
    return candidates[:3]
