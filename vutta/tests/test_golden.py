"""Golden-case tests. Run with:  uv run -m vutta.tests.test_golden"""

from vutta.normalize import clean, metrical
from vutta.pada_split import split_padas
from vutta.syllabify import syllabify_pada
from vutta.weight import weigh
from vutta.match import match


CASES = [
    (
        "Maṅgalasutta v.1 (mixed Siloka – pāda 3 mavipulā)",
        "Bahū devā manussā ca, maṅgalāni acintayuṃ, "
        "Ākaṅkhamānā sotthānaṃ, brūhi maṅgalam-uttamaṃ.",
        ["·–––·–––", "–·–··–·–", "––·–––––", "–·–··–·–"],
        "Siloka [pathyā / mavipulā]",
    ),
    (
        "Jinacarita v.1 (Pathyāvatta)",
        "Uttamaṃ uttamaṅgena namassitvā Mahesino, "
        "Nibbānamadhudaṃ pādapaṅkajaṃ sajjanālinaṃ.",
        ["–·––·–––", "·–––·–·–", "––···–––", "–·––·–·–"],
        "Siloka (Pathyāvatta)",
    ),
    (
        "Dhammapada 183 line d",
        "Etaṃ Buddhāna' sāsanaṃ",
        ["––––·–·–"],
        None,
    ),
]


def report():
    for label, raw, expected_weights, expected_metre in CASES:
        print(f"\n=== {label} ===")
        cleaned = clean(raw)
        padas = split_padas(cleaned)
        ws = []
        for i, p in enumerate(padas):
            sub_p, _ = metrical(p)
            sylls = syllabify_pada(sub_p)
            w = weigh(sylls)
            ws.append(w)
            exp = expected_weights[i] if i < len(expected_weights) else "?"
            ok = "✓" if w == exp else "✗"
            print(f"  pāda {i+1}: {ok}  got: {w}  expected: {exp}")
        if expected_metre:
            top = match(ws)
            ok = "✓" if top and top[0][0] == expected_metre else "✗"
            print(f"  metre {ok}: {top}")


if __name__ == "__main__":
    report()
