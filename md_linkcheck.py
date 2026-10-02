#!/usr/bin/env python3
"""Check local inline links in Markdown files without making network requests."""

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\s*\)")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
SKIP_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "dist", "build"}


def markdown_files(root):
    if root.is_file():
        if root.suffix.lower() == ".md":
            yield root
        return
    for folder, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS)
        for name in sorted(files):
            path = Path(folder, name)
            if path.suffix.lower() == ".md":
                yield path


def checked_links(path, root):
    fenced_char = None
    fenced_size = 0
    with path.open(encoding="utf-8-sig") as source:
        for number, line in enumerate(source, 1):
            fence = FENCE_RE.match(line)
            if fence:
                marker = fence.group(1)
                char = marker[0]
                if fenced_char is None:
                    fenced_char, fenced_size = char, len(marker)
                elif char == fenced_char and len(marker) >= fenced_size:
                    fenced_char = None
                continue
            if fenced_char:
                continue

            line = re.sub(r"`[^`]*`", "", line)
            for match in LINK_RE.finditer(line):
                destination = match.group(1) or match.group(2)
                try:
                    parts = urlsplit(destination)
                except ValueError:
                    yield number, destination
                    continue
                if parts.scheme or destination.startswith("//"):
                    continue
                if not parts.path:
                    continue
                target = unquote(parts.path)
                candidate = (root / target.lstrip("/")) if target.startswith("/") else (path.parent / target)
                if candidate.is_dir():
                    candidate = next(
                        (candidate / name for name in ("README.md", "index.md") if (candidate / name).is_file()),
                        candidate,
                    )
                if not candidate.exists():
                    yield number, destination


def main():
    parser = argparse.ArgumentParser(
        description="Find missing local targets in Markdown inline links; never fetches URLs."
    )
    parser.add_argument("path", type=Path, help="Markdown file or directory to scan")
    args = parser.parse_args()
    root = args.path.resolve()
    if not root.exists():
        print(f"md-linkcheck: path not found: {args.path}", file=sys.stderr)
        return 2
    scan_root = root if root.is_dir() else root.parent
    files = list(markdown_files(root))
    if not files:
        print("No Markdown files found.")
        return 0

    failures = 0
    for path in files:
        try:
            for number, destination in checked_links(path, scan_root):
                print(f"{path}:{number}: missing {destination!r}")
                failures += 1
        except (OSError, UnicodeError) as error:
            print(f"md-linkcheck: {path}: {error}", file=sys.stderr)
            failures += 1
    if failures:
        print(f"Found {failures} issue(s) across {len(files)} Markdown file(s).")
        return 1
    print(f"No missing local links in {len(files)} Markdown file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
