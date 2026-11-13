import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import apply  # noqa: E402
import sp_bar  # noqa: E402

FUNDING = "https://jlib271.github.io/stemed-funding/"
OLD_BAND = ('<div class="sp-bar"><div class="sp-in"><a class="sp-logo" href="https://stemedplus.org/">old</a>'
            '<nav class="sp-nav">old menu</nav><a class="sp-login" href="x">Log in</a></div></div>')


def make_site(tmp: Path, config: dict, page: str = None) -> Path:
    site = tmp / "site-repo"
    (site / "site").mkdir(parents=True)
    (site / "site" / "index.html").write_text(page or f"<html><body>{OLD_BAND}<main>Hi</main></body></html>")
    (site / "site" / "stemedplus-theme.css").write_text("/* old */")
    (site / apply.CONFIG).write_text(json.dumps(config))
    return site


class MenuTests(unittest.TestCase):
    def test_menu_is_valid_and_lists_every_site(self):
        menu = sp_bar.load_menu()
        urls = [s["url"] for item in menu["items"] for s in item.get("submenu", [])]
        for site in ("stemed-funding", "STEMEd-Digest", "stemed-deadlines", "stemed-faculty-development"):
            self.assertTrue(any(site in u for u in urls), site)

    def test_band_marks_the_current_site(self):
        band = sp_bar.bar(FUNDING)
        self.assertIn(f'href="{FUNDING}" aria-current="page"', band)
        self.assertIn('class="sp-has sp-here"', band)
        self.assertEqual(band.count('aria-current="page"'), 1)

    def test_bad_menu_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "menu.json"
            bad.write_text(json.dumps({"login": "https://x", "items": [{"label": "A", "url": "http://insecure"}]}))
            with self.assertRaises(ValueError):
                sp_bar.load_menu(bad)


class ApplyTests(unittest.TestCase):
    def test_updates_band_and_existing_assets_only(self):
        with tempfile.TemporaryDirectory() as d:
            site = make_site(Path(d), {"asset_dirs": ["site"], "bars": [{"file": "site/index.html", "current": FUNDING}]})
            self.assertEqual(apply.main(["apply.py", str(site)]), 0)
            page = (site / "site" / "index.html").read_text()
            self.assertIn(sp_bar.bar(FUNDING), page)
            self.assertIn("<main>Hi</main>", page)
            self.assertEqual((site / "site" / "stemedplus-theme.css").read_bytes(),
                             (apply.ASSETS / "stemedplus-theme.css").read_bytes())
            self.assertFalse((site / "site" / "manrope.woff").exists())

    def test_custom_logo_path(self):
        with tempfile.TemporaryDirectory() as d:
            site = make_site(Path(d), {"bars": [{"file": "site/index.html", "logo": "{root}assets/logo.png"}]})
            apply.main(["apply.py", str(site)])
            self.assertIn('src="{root}assets/logo.png"', (site / "site" / "index.html").read_text())

    def test_problem_changes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            site = make_site(Path(d), {"asset_dirs": ["site"],
                                       "bars": [{"file": "site/index.html"}, {"file": "site/missing.html"}]})
            before = (site / "site" / "index.html").read_text()
            self.assertEqual(apply.main(["apply.py", str(site)]), 1)
            self.assertEqual((site / "site" / "index.html").read_text(), before)
            self.assertEqual((site / "site" / "stemedplus-theme.css").read_text(), "/* old */")

    def test_file_without_band_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            site = make_site(Path(d), {"bars": [{"file": "site/index.html"}]}, page="<html>no band</html>")
            self.assertEqual(apply.main(["apply.py", str(site)]), 1)

    def test_runs_as_a_script(self):
        with tempfile.TemporaryDirectory() as d:
            site = make_site(Path(d), {"bars": [{"file": "site/index.html"}]})
            run = subprocess.run([sys.executable, str(ROOT / "apply.py"), str(site)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("updated site/index.html", run.stdout)


if __name__ == "__main__":
    unittest.main()
