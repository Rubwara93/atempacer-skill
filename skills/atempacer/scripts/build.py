#!/usr/bin/env python3
"""Build a branded breath pacer from a config.json.

Usage:  python3 build.py path/to/config.json

Writes <config dir>/<output>/ with:
  index.html            the whole app in one file (fonts, logo, texts inlined)
  apple-touch-icon.png  home screen icon for iPhone/iPad (180 px)
  icon-192.png, icon-512.png, icon-maskable-512.png   Android / desktop install
  manifest.webmanifest  install metadata
  sw.js                 offline cache, so the home screen app also opens without network

Needs Python 3.8+ and Pillow (pip install pillow).
"""
import base64
import hashlib
import io
import json
import math
import mimetypes
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    sys.exit("Pillow fehlt / Pillow missing: python3 -m pip install pillow")

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"

BUILTIN_PRESETS = {
    "calm":      {"in": 4, "h1": 0, "out": 6, "h2": 0},
    "coherence": {"in": 5, "h1": 0, "out": 5, "h2": 0},
    "box":       {"in": 4, "h1": 4, "out": 4, "h2": 4},
    "478":       {"in": 4, "h1": 7, "out": 8, "h2": 0},
    "energize":  {"in": 4, "h1": 0, "out": 2, "h2": 0},
}
VISUALS = ("circle", "flower", "wave", "square")
DEFAULT_FONT = {
    "family": "Roboto",
    "fallback": "'Helvetica Neue', Helvetica, Arial, sans-serif",
    "faces": [{"weight": w, "file": str(ASSETS / "fonts" / f"roboto-{w}.woff2")} for w in (300, 400, 500)],
}

warnings = []


# ---------- colour helpers ----------
def hex_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"not a hex colour: {h}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_hex(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in c)


def mix(a, b, t):
    """t=0 → a, t=1 → b"""
    ra, rb = hex_rgb(a), hex_rgb(b)
    return rgb_hex([ra[i] + (rb[i] - ra[i]) * t for i in range(3)])


