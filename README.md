# STEMEd+ shared look

The look shared by the STEMEd+ Commons sites on GitHub Pages, matching https://stemedplus.org:
a green band with the white STEMEd+ Commons logo and the stemedplus.org menu, the Manrope
typeface, green accents, and rounded buttons.

This is the one place to change it. Each site keeps its own copy of these files, so it always
builds even if this repository can't be reached. Each site's build workflow runs `apply.py` first,
which replaces those copies with the current ones here. **A change merged here appears on every
site at its next build** (most sites build daily).

## What's here

| File | What it is |
|---|---|
| `menu.json` | The STEMEd+ Commons menu: Start here, Find (one wide panel of headed groups), Build, Share, About, and a Join button, plus the Log in link. An item can be a link, a link or label with a `submenu`, a label with `groups` (each a `heading` and `links`), or a link with `"button": true`. Every site picks up changes on its next build. |
| `sp_bar.py` | Builds the green band's HTML from `menu.json`, marking the current site's menu item. Needs no JavaScript. `python sp_bar.py <site-url>` prints it. |
| `apply.py` | Updates a site's copies: rebuilds each band and refreshes each theme file the site already has. |
| `assets/stemedplus-theme.css` | Load after a site's own styles. Colors, fonts, buttons, the join box, and the green band. |
| `assets/stemedplus-commons-logo-white.png` | The logo in white, for the green band. |
| `assets/stemedplus-commons-logo.png` | The logo in color. |
| `assets/manrope.woff` | Manrope (Latin subset), by the Manrope Project Authors, under the SIL Open Font License (`assets/manrope-OFL.txt`). |

## Sites that use it

| Site | Repository |
|---|---|
| The Seekers' Hub (Jobs) | [stemed-jobs](https://github.com/JLib271/stemed-jobs) |
| Find Funding | [stemed-funding](https://github.com/JLib271/stemed-funding) |
| STEMEd+ Digest | [STEMEd-Digest](https://github.com/JLib271/STEMEd-Digest) |
| Graduate Programs | [stem-ed-research-programs](https://github.com/JLib271/stem-ed-research-programs) |
| Conferences | [stemed-conferences](https://github.com/JLib271/stemed-conferences) |
| Professional Development | [stemed-professional-development](https://github.com/JLib271/stemed-professional-development) |
| Deadlines | [stemed-deadlines](https://github.com/JLib271/stemed-deadlines) |
| Find Collaborators | [stemed-collaborators](https://github.com/JLib271/stemed-collaborators) |
| HuMeta Library | [humeta-library](https://github.com/JLib271/humeta-library) |

## Adding a site

1. Copy the files in `assets/` that the site uses next to its pages, and put the band in each
   page: `python sp_bar.py https://your-site-url/`.
2. Add `.stemedplus-theme.json` at the site's root, listing the folders with theme files and the
   files with a band:

   ```json
   {
     "asset_dirs": ["site"],
     "bars": [{"file": "site/index.html", "current": "https://jlib271.github.io/your-site/"}]
   }
   ```

   `current` is the site's address as it appears in `menu.json`, so its menu item is marked. Leave it
   out for a site that isn't in the menu. `logo` sets the band's image path, if it isn't
   `stemedplus-commons-logo-white.png`.
3. Add this step to the site's build workflow, before the build:

   ```yaml
   - name: Refresh the shared STEMEd+ look
     continue-on-error: true
     run: |
       git clone --depth 1 https://github.com/JLib271/stemedplus-theme.git "$RUNNER_TEMP/stemedplus-theme"
       python "$RUNNER_TEMP/stemedplus-theme/apply.py" .
   ```

   If this repository can't be reached, or a file can't be updated, the step changes nothing and
   the site builds with its own copies.
4. Add the site to the menu in `menu.json` and to the table above.

## Checking a change

```bash
python -m unittest discover -s tests -v
python sp_bar.py https://jlib271.github.io/stemed-funding/
```

This repository was split out of [HuMeta](https://github.com/JLib271/HuMeta), where it lived in
`standard/stemedplus_theme/`. The shared discipline list (`stemedplus_disciplines.json`) is part of
the HuMeta profile, in [humeta-profile](https://github.com/JLib271/humeta-profile).
