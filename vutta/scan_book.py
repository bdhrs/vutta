"""Scan every verse in a canon book and write results to a TSV.

Usage:
    uv run -m vutta.scan_book <book_code> [<book_code2> ...] [--out path.tsv]

Examples:
    uv run -m vutta.scan_book s0502m_mul                  # Dhammapada
    uv run -m vutta.scan_book s0505m_mul                  # Suttanipāta
    uv run -m vutta.scan_book s0508m_mul s0509m_mul

Output TSV columns:
    book_code, paranum, vagga, metre, cost, pada_count, scansion, pali
"""

import re
import sqlite3
import sys
from pathlib import Path

from .normalize import clean
from .pada_split import split_padas
from .syllabify import syllabify_pada
from .weight import weigh
from .match import match
from ._data.env import canon_db_path, repo_root


def _strip_xml(s: str) -> str:
    s = re.sub(r"<pb [^/]*/>", " ", s)
    s = re.sub(r"<note>.*?</note>", "", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _padayugas_from_gatha(gatha_html: str) -> list[str]:
    parts = re.split(r"</p>", gatha_html)
    return [c for c in (_strip_xml(p) for p in parts) if c]


def scan_book(conn, book_code: str):
    rows = conn.execute(
        f"SELECT id, rend, paranum, pali_text FROM {book_code} ORDER BY id"
    ).fetchall()

    current_vagga = ""
    current_num = None
    buf: list[str] = []

    def flush():
        nonlocal current_num, buf
        if current_num is None or not buf:
            return None
        text = " , ".join(buf)
        try:
            cleaned = clean(text)
            padas = split_padas(cleaned)
            # Scansion uses metrical (substituted) form per pāda.
            from .normalize import metrical
            ws = []
            for p in padas:
                sub_p, _ = metrical(p)
                ws.append(weigh(syllabify_pada(sub_p)))
            top = match(ws)
        except Exception as e:
            return (current_num, current_vagga, text, "ERROR", 999.0, str(e))
        if not top:
            return (current_num, current_vagga, text, "unmatched", 99.0, " | ".join(ws))
        name, cost = top[0]
        return (current_num, current_vagga, text, name, cost, " | ".join(ws))

    for _id, rend, paranum, pali in rows:
        if rend == "chapter":
            current_vagga = _strip_xml(pali)
        elif rend == "hangnum" and paranum:
            result = flush()
            if result:
                yield result
            current_num = paranum
            buf = []
        elif rend == "gatha":
            buf.extend(_padayugas_from_gatha(pali))
    result = flush()
    if result:
        yield result


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    args = sys.argv[1:]
    out_path = "data/output/verse_scansion.tsv"
    if "--out" in args:
        i = args.index("--out")
        out_path = args[i + 1]
        args = args[:i] + args[i + 2:]
    book_codes = args

    out = repo_root() / out_path
    out.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(f"file:{canon_db_path()}?mode=ro", uri=True)

    with out.open("w", encoding="utf-8") as f:
        f.write("book_code\tparanum\tvagga\tmetre\tcost\tpada_count\tscansion\tpali\n")
        totals = {}
        for code in book_codes:
            count = 0
            try:
                for paranum, vagga, text, metre, cost, scansion in scan_book(conn, code):
                    pada_count = len(scansion.split(" | "))
                    text_c = text.replace("\t", " ").replace("\n", " ")
                    s_c = scansion.replace("\t", " ")
                    f.write(f"{code}\t{paranum}\t{vagga}\t{metre}\t{cost}\t{pada_count}\t{s_c}\t{text_c}\n")
                    count += 1
            except sqlite3.OperationalError as e:
                print(f"  {code}: error {e}", file=sys.stderr)
                continue
            totals[code] = count
            print(f"  {code}: {count} verses scanned")
    print(f"\nwrote {out}")
    print(f"totals: {totals}")


if __name__ == "__main__":
    main()
