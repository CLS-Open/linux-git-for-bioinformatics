#!/usr/bin/env python3
"""CI guard 2 — internal documentation link check (offline, deterministic).

External links rot and rate-limit; internal links rot *silently* and are
entirely within our control, so they are checked on every push.

Exit code 0 = all internal links resolve; 1 = broken links (printed with source).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_GLOBS = ["README.md", "CONTRIBUTING.md", "CHANGELOG.md", "SECURITY.md",
             "docs/**/*.md", "projects/**/*.md", "datasets/README.md", "LICENSES/README.md"]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def resolve(base: Path, target: str, src: Path) -> bool:
    target = target.split("#", 1)[0].strip()
    if not target or target.startswith(("http://", "https://", "mailto:", "tel:")):
        return True
    if target.startswith("/"):
        return (ROOT / target.lstrip("/")).exists()
    return (src.parent / target).resolve().exists()


def main() -> int:
    sources: list[Path] = []
    for pattern in DOC_GLOBS:
        sources.extend(sorted(ROOT.glob(pattern)))
    broken: list[tuple[Path, str]] = []
    checked = 0
    for src in sources:
        for target in LINK_RE.findall(src.read_text(encoding="utf-8")):
            checked += 1
            if not resolve(ROOT, target, src):
                broken.append((src.relative_to(ROOT), target))
    print(f"checked {checked} internal links across {len(sources)} markdown files")
    if broken:
        print("FAILED — broken internal links:")
        for src, target in broken:
            print(f"  {src} -> {target}")
        return 1
    print("OK: all internal links resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