def lum(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = hex_rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check(name, fg, bg, need):
    c = contrast(fg, bg)
    if c < need:
        warnings.append(f"Kontrast/contrast {name}: {c:.2f}:1 (< {need}:1) – {fg} auf/on {bg}")


# ---------- config ----------
def load(cfg_path):
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base = cfg_path.parent

    def p(rel):
        q = Path(rel).expanduser()
        return q if q.is_absolute() else base / q

    langs = cfg.get("languages") or ["de-sie"]
    i18n = {}
    for lang in langs:
        for cand in (base / "i18n" / f"{lang}.json", ASSETS / "i18n" / f"{lang}.json"):
            if cand.exists():
                i18n[lang] = json.loads(cand.read_text(encoding="utf-8"))
                break
        else:
            sys.exit(f"Sprachdatei fehlt / missing language file: i18n/{lang}.json")
    ref = json.loads((ASSETS / "i18n" / "en.json").read_text(encoding="utf-8"))
    for lang, d in i18n.items():
        missing = sorted(set(ref) - set(d))
        if missing:
            sys.exit(f"{lang}.json: fehlende Schlüssel / missing keys: {', '.join(missing)}")
        overrides = (cfg.get("texts") or {}).get(lang) or {}
        d.update(overrides)

    visual = cfg.get("visual", "circle")
    if visual not in VISUALS:
        sys.exit(f"visual muss eins sein von / must be one of: {', '.join(VISUALS)}")

    presets = []
    for item in cfg.get("presets") or ["calm", "coherence", "box", "478"]:
        if isinstance(item, str):
            if item not in BUILTIN_PRESETS:
                sys.exit(f"Unbekanntes Preset / unknown preset: {item}")
            presets.append({"id": item, **BUILTIN_PRESETS[item]})
        else:
            pr = {"id": item["id"], "name": item.get("name")}
            for k in ("in", "h1", "out", "h2"):
                pr[k] = float(item.get(k, 0))
            if pr["in"] < 1 or pr["out"] < 1:
                sys.exit(f"Preset {pr['id']}: in/out mindestens 1 s / at least 1 s")
            presets.append(pr)
    default = cfg.get("defaultPreset") or presets[0]["id"]
    if default not in [x["id"] for x in presets]:
        sys.exit(f"defaultPreset {default} steht nicht in presets / not in presets")

    col = cfg.get("colors") or {}
    primary = col.get("primary", "#2f6f8f")
    bg = col.get("background", "#ffffff")
    ink = col.get("ink", "#1d232b")
    colors = {
        "primary": primary,
        "secondary": col.get("secondary", mix(primary, ink, 0.35)),
        "background": bg,
        "surface": col.get("surface", bg),
        "ink": ink,
        "muted": col.get("muted", mix(ink, bg, 0.32)),
        "line": col.get("line", mix(ink, bg, 0.84)),
        "onPrimary": col.get("onPrimary", "#ffffff" if contrast("#ffffff", primary) >= contrast(ink, primary) else ink),
    }
    colors["inhale"] = col.get("inhale", colors["primary"])
    colors["exhale"] = col.get("exhale", colors["secondary"])
    colors["hold"] = col.get("hold", mix(ink, bg, 0.55))
    for k, v in colors.items():
        hex_rgb(v)

    check("Text/Hintergrund (ink/background)", colors["ink"], bg, 4.5)
    check("Nebentext (muted/background)", colors["muted"], bg, 4.5)
    check("Button-Text (onPrimary/primary)", colors["onPrimary"], colors["primary"], 4.5)
    for ph in ("inhale", "exhale"):
        fill = colors[ph]
        best = max(contrast("#ffffff", fill), contrast(ink, fill))
        if visual == "circle" and best < 3:
            warnings.append(f"Kontrast/contrast Phasentext im Kreis / phase text in circle ({ph} {fill}): max {best:.2f}:1 (< 3:1) – dunklere Phasenfarbe wählen / pick a darker colors.{ph}")

    return cfg, base, p, langs, i18n, visual, presets, default, colors


# ---------- fonts ----------
def font_css(spec, p, role):
    if not spec:
        return ""
    out = []
    for f in spec.get("faces", []):
        fp = p(f["file"]) if not Path(f["file"]).is_absolute() else Path(f["file"])
        data = base64.b64encode(fp.read_bytes()).decode()
        fmt = {"woff2": "woff2", "woff": "woff", "ttf": "truetype", "otf": "opentype"}[fp.suffix.lstrip(".").lower()]
        mime = {"woff2": "font/woff2", "woff": "font/woff", "truetype": "font/ttf", "opentype": "font/otf"}[fmt]
        rng = f"  unicode-range: {f['unicodeRange']};\n" if f.get("unicodeRange") else ""
        out.append(
            "@font-face {\n"
            f"  font-family: '{spec['family']}'; font-weight: {f.get('weight', 400)}; font-style: {f.get('style', 'normal')}; font-display: swap;\n"
            f"  src: url(data:{mime};base64,{data}) format('{fmt}');\n{rng}}}"
        )
    return "\n".join(out)


def font_stack(spec):
    if not spec:
        return "system-ui, -apple-system, 'Segoe UI', sans-serif"
    return f"'{spec['family']}', {spec.get('fallback', 'system-ui, sans-serif')}"


# ---------- logo ----------
def html_attr(v):
    return str(v).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def logo_html(cfg, p):
    lg = cfg.get("logo")
    if not lg or not lg.get("file"):
        return '<span class="logo" aria-hidden="true"></span>'
    fp = p(lg["file"])
    alt = lg.get("alt") or cfg.get("company", "")
    inner = ""
    if fp.suffix.lower() == ".svg":
        svg = fp.read_text(encoding="utf-8")
        svg = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>|<!--.*?-->", "", svg, flags=re.S)
        svg = re.sub(r">\s+<", "><", svg).strip()
        # Scripts and event handlers have no place in a logo
        svg = re.sub(r"<script\b.*?</script>", "", svg, flags=re.S | re.I)
        svg = re.sub(r"\son\w+\s*=\s*(\"[^\"]*\"|'[^']*')", "", svg, flags=re.I)
        svg = re.sub(r"(<svg\b[^>]*?)\s(width|height)=\"[^\"]*\"", r"\1", svg, count=1)
        svg = re.sub(r"(<svg\b[^>]*?)\s(width|height)=\"[^\"]*\"", r"\1", svg, count=1)
        svg = re.sub(r"<foreignObject\b.*?</foreignObject>", "", svg, flags=re.S | re.I)
        svg = re.sub(r"(href\s*=\s*[\"'])\s*javascript:[^\"']*", r"\1#", svg, flags=re.I)
        inner = re.sub(r"<svg\b", f'<svg role="img" aria-label="{html_attr(alt)}"', svg, count=1)
    else:
        mime = mimetypes.guess_type(fp.name)[0] or "image/png"
        data = base64.b64encode(fp.read_bytes()).decode()
        inner = f'<img src="data:{mime};base64,{data}" alt="{html_attr(alt)}">'
    href = lg.get("href")
    if href:
        if not re.match(r"https?://", href):
            sys.exit("logo.href muss mit http(s):// beginnen / must start with http(s)://")
        return f'<a class="logo" href="{html_attr(href)}" target="_blank" rel="noopener" aria-label="{html_attr(alt)}">{inner}</a>'
    return f'<span class="logo">{inner}</span>'


# ---------- icons ----------
def draw_motif(visual, size, fg, accent, safe):
    """Draw the chosen visual as a simple symbol on a transparent layer."""
    S = size
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = S / 2
    R = S * safe / 2  # radius of the usable area
    fg_rgb, ac_rgb = hex_rgb(fg), hex_rgb(accent)
    if visual == "circle":
        w = max(2, int(R * 0.07))
        d.ellipse([c - R * 0.92, c - R * 0.92, c + R * 0.92, c + R * 0.92], outline=fg_rgb + (110,), width=w)
        r = R * 0.66
        d.ellipse([c - r, c - r, c + r, c + r], fill=fg_rgb + (255,))
        r2 = r * 0.62
        inner = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(inner).ellipse([c - r2, c - r2, c + r2, c + r2], fill=ac_rgb + (70,))
        layer = Image.alpha_composite(layer, inner)
        d = ImageDraw.Draw(layer)
    elif visual == "flower":
        for i in range(8):
            petal = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            pd = ImageDraw.Draw(petal)
            rx, ry, off = R * 0.26, R * 0.5, R * 0.42
            pd.ellipse([c - rx, c - off - ry, c + rx, c - off + ry], fill=fg_rgb + (150 if i % 2 == 0 else 105,))
            layer = Image.alpha_composite(layer, petal.rotate(i * 45, resample=Image.BICUBIC, center=(c, c)))
        d = ImageDraw.Draw(layer)
        r = R * 0.2
        d.ellipse([c - r, c - r, c + r, c + r], fill=fg_rgb + (255,))
    elif visual == "wave":
        w = max(3, int(R * 0.12))
        x0, x1, y0, y1 = c - R * 0.92, c + R * 0.92, c + R * 0.42, c - R * 0.42
        pts = []
        for i in range(201):
            u = i / 200
            lvl = 0.5 - 0.5 * math.cos(math.pi * u / 0.4) if u < 0.4 else 0.5 + 0.5 * math.cos(math.pi * (u - 0.4) / 0.6)
            pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * lvl))
        for i in range(len(pts) - 1):  # stamp round dots along the curve: clean edges at any width
            (xa, ya), (xb, yb) = pts[i], pts[i + 1]
            for k in range(4):
                x, y = xa + (xb - xa) * k / 4, ya + (yb - ya) * k / 4
                d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=fg_rgb + (255,))
        px, py = pts[80]
        r = R * 0.17
        d.ellipse([px - r * 1.7, py - r * 1.7, px + r * 1.7, py + r * 1.7], fill=fg_rgb + (70,))
        d.ellipse([px - r, py - r, px + r, py + r], fill=fg_rgb + (255,))
    else:  # square
        w = max(3, int(R * 0.1))
        a = R * 0.66
        d.rounded_rectangle([c - a, c - a, c + a, c + a], radius=w, outline=fg_rgb + (120,), width=w)
        d.line([(c - a + w / 2, c + a), (c - a + w / 2, c - a)], fill=fg_rgb + (255,), width=w)
        r = R * 0.17
        x, y = c - a + w / 2, c - a + w / 2
        d.ellipse([x - r * 1.7, y - r * 1.7, x + r * 1.7, y + r * 1.7], fill=fg_rgb + (70,))
        d.ellipse([x - r, y - r, x + r, y + r], fill=fg_rgb + (255,))
    return layer


