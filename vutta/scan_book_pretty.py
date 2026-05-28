"""Scan a canon book and write Ānandajoti-style aligned output to .md.

Usage:
    uv run -m vutta.scan_book_pretty <book_code> [<book_code2> ...] [--out path.md]

Examples:
    uv run -m vutta.scan_book_pretty s0502m_mul --out output/pretty/dhammapada.md
    uv run -m vutta.scan_book_pretty s0501m_mul s0502m_mul s0503m_mul --out output/pretty/khp_dhp_ud.md
"""

import re
import sqlite3
import sys

from .scan import scan
from ._data.env import canon_db_path, repo_root


def _strip_xml(s: str) -> str:
    s = re.sub(r"<pb [^/]*/>", " ", s)
    s = re.sub(r"<note>.*?</note>", "", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _gatha_to_text(gatha_html: str) -> str:
    parts = re.split(r"</p>", gatha_html)
    return " , ".join(c for c in (_strip_xml(p) for p in parts) if c)


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


def render_book(conn, book_code: str) -> str:
    lines = []
    title = BOOK_NAMES.get(book_code, book_code)
    lines.append(f"# {title}\n")
    rows = conn.execute(
        f"SELECT id, rend, paranum, pali_text FROM {book_code} ORDER BY id"
    ).fetchall()
    current_num = None
    buf = []

    def flush():
        nonlocal current_num, buf
        if current_num is None or not buf:
            return
        text = " , ".join(buf)
        try:
            result = scan(text)
        except Exception as e:
            result = f"[scan error: {e}]\n{text}"
        lines.append(f"## v.{current_num}\n")
        lines.append("```")
        lines.append(result)
        lines.append("```\n")

    for _id, rend, paranum, pali in rows:
        if rend == "chapter":
            flush()
            current_num = None
            buf = []
            lines.append(f"\n# {_strip_xml(pali)}\n")
        elif rend == "hangnum" and paranum:
            flush()
            current_num = paranum
            buf = []
        elif rend == "gatha":
            buf.append(_gatha_to_text(pali))
    flush()
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    args = sys.argv[1:]
    out_path = "output/pretty/verse_pretty.md"
    if "--out" in args:
        i = args.index("--out")
        out_path = args[i + 1]
        args = args[:i] + args[i + 2:]
    book_codes = args

    out = repo_root() / out_path
    out.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(f"file:{canon_db_path()}?mode=ro", uri=True)
    chunks = []
    for code in book_codes:
        try:
            chunks.append(render_book(conn, code))
            print(f"  {code}: rendered")
        except sqlite3.OperationalError as e:
            print(f"  {code}: error {e}", file=sys.stderr)
    out.write_text("\n".join(chunks), encoding="utf-8")
    print(f"\nwrote {out}  ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
