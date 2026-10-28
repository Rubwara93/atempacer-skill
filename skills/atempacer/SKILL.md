---
name: atempacer
description: Builds a breath pacer (Atempacer) web app in a company's corporate design – one self-contained HTML file plus home screen icons, offline cache and install manifest, ready to upload and add to a phone's home screen. Use whenever someone wants a breathing exercise app, breath pacer, Atemübung, Atemtrainer, Resonanzatmung or Kohärenzatmung tool for a client, company, team or training in their own branding, wants to re-brand an existing pacer, or asks to change its default rhythm, languages or animation (circle, flower, wave, square).
---

# Atempacer – branded breath pacer

You build a small breathing-exercise web app in someone's corporate design. The person you work with is usually a coach, trainer or consultant making it for a client. The result runs entirely on the device: no tracking, no server logic, no data leaves the phone.

**Talk to the user in their language** (German if they write German, and so on). Everything below is instructions for you, not text to show them.

## What gets built

`scripts/build.py` turns a `config.json` into a folder:

```
<slug>-atempacer/
  config.json, logo, fonts/, i18n/   ← sources (you write these)
  dist/                              ← upload this folder
    index.html                       the whole app in one file
    apple-touch-icon.png             iPhone home screen icon
    icon-192.png, icon-512.png, icon-maskable-512.png
    manifest.webmanifest, sw.js      install + offline
```

`dist/index.html` alone works when opened on a computer, so it can be emailed. **For the home screen icon on a phone the `dist/` folder must be online** (any static host, HTTPS). An HTML file opened from mail, WhatsApp or AirDrop on an iPhone lands in Quick Look, where scripts don't run and "Add to Home Screen" doesn't exist. Say this early and plainly, it's the most common misunderstanding.

## Flow

### 1. Brand

Ask for whatever they have, in one message: company name, website, logo file, colours, fonts, brand guide or design system. Read every file or folder they point to before asking anything else.

If only a website is given, extract the design yourself – see `references/brand-from-website.md`. Then show what you found (colours with hex, font names, logo source) and let them confirm or correct it. Never invent brand colours; if you're guessing, say so.

