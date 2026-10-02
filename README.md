# md-linkcheck

Find broken local targets in Markdown inline links. It scans a file or a directory recursively, skips common generated and dependency folders, and never requests a URL or changes a file.

## Use

Requires Python 3.8+; no packages to install.

```sh
python md_linkcheck.py README.md
python md_linkcheck.py docs/
```

Exit status is `0` when all checked targets exist, `1` when a target is missing or a Markdown file cannot be read, and `2` when the scan path does not exist. External links, fragment-only links, and links inside fenced or single-backtick code are skipped. Directory links resolve to `README.md` or `index.md` when either exists.

The checker handles ordinary inline links and images, including angle-bracket-wrapped paths. Reference-style links and destinations with nested parentheses are outside its small parser's scope. It checks target paths, not heading fragments.

## License

MIT
