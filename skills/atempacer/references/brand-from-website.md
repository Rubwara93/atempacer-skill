# Getting the corporate design from a website

Use this when the user gives a URL but no brand guide. Tell them the result is read from the website, not from an official guide, and let them confirm.

1. **Fetch the page and its stylesheets.** With a fetch tool or `curl -sL <url>`; then fetch the CSS files linked in `<head>` (`<link rel="stylesheet" href=…>`). Many sites keep brand colours as CSS variables (`--primary`, `--brand`, `--color-…`) – those are the best source.
2. **Colours.** Count hex/rgb values across the CSS (`grep -oE '#[0-9a-fA-F]{6}' | sort | uniq -c | sort -rn`). Ignore pure greys, black and white for `primary`/`secondary`. The colour of buttons, links and the header is usually the primary. Check `<meta name="theme-color">` too.
3. **Fonts.** Look at `font-family` on `body` and `h1`/`h2`, at `fonts.googleapis.com` links and at `@font-face` rules. Google Font → fetch with `scripts/fetch_font.py`. Self-hosted commercial font (Adobe Fonts, Monotype, custom) → ask about a web licence or choose the closest Google Font.
4. **Logo.** Look for `<img>`/`<svg>` in the header, `class`/`alt` containing "logo", the `apple-touch-icon` and `og:image`. Download the SVG if there is one. Use the logo only for this client's own pacer.
5. **Shapes and tone.** Rounded or sharp buttons (→ `radius`, `buttonRadius`), light or dark background, and whether the site says "du" or "Sie".

Show a short summary: primary, secondary, background, text colour (hex), fonts, logo file, radius, address form. Then go on with the adjustments.
