# config.json reference

Paths are relative to the config file. Only `company` and `colors.primary` are really needed; everything else has a default.

```json
{
  "company": "Muster AG",
  "appName": "Atempacer",
  "shortName": "Atempacer",
  "description": "Atemübung der Muster AG",
  "titleHighlight": {"de-sie": "Atem", "en": "Breath"},

  "visual": "circle",
  "languages": ["de-sie", "en"],
  "presets": ["calm", "coherence", "box", "478"],
  "defaultPreset": "calm",
  "duration": 300,

  "colors": {
    "primary": "#0b5c4a",
    "secondary": "#3c8dbc",
    "background": "#ffffff",
    "ink": "#1a1f24"
  },
  "radius": 8,
  "buttonRadius": 8,

  "fonts": {
    "display": { "family": "Fraunces", "fallback": "Georgia, serif", "weight": 400, "faces": [ … ] },
    "body":    { "family": "Inter", "fallback": "system-ui, sans-serif", "faces": [ … ] }
  },

  "logo": { "file": "logo.svg", "alt": "Muster AG", "href": "https://www.muster.de", "height": 48 },
  "icon": { "background": "#0b5c4a", "foreground": "#ffffff", "logo": "signet-1024.png", "safe": 0.72 },

  "texts": { "de-sie": { "privacy": "…" } },
  "customCss": "",
  "customCssFile": "brand.css",
  "decorHtml": "",
  "output": "dist"
}
```

| Key | Meaning |
|---|---|
| `company` | Used in the page title and install name (`<appName> – <company>`). |
| `appName` | Title in the app. String, or object per language (`{"de-sie": "Atempause", "en": "Breathing Space"}`). Default from the language file. |
| `shortName` | Name under the home screen icon. Keep it ≤ 12 characters. |
| `titleHighlight` | Part of the title shown in brand colour, string or object per language. Default from the language file ("Atem", "Breath"). `""` = none. |
| `visual` | `circle` · `flower` · `wave` · `square` |
| `languages` | Order matters: the first is the fallback. The app picks the phone's language if it's in the list, and remembers a manual switch. Bundled: `de-sie`, `de-du`, `en`. Others: `i18n/<code>.json` in the project, all keys of `en.json`. Codes like `fr`, `es`, `nl`, `tr`, `pl`, `it`, `uk`, `ar` (right-to-left is not supported by the layout – say so if asked). |
| `presets` | Built-in ids: `calm` 4/0/6/0, `coherence` 5/0/5/0, `box` 4/4/4/4, `478` 4/7/8/0, `energize` 4/0/2/0. Custom: `{"id": "slow", "name": {"de-sie": "Langsam", "en": "Slow"}, "in": 5, "h1": 0, "out": 7, "h2": 0}`. Values in seconds, 0.5 steps work. |
| `defaultPreset` | Id the app starts with on first visit. Default 4/6 = `calm`. |
| `duration` | Default session length in seconds (60–1800). |
| `colors.primary` | Buttons, selected preset, inhale phase. |
| `colors.secondary` | Exhale phase and focus ring. Default: primary darkened. |
| `colors.background` / `surface` / `ink` / `muted` / `line` | Page, cards, text, secondary text, hairlines. `muted` and `line` are mixed from ink and background if missing. |
| `colors.onPrimary` | Text on primary buttons. Default: white or ink, whichever contrasts more. |
| `colors.inhale` / `exhale` / `hold` | Override the phase colours if the brand needs it. |
| `radius`, `buttonRadius` | Corner radius in px for cards and for buttons (999 = pill). |
| `fonts.*.faces` | `[{ "weight": 400` (or a range like `"400 500"` for variable fonts), "style": "normal", "file": "fonts/x.woff2", "unicodeRange": "…" }]` – woff2, woff, ttf or otf. `fetch_font.py` prints this block. `display.weight` sets the weight used for title, timer and counter (default 300). |
| `logo` | SVG or PNG/JPG. `href` makes it a link (opens in a new tab). `height` in px. |
| `icon` | Home screen icon. Default: chosen animation as a white symbol on `primary`. `logo` (PNG/JPG, square works best) replaces the symbol. `safe` = share of the icon the symbol fills. |
| `texts` | Override single strings per language without copying the file. Keys: see `assets/i18n/en.json`. |
| `customCss` / `customCssFile` | Extra CSS appended last. CSS variables you can use: `--primary --secondary --bg --surface --surface-2 --ink --muted --line --font-body --font-display --radius --radius-btn`. Main classes: `.head .titel .intro .preset .phase-row .step .btn-primary .btn-dark .stage .readout .done`. |
| `decorHtml` / `decorHtmlFile` | Markup inserted at the start of `<body>`, e.g. decorative shapes. Give it `aria-hidden="true"` and `position: fixed; z-index: 0; pointer-events: none` in CSS. No scripts. |
| `storageKey` | localStorage key. Default from the company name; change it only to reset saved settings. |
| `output` | Output folder, default `dist`. |