def make_icon(size, visual, bg, fg, accent, safe, logo_img=None, round_corners=False):
    big = 1024
    img = Image.new("RGBA", (big, big), hex_rgb(bg) + (255,))
    if logo_img is not None:
        box = int(big * safe)
        f = box / max(logo_img.width, logo_img.height)
        lg = logo_img.resize((max(1, round(logo_img.width * f)), max(1, round(logo_img.height * f))), Image.LANCZOS)
        img.alpha_composite(lg, ((big - lg.width) // 2, (big - lg.height) // 2))
    else:
        img = Image.alpha_composite(img, draw_motif(visual, big, fg, accent, safe))
    if round_corners:
        mask = Image.new("L", (big, big), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, big - 1, big - 1], radius=int(big * 0.22), fill=255)
        img.putalpha(mask)
    return img.resize((size, size), Image.LANCZOS)


def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


# ---------- main ----------
def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cfg_path = Path(sys.argv[1]).expanduser().resolve()
    cfg, base, p, langs, i18n, visual, presets, default, colors = load(cfg_path)
    out = p(cfg.get("output", "dist"))
    out.mkdir(parents=True, exist_ok=True)

    first = i18n[langs[0]]
    app_name = cfg.get("appName") or {}
    if isinstance(app_name, str):
        app_name = {l: app_name for l in langs}
    for l in langs:
        app_name.setdefault(l, i18n[l]["appName"])
    company = cfg.get("company", "")
    name0 = app_name[langs[0]]
    short_name = cfg.get("shortName") or name0
    title = f"{name0} – {company}" if company else name0
    description = cfg.get("description") or first["intro_" + visual]

    fonts = cfg.get("fonts") or {}
    body = fonts.get("body") or DEFAULT_FONT
    display = fonts.get("display") or body
    faces = font_css(body, p, "body")
    if display is not body and display.get("family") != body.get("family"):
        faces += "\n" + font_css(display, p, "display")

    radius = float(cfg.get("radius", 0))
    css_vars = {
        "--primary": colors["primary"],
        "--primary-text": colors["primary"] if contrast(colors["primary"], colors["background"]) >= 3 else colors["ink"],
        "--primary-soft": mix(colors["primary"], colors["background"], 0.82),
        "--secondary": colors["secondary"],
        "--on-primary": colors["onPrimary"],
        "--bg": colors["background"],
        "--surface": colors["surface"],
        "--surface-2": mix(colors["ink"], colors["background"], 0.93),
        "--ink": colors["ink"],
        "--muted": colors["muted"],
        "--line": colors["line"],
        "--font-body": font_stack(body),
        "--font-display": font_stack(display),
        "--display-weight": str(display.get("weight", 300)),
        "--radius": f"{radius:g}px",
        "--radius-s": f"{min(radius, 4):g}px",
        "--radius-btn": f"{float(cfg.get('buttonRadius', radius)):g}px",
        "--logo-h": f"{float((cfg.get('logo') or {}).get('height', 48)):g}px",
    }
    css_vars_txt = "\n".join(f"  {k}: {v};" for k, v in css_vars.items())

    custom_css = cfg.get("customCss", "")
    if cfg.get("customCssFile"):
        custom_css += "\n" + p(cfg["customCssFile"]).read_text(encoding="utf-8")
    decor = cfg.get("decorHtml", "")
    if cfg.get("decorHtmlFile"):
        decor += p(cfg["decorHtmlFile"]).read_text(encoding="utf-8")

    # icons
    ic = cfg.get("icon") or {}
    icon_bg = ic.get("background", colors["primary"])
    icon_fg = ic.get("foreground", colors["onPrimary"])
    icon_accent = ic.get("accent", colors["secondary"])
    logo_img = None
    if ic.get("logo"):
        lp = p(ic["logo"])
        if lp.suffix.lower() == ".svg":
            sys.exit("icon.logo braucht PNG/JPG (SVG vorher umwandeln) / icon.logo needs PNG or JPG")
        logo_img = Image.open(lp).convert("RGBA")
        if max(logo_img.size) < 512:
            warnings.append(f"icon.logo ist klein / is small ({logo_img.width}×{logo_img.height}px) – das Icon kann unscharf werden / icon may look blurry; 1024 px empfohlen / recommended")
    safe = float(ic.get("safe", 0.72))
    icons = {
        "apple-touch-icon.png": make_icon(180, visual, icon_bg, icon_fg, icon_accent, safe, logo_img),
        "icon-192.png": make_icon(192, visual, icon_bg, icon_fg, icon_accent, safe, logo_img),
        "icon-512.png": make_icon(512, visual, icon_bg, icon_fg, icon_accent, safe, logo_img),
        "icon-maskable-512.png": make_icon(512, visual, icon_bg, icon_fg, icon_accent, min(safe, 0.6), logo_img),
    }
    for fn, img in icons.items():
        (out / fn).write_bytes(png_bytes(img))
    fav = make_icon(64, visual, icon_bg, icon_fg, icon_accent, safe, logo_img, round_corners=True)
    favicon_data = "data:image/png;base64," + base64.b64encode(png_bytes(fav)).decode()

    js_cfg = {
        "storageKey": cfg.get("storageKey") or "atempacer-" + re.sub(r"[^a-z0-9]+", "-", (company or name0).lower()).strip("-"),
        "visual": visual,
        "presets": presets,
        "defaultPreset": default,
        "duration": int(cfg.get("duration", 300)),
        "appName": app_name,
        "titleHighlight": cfg.get("titleHighlight"),
        "colors": {k: colors[k] for k in ("inhale", "exhale", "hold", "ink", "line")},
    }

    def js(obj):
        return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

    html = (ASSETS / "template.html").read_text(encoding="utf-8")
    esc = lambda s: s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    repl = {
        "{{LANG}}": langs[0][:2],
        "{{THEME_COLOR}}": colors["background"],
        "{{SHORT_NAME}}": esc(short_name),
        "{{DESCRIPTION}}": esc(description),
        "{{TITLE}}": esc(title),
        "{{FAVICON_DATA}}": favicon_data,
        "{{FONT_FACES}}": faces,
        "{{CSS_VARS}}": css_vars_txt,
        "{{CUSTOM_CSS}}": custom_css,
        "{{DECOR_HTML}}": decor,
        "{{LOGO_HTML}}": logo_html(cfg, p),
        "{{CONFIG_JSON}}": js(js_cfg),
        "{{I18N_JSON}}": js({l: i18n[l] for l in langs}),
    }
    for k, v in repl.items():
        html = html.replace(k, v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if left:
        sys.exit(f"Platzhalter übrig / placeholders left: {left}")
    (out / "index.html").write_text(html, encoding="utf-8")

    manifest = {
        "name": title,
        "short_name": short_name,
        "description": description,
        "lang": langs[0][:2],
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": colors["background"],
        "theme_color": colors["background"],
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    (out / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    files = ["./", "index.html", "manifest.webmanifest", *icons.keys()]
    h = hashlib.sha256()
    for fn in ["index.html", *icons.keys()]:
        h.update((out / fn).read_bytes())
    sw = (ASSETS / "sw.js").read_text(encoding="utf-8")
    sw = sw.replace("{{CACHE}}", "atempacer-" + h.hexdigest()[:10]).replace("{{FILES}}", json.dumps(files))
    (out / "sw.js").write_text(sw, encoding="utf-8")

    size = (out / "index.html").stat().st_size / 1024
    print(f"OK  {out}")
    print(f"    index.html {size:.0f} KB · {visual} · {', '.join(langs)} · Standard/default {default}")
    for w in warnings:
        print("WARN", w)


if __name__ == "__main__":
    main()
