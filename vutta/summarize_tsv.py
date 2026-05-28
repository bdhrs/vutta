"""Summarize a scansion TSV: per-book stats, family distribution.

Usage: uv run -m vutta.summarize_tsv [path.tsv]
"""

import sys
from collections import Counter
from pathlib import Path

from ._data.env import repo_root


BOOK_NAMES = {
    "s0501m_mul": "Khuddakapāṭha",
    "s0502m_mul": "Dhammapada",
    "s0503m_mul": "Udāna",
    "s0504m_mul": "Itivuttaka",
    "s0505m_mul": "Suttanipāta",
    "s0506m_mul": "Vimānavatthu",
    "s0507m_mul": "Petavatthu",
    "s0508m_mul": "Theragāthā",
    "s0509m_mul": "Therīgāthā",
    "s0511m_mul": "Buddhavaṃsa",
    "s0512m_mul": "Cariyāpiṭaka",
    "e0808n_nrf": "Vuttodaya",
}


def fam_of(metre: str) -> str:
    if metre.startswith("Siloka"):
        return "Siloka"
    if metre == "unmatched":
        return "unmatched"
    if metre == "ERROR":
        return "ERROR"
    if metre in ("Tuṭṭhubha", "Jagatī", "Tuṭṭhubha/Jagatī mix"):
        return "Tuṭṭhubha/Jagatī"
    if metre in ("Vetālīya", "Opacchandasaka", "Āpātalikā"):
        return "mātrā"
    return "other-fixed"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root() / "output/tsv/verse_scansion.tsv"
    by_book_total: dict[str, int] = {}
    by_book_fam: dict[str, Counter] = {}
    by_book_cost: dict[str, list[float]] = {}

    with path.open() as f:
        header = f.readline().rstrip("\n").split("\t")
        idx = {k: i for i, k in enumerate(header)}
        for line in f:
            row = line.rstrip("\n").split("\t")
            if len(row) < len(header):
                continue
            book = row[idx["book_code"]]
            metre = row[idx["metre"]]
            cost = float(row[idx["cost"]])
            by_book_total[book] = by_book_total.get(book, 0) + 1
            by_book_fam.setdefault(book, Counter())[fam_of(metre)] += 1
            by_book_cost.setdefault(book, []).append(cost)

    print(f"{'book':28} {'total':>6} {'exact':>6} {'≤0.5':>5} {'≤1.0':>5} {'≤2.0':>5} {'>2':>4} {'unm':>4}")
    print("-" * 70)
    grand = Counter()
    grand_cost: list[float] = []
    grand_total = 0
    for book, total in by_book_total.items():
        name = BOOK_NAMES.get(book, book)
        costs = by_book_cost[book]
        ex = sum(1 for c in costs if c == 0)
        c5 = sum(1 for c in costs if 0 < c <= 0.5)
        c10 = sum(1 for c in costs if 0.5 < c <= 1.0)
        c20 = sum(1 for c in costs if 1.0 < c <= 2.0)
        cgt = sum(1 for c in costs if 2.0 < c < 99.0)
        unm = by_book_fam[book].get("unmatched", 0)
        print(f"{name:28} {total:>6} {ex:>6} {c5:>5} {c10:>5} {c20:>5} {cgt:>4} {unm:>4}")
        grand_total += total
        grand_cost.extend(costs)
        for k, v in by_book_fam[book].items():
            grand[k] += v
    print("-" * 70)
    ex = sum(1 for c in grand_cost if c == 0)
    c5 = sum(1 for c in grand_cost if 0 < c <= 0.5)
    c10 = sum(1 for c in grand_cost if 0.5 < c <= 1.0)
    c20 = sum(1 for c in grand_cost if 1.0 < c <= 2.0)
    cgt = sum(1 for c in grand_cost if 2.0 < c < 99.0)
    unm = grand.get("unmatched", 0)
    print(f"{'TOTAL':28} {grand_total:>6} {ex:>6} {c5:>5} {c10:>5} {c20:>5} {cgt:>4} {unm:>4}")
    pct_clean = (ex + c5 + c10) / grand_total * 100
    print(f"\ncleanly identified (cost ≤ 1.0): {pct_clean:.1f}%")
    print(f"\nfamily distribution:")
    for fam, n in grand.most_common():
        print(f"  {fam:20s}  {n:>6}  ({n/grand_total*100:.1f}%)")


if __name__ == "__main__":
    main()