Decide the mapping (details in `references/config.md`):
- `primary` – main brand colour: buttons, selected preset, **breathing in**
- `secondary` – second brand colour: **breathing out**. It fills half of every breath, so if the brand guide says its accent colour is to be used sparingly (or it's a light yellow/orange), use a darker shade of the primary as `colors.exhale` and keep the accent for `secondary` only – mention the choice
- `background`, `ink` (text), optionally `muted`, `line`, `surface`, `hold`
- `radius` / `buttonRadius` from the brand's shapes (0 = sharp, 999 = pill buttons)
- display font + body font; anything brand-specific beyond that goes in `customCss`

Fonts: Google Fonts → `python3 scripts/fetch_font.py "<Family>" 400,500 <project>/fonts` (add `--serif` for a serif, `--italic` if the brand uses italics) and paste the printed block into `fonts.body` / `fonts.display`; for the display font set `weight` to the weight the title should have. A commercial brand font may only be embedded if the company holds a web licence – ask; if unclear, pick the closest Google Font and say which. No font at all → the bundled Roboto is used.

Logo: SVG preferred (inlined; scripts and event handlers are stripped). PNG/JPG works too. A round signet without wordmark is fine as logo; give it `height` 40–48.

Home screen icon – decide like this:
- The brand has a compact signet/symbol (round or square, readable at 60 px) → `icon.logo` with a PNG of it, at least 512 px (1024 best), and `icon.background` = the colour the signet sits on (for a coloured round signet: that same colour, so the circle merges into the tile). 
- Only a wide wordmark → don't squeeze it in; leave `icon.logo` out and the icon shows the chosen animation as a white symbol on the primary colour.
- If you only have an SVG and need a PNG on macOS: `qlmanage -t -s 1024 -o <dir> logo.svg`.

### 2. Adjustments

Ask with your question tool (in Claude Code: `AskUserQuestion`, max. 4 questions per call, recommended option first and marked as such). Without such a tool, ask as a short numbered list. Two rounds:

**Round A**
1. **Animation** – Circle (recommended, calmest) · Flower (petals open and close) · Wave (dot travels along the breath curve, good for longer exhales) · Square (box breathing; with no holds it becomes a rising and falling line). Use each option's `preview` field, if your tool has one, to describe the motion in one line. Then offer to let users switch between animations in the app (`visuals`: the chosen ones or `"all"`); the one picked here stays the start animation and the icon symbol.
2. **Default rhythm** – 4 s in / 6 s out "Calm" (recommended, the established default) · 5/5 "Coherence" · Box 4-4-4-4 · 4-7-8 · custom (they name seconds for in / hold / out / hold).
3. **Languages** (multi-select) – German, English, + "other" (they name them). The language switch appears in the app once there are two or more.
4. **German form of address** (only if German is chosen) – Sie / du. Take it from the brand's own texts if you've seen them and just confirm.

**Round B** (skip what's already answered)
1. Which exercises appear as buttons (2–4; default: calm, coherence, box, 4-7-8; `energize` 4/2 also available; custom ones allowed).
2. Default duration (5 min recommended; 1–30 min).
3. App name on the home screen (≤ 12 characters so iOS doesn't cut it; default "Atempacer" / "Breath Pacer") and which part of the title gets the brand colour (`titleHighlight`, default "Atem" / "Breath").
4. Anything else in the CD: decorative shapes, special typography, a footer link → `customCss`, `decorHtml`.

### 3. Build

1. Create `<slug>-atempacer/` in the current directory (or where the user says). Copy logo and fonts in.
2. Extra languages: copy `assets/i18n/en.json` to `<project>/i18n/<code>.json` and translate **every** value (keep keys and `{placeholders}`, set `short`, `languageName`, `locale`). Use natural, calm phrasing a native speaker would use for a breathing exercise. Single wording changes for bundled languages go into `texts` in config.json instead of copying a whole file.
3. Write `config.json` (schema: `references/config.md`).
4. Run `python3 <skill-dir>/scripts/build.py <project>/config.json`. Pillow is needed (`python3 -m pip install pillow`).
5. Fix every `WARN` about contrast (body text and button text need 4.5:1) by adjusting `ink`, `muted` or `onPrimary` – never by silently replacing brand colours. If a brand colour itself is too light for text, keep it for fills and tell the user.

### 4. Check

Serve `dist/` locally (`python3 -m http.server 8790 -d <project>/dist`) and open it at phone width (375 px) if you have a browser tool. Check: setup screen (logo, title, presets, language switch), start an exercise and look at inhale and exhale, finish screen, and the icons in `dist/`. Show the user a screenshot of the setup and the exercise screen.

Testing aids: `?speed=10` in the URL runs the exercise ten times faster (to reach the finish screen quickly). If the browser pane is hidden, `requestAnimationFrame` may not tick – override it via JS: `window.requestAnimationFrame = cb => setTimeout(() => cb(performance.now()), 16)`. Wait ~0.5 s after switching screens before a screenshot (fade-in). Home screen install, icon and offline mode can't be verified reliably on localhost – say they're checked once it's hosted. Without a browser tool, at least open the generated icon PNGs and say that you couldn't view the page.

### 5. Hand over

Tell the user, briefly:
- where the `dist/` folder is and that it's the thing to upload;
- the hosting options from `references/hosting.md` – recommend the simplest for them (no own website → Netlify Drop; own website → a subfolder like `/atem/` via their usual upload);
- that after uploading they open the link once on their phone to test, then send the link to clients;
- the ready-to-forward text for clients from `references/homescreen-guide.md`, in the client's language and form of address, with the link placeholder.

Offer to change anything (colours, animation, rhythm, texts) – a change is just an edit to `config.json` and a rebuild. After a rebuild, the files must be uploaded again; installed home screen apps pick up the new version on the next start with network.

## Rules

- No tracking, analytics, external requests, CDN scripts or web fonts loaded at runtime. Everything is inlined. Keep it that way when adding custom CSS or HTML.
- Don't change the breathing logic or add health claims. The app is a pacer, not a medical device. Don't promise effects in texts you write.
- Rhythm limits: inhale and exhale at least 1 s, each phase at most 20 s, session 1–30 min.
- Typical `customCss` touches: `.titel b { font-style: italic; }` (brand emphasises with italics), `.btn-dark { background: var(--primary); }` (Pause button in brand colour), letter-spacing of `.titel`.
- Don't edit `assets/template.html` per client. Brand-specific styling goes in `customCss`; if the template really lacks something, tell the user it's a change to the skill itself.
