"""Split a normalised pāda into syllables.

Algorithm:
    1. Tokenise the string into atoms: each atom is one of
         - a vowel (a i u e o ā ī ū)
         - the niggahīta ṃ
         - a single consonant (with aspirated digraphs treated as one atom)
    2. Find the vowel positions in the atom list.
    3. For each vowel v_i, its syllable contains:
         - any onset consonants assigned to it from the cluster before v_i
         - the vowel v_i itself
         - a trailing niggahīta, if any
    4. Between vowel v_i and v_{i+1} there are k consonant atoms:
         - k == 0 : v_i open, v_{i+1} has no onset
         - k == 1 : that consonant is the onset of syllable i+1
         - k >= 2 : the FIRST consonant closes syllable i (coda),
                    the rest become the onset of syllable i+1
    5. Leading consonants before the first vowel become the onset of
       syllable 0.
    6. Trailing consonants after the last vowel attach to the last syllable.

Returns a list of syllable strings.
"""

from typing import List

from ._data.digraphs import DIGRAPHS, NIGGAHITA, VOWELS


def _tokenize(s: str) -> List[str]:
    out = []
    i = 0
    while i < len(s):
        matched_digraph = None
        for d in DIGRAPHS:
            if s.startswith(d, i):
                matched_digraph = d
                break
        if matched_digraph:
            out.append(matched_digraph)
            i += len(matched_digraph)
        else:
            out.append(s[i])
            i += 1
    return out


def syllabify_pada(pada: str) -> List[str]:
    s = pada.replace(" ", "")
    if not s:
        return []
    atoms = _tokenize(s)

    # Indices of vowel atoms.
    vowel_idx = [i for i, a in enumerate(atoms) if a in VOWELS]
    if not vowel_idx:
        return []

    syllables: List[str] = []
    for k, v_pos in enumerate(vowel_idx):
        # Determine the range of atoms belonging to this syllable.
        # Onset: consonants between previous-coda-boundary and v_pos.
        prev_v = vowel_idx[k - 1] if k > 0 else -1
        # Consonants strictly between prev_v and v_pos (excluding any
        # niggahīta directly after prev_v, which belongs to prev syllable).
        start = prev_v + 1
        # Skip a niggahīta right after the previous vowel — it belongs to
        # that syllable, not this one. (Already handled below.)
        if start < len(atoms) and atoms[start] == NIGGAHITA:
            start += 1
        cluster = atoms[start:v_pos]
        n = len(cluster)
        if k == 0:
            # All leading consonants belong to syllable 0.
            onset_atoms = cluster
        elif n <= 1:
            onset_atoms = cluster
        else:
            # First consonant became coda of previous syllable; rest = onset here.
            onset_atoms = cluster[1:]
            # Splice the coda onto the previous syllable (already appended).
            syllables[-1] += cluster[0]

        syl = "".join(onset_atoms) + atoms[v_pos]
        # Niggahīta directly after this vowel?
        if v_pos + 1 < len(atoms) and atoms[v_pos + 1] == NIGGAHITA:
            syl += NIGGAHITA
        syllables.append(syl)

    # Trailing consonants after the last vowel (and any niggahīta past it):
    last_v = vowel_idx[-1]
    tail_start = last_v + 1
    if tail_start < len(atoms) and atoms[tail_start] == NIGGAHITA:
        tail_start += 1  # already attached above
    tail = atoms[tail_start:]
    if tail:
        syllables[-1] += "".join(tail)

    return syllables


if __name__ == "__main__":
    for word in ["bahū", "devā", "manussāca", "maṅgalāni", "acintayuṃ",
                 "ākaṅkhamānā", "sotthānaṃ", "brūhi", "uttamaṃ", "dhammaṃ",
                 "bahūdevāmanussāca"]:
        print(word, "->", syllabify_pada(word))
