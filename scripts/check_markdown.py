#!/usr/bin/env python3
"""Verify local links and image references in Markdown files.

External URLs are intentionally skipped; this check keeps the repository's own
references honest. Run with: python3 scripts/check_markdown.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

MARKDOWN_REF = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_REF = re.compile(r'(?:src|href|srcset)=["\']([^"\']+)["\']')


def is_external(ref: str) -> bool:
    scheme = urlsplit(ref).scheme
    return bool(scheme) or ref.startswith("#")


def references(text: str) -> list[str]:
    found = [m.group(1) for m in MARKDOWN_REF.finditer(text)]
    for group in HTML_REF.finditer(text):
        for item in group.group(1).split(","):
            candidate = item.strip().split()[0] if item.strip() else ""
            if candidate:
                found.append(candidate)
    return found


def main() -> int:
    broken: list[str] = []
    checked = 0

    for path in sorted(ROOT.rglob("*.md")):
        if any(part in {"__MACOSX", ".git"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for ref in references(text):
            if is_external(ref):
                continue
            target = (path.parent / unquote(ref)).resolve()
            checked += 1
            if not target.exists():
                broken.append(f"{path.relative_to(ROOT)}: {ref} -> missing")

    if broken:
        print(f"Checked {checked} local references; {len(broken)} broken:")
        for item in broken:
            print("  -", item)
        return 1

    print(f"Checked {checked} local references; all resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
