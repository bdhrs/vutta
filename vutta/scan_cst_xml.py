"""Scan every CST XML file that contains gāthā tags and write aligned .md.

Usage:
    uv run -m vutta.scan_cst_xml                        # all files
    uv run -m vutta.scan_cst_xml s0502m.mul.xml         # one file
    uv run -m vutta.scan_cst_xml --out-dir path/to/dir  # custom output dir

CST XML source is read from the VUTTA_CST_DIR env var (set in .env).
Point it at the romn/ directory of the CST dpd-db submodule.

Output:
    output/cst/<basename-without-.xml>.md
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

from .scan import scan
from ._data.env import repo_root, load_env


def _cst_romn_dir() -> Path:
    env = load_env()
    raw = env.get("VUTTA_CST_DIR")
    if not raw:
        raise RuntimeError(
            "Set VUTTA_CST_DIR in .env or environment "
            "(pointing to the CST romn/ directory of XML files)."
        )
    return Path(os.path.expanduser(raw))


def discover_xml_files() -> list[Path]:
    return sorted(_cst_romn_dir().glob("*.xml"))


def read_xml(path: Path) -> str:
    data = path.read_bytes()
    return data.decode("utf-16")


def _get_text(el) -> str:
    """Extract text from a gatha element, skipping <note> content."""
    parts = [el.text or ""]
    for child in el:
        if child.tag != "note":
            parts.append(child.text or "")
        parts.append(child.tail or "")
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def iter_verses(xml_str: str) -> Iterator[tuple[str, str, list[str]]]:
    """Yield (vagga, paranum, gatha_lines) for every verse in the document.

    gatha_lines is a list of individual gatha element texts (one per gatha1/2/3/last).
    Callers should scan each line independently.

    Handles two numbering schemes found in the CST XML:
    - hangnum style: <p rend="hangnum" n="N"> precedes each verse group.
    - bodytext style: <p rend="bodytext" n="N"> precedes the verse; gatha1
      signals the start of each new verse.

    gathalast closes a verse; stray gatha lines after it are ignored until the
    next gatha1 opens a new one. A gatha1 with no preceding paranum marker gets
    paranum "?".
    """
    root = ET.fromstring(xml_str)

    current_vagga = ""
    current_paranum: str | None = None
    last_paranum: str | None = None
    paranum_fresh = False
    in_verse = False
    buf: list[str] = []

    def flush():
        nonlocal in_verse, buf
        if buf:
            yield (current_vagga, current_paranum or "?", list(buf))
        in_verse = False
        buf = []

    for el in root.iter():
        rend = el.get("rend", "")

        if el.tag == "head" and rend == "chapter":
            yield from flush()
            current_paranum = None
            last_paranum = None
            paranum_fresh = False
            current_vagga = _get_text(el)

        elif el.tag == "p" and rend == "hangnum":
            yield from flush()
            n = el.get("n", "")
            current_paranum = n if n else None
            last_paranum = current_paranum
            paranum_fresh = True

        elif el.tag == "p" and rend == "bodytext":
            n = el.get("n", "")
            if n:
                last_paranum = n
                paranum_fresh = True

        elif el.tag == "p" and rend == "gatha1":
            yield from flush()
            current_paranum = last_paranum if paranum_fresh else "?"
            paranum_fresh = False
            in_verse = True
            buf = [_get_text(el)]

        elif el.tag == "p" and rend in ("gatha2", "gatha3"):
            if in_verse:
                buf.append(_get_text(el))

        elif el.tag == "p" and rend == "gathalast":
            if in_verse:
                buf.append(_get_text(el))
            in_verse = False

    yield from flush()


def _book_title(xml_str: str, fallback: str) -> str:
    root = ET.fromstring(xml_str)
    for el in root.iter("head"):
        if el.get("rend") == "book":
            return _get_text(el)
    return fallback


def render_file(path: Path) -> str | None:
    xml_str = read_xml(path)
    verses = list(iter_verses(xml_str))
    if not verses:
        return None

    title = _book_title(xml_str, path.stem)
    lines = [f"# {title}\n"]
    current_vagga = None

    for vagga, paranum, gatha_lines in verses:
        if vagga != current_vagga:
            current_vagga = vagga
            if vagga:
                lines.append(f"\n# {vagga}\n")

        lines.append(f"## v.{paranum}\n")
        for gatha_text in gatha_lines:
            try:
                result = scan(gatha_text)
            except Exception as e:
                result = f"{gatha_text}\nmetre: unknown  [{e}]"
            lines.append("```")
            lines.append(result)
            lines.append("```\n")
        lines.append("---\n")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    out_dir = repo_root() / "output" / "cst"
    if "--out-dir" in args:
        i = args.index("--out-dir")
        out_dir = Path(args[i + 1])
        args = args[:i] + args[i + 2:]

    if args:
        paths = []
        for a in args:
            p = Path(a)
            if not p.is_absolute():
                p = _cst_romn_dir() / p.name
            paths.append(p)
    else:
        paths = discover_xml_files()

    out_dir.mkdir(parents=True, exist_ok=True)

    total_verses = 0
    rendered = 0
    for path in paths:
        try:
            md = render_file(path)
        except Exception as e:
            print(f"  {path.name}: ERROR {e}", file=sys.stderr)
            continue
        if md is None:
            print(f"  {path.name}: no gāthās, skipped")
            continue
        stem = path.name.replace(".xml", "")
        out_path = out_dir / f"{stem}.md"
        out_path.write_text(md, encoding="utf-8")
        verse_count = md.count("## v.")
        total_verses += verse_count
        print(f"  {path.name}: {verse_count} verses → {out_path.name}")
        rendered += 1

    print(f"\n{rendered} files written to {out_dir}  ({total_verses} verses total)")


if __name__ == "__main__":
    main()
