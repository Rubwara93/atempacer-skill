# Atempacer-Skill – Entwurf (13.10.2026)

Ziel: Ein öffentlicher Skill (Claude Code, Codex), mit dem Rubens Community für ihre Kunden Atempacer im jeweiligen Corporate Design baut.

Entscheidungen (Ruben, 13.10.2026)
- Name `atempacer`, Repo `Rubwara93/atempacer-skill`, MIT.
- SKILL.md auf Englisch, der Skill spricht in der Sprache der Nutzerin; README Deutsch mit englischer Zusammenfassung.
- Darstellungen: Kreis, Blume, Welle, Quadrat (ohne Haltephasen als Linie).
- Standard-Rhythmus 4/6, änderbar; Sprachen de-sie, de-du, en mitgeliefert, weitere übersetzt der Agent; Umschalter ab zwei Sprachen.
- Auslieferung: möglichst einfach. Eine HTML-Datei, die allein läuft, plus Icons, Manifest und Service Worker im selben Ordner, damit „Zum Home-Bildschirm“ mit Icon und offline funktioniert. Grund: Auf ein eingebettetes (data-URI) apple-touch-icon ist bei iOS kein Verlass, und eine per Mail geöffnete HTML-Datei läuft auf dem iPhone nicht.
- Basis: Uni-Leipzig-Fassung (Vanilla JS) statt Claude-Design-Bundle.

Aufbau: `assets/template.html` mit Platzhaltern, `scripts/build.py` (config.json → dist/), `scripts/fetch_font.py`, Referenzen zu Konfiguration, CD-Erkennung, Hosting und Kundentext.

Video (LinkedIn): Installation in Claude Code und Codex, Individualisierung am Beispiel Resilienz Initiative, Homescreen auf dem iPhone mit Icon.
