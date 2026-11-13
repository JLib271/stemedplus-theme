"""Bring a STEMEd+ site up to date with the shared look.

Run from a site's repository (its build workflow does this before building):

    python /path/to/stemedplus-theme/apply.py [site-repo-dir]

The site lists what to update in `.stemedplus-theme.json` at its root:

    {
      "asset_dirs": ["site"],
      "bars": [
        {"file": "site/index.html", "current": "https://jlib271.github.io/stemed-funding/"}
      ]
    }

- `asset_dirs`: folders that hold copies of the theme files. Each theme file already in the
  folder is replaced with the current one; files the site does not use are not added.
- `bars`: files that contain the green band. Each band is rebuilt from menu.json, with the
  site's own menu item (`current`) marked. `logo` is the image path written into the band
  (default `stemedplus-commons-logo-white.png`).

Nothing is written unless every file can be updated, so a problem leaves the site's own copies
as they were. Exit status 1 means nothing changed.
"""
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sp_bar  # noqa: E402

ASSETS = HERE / "assets"
CONFIG = ".stemedplus-theme.json"
BAND = re.compile(r'<div class="sp-bar"><div class="sp-in">.*?</nav>(?:<a class="sp-login"[^>]*>Log in</a>)?</div></div>',
                  re.S)


def plan(site: Path) -> tuple:
    """Work out every change without writing anything. Returns (text_updates, copies)."""
    config = json.loads((site / CONFIG).read_text(encoding="utf-8"))
    menu = sp_bar.load_menu()
    texts = {}
    for b in config.get("bars", []):
        path = site / b["file"]
        text = texts.get(path) or path.read_text(encoding="utf-8")
        band = sp_bar.bar(b.get("current", ""), b.get("logo", "stemedplus-commons-logo-white.png"), menu)
        new, n = BAND.subn(lambda m: band, text)
        if n == 0:
            raise ValueError(f"{b['file']}: no STEMEd+ band found")
        texts[path] = new
    copies = []
    for d in config.get("asset_dirs", []):
        folder = site / d
        if not folder.is_dir():
            raise ValueError(f"{d}: not a folder")
        copies += [(src, folder / src.name) for src in sorted(ASSETS.iterdir()) if (folder / src.name).exists()]
    return texts, copies


def main(argv) -> int:
    site = Path(argv[1] if len(argv) > 1 else ".").resolve()
    try:
        texts, copies = plan(site)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"stemedplus-theme: nothing changed: {exc}", file=sys.stderr)
        return 1
    changed = []
    for path, text in texts.items():
        if path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
            changed.append(path)
    for src, dest in copies:
        if src.read_bytes() != dest.read_bytes():
            shutil.copyfile(src, dest)
            changed.append(dest)
    for path in changed:
        print(f"stemedplus-theme: updated {path.relative_to(site)}")
    if not changed:
        print("stemedplus-theme: already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
