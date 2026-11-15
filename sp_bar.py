"""The green STEMEd+ Commons band at the top of every STEMEd+ site, and the footer at the bottom.

The band copies the menu of https://stemedplus.org (same items, same order, same submenus) so the
GitHub Pages sites look like part of that site. The menu itself is in menu.json; when the
stemedplus.org menu changes, change menu.json and every site picks it up on its next build.

The footer copies stemedplus.org's footer (what STEMEd+ Commons is, and its NSF and MSU support);
its text is the "footer" entry of menu.json.

The band needs no JavaScript: submenus open on hover or keyboard focus, and on narrow screens
a "Menu" button (a checkbox and its label) opens the whole menu as a list.

    python sp_bar.py [current-url] [logo-path]     # print the band's HTML
    python sp_bar.py --footer                      # print the footer's HTML
"""
import html
import json
import re
import sys
from pathlib import Path

MENU_FILE = Path(__file__).with_name("menu.json")
CHEVRON = ('<svg class="sp-chev" width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">'
           '<path d="M1.5 4L6 8L10.5 4" stroke="currentColor" stroke-width="1.5"/></svg>')


def load_menu(path: Path = MENU_FILE) -> dict:
    """Read menu.json and check its shape; raise ValueError if it is not usable."""
    menu = json.loads(Path(path).read_text(encoding="utf-8"))
    if not str(menu.get("login", "")).startswith("https://"):
        raise ValueError("menu.json: login must be an https:// URL")
    items = menu.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("menu.json: items must be a non-empty list")
    for item in items:
        for entry in [item] + list(item.get("submenu", [])):
            if not entry.get("label") or not str(entry.get("url", "")).startswith("https://"):
                raise ValueError(f"menu.json: every item needs a label and an https:// url: {entry!r}")
    footer = menu.get("footer")
    if not isinstance(footer, str) or not footer.strip():
        raise ValueError("menu.json: footer must be the footer's HTML")
    if any(ch in footer for ch in "{}`'\\"):
        raise ValueError("menu.json: footer must not contain { } ` ' or \\ (sites put it inside code templates)")
    for href in re.findall(r'href="([^"]*)"', footer):
        if not href.startswith("https://"):
            raise ValueError(f"menu.json: footer links must be https:// URLs: {href!r}")
    return menu


def footer(menu: dict = None) -> str:
    """The STEMEd+ Commons footer's HTML, as on stemedplus.org."""
    menu = menu or load_menu()
    return f'<footer class="sp-footer"><div class="sp-fin"><p>{menu["footer"]}</p></div></footer>'


def bar(current: str = "", logo: str = "stemedplus-commons-logo-white.png", menu: dict = None) -> str:
    """The band's HTML. ``current`` is this site's URL; its menu item is marked as the current page."""
    menu = menu or load_menu()
    e = html.escape

    def a(label, url):
        cur = ' aria-current="page"' if current and url == current else ""
        return f'<a href="{e(url)}"{cur}>{e(label)}</a>'

    items = []
    for item in menu["items"]:
        sub = item.get("submenu", [])
        if sub:
            here = any(current and s["url"] == current for s in sub)
            subs = "".join(f"<li>{a(s['label'], s['url'])}</li>" for s in sub)
            items.append(f'<li class="sp-has{" sp-here" if here else ""}">{a(item["label"], item["url"])}{CHEVRON}'
                         f'<ul class="sp-sub">{subs}</ul></li>')
        else:
            items.append(f"<li>{a(item['label'], item['url'])}</li>")
    return (
        '<div class="sp-bar"><div class="sp-in">'
        f'<a class="sp-logo" href="https://stemedplus.org/"><img src="{logo}" alt="STEMEd+ Commons home" width="263" height="91"></a>'
        '<input type="checkbox" id="sp-menu-toggle" class="sp-toggle">'
        '<label for="sp-menu-toggle" class="sp-burger"><span class="sp-burger-icon" aria-hidden="true"></span>Menu</label>'
        f'<nav class="sp-nav" aria-label="STEMEd+ Commons"><ul class="sp-top">{"".join(items)}</ul></nav>'
        f'<a class="sp-login" href="{e(menu["login"])}">Log in</a>'
        '</div></div>'
    )


if __name__ == "__main__":
    print(footer() if sys.argv[1:] == ["--footer"] else bar(*sys.argv[1:]))
