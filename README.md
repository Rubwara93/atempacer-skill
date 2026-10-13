# Atempacer-Skill

Ein Skill für Claude Code und Codex, der einen Atempacer im Corporate Design einer Firma baut. Gedacht für Coaches, Trainerinnen und Berater, die ihren Kunden eine Atemübung mitgeben wollen, die aussieht wie deren eigene App.

Der Skill fragt nach Logo, Farben und Schrift (oder liest sie von der Website), dann nach den Anpassungen:

- Darstellung: Kreis, Blume, Welle oder Quadrat
- Standard-Rhythmus: 4 Sekunden ein, 6 aus (voreingestellt), 5/5, Box 4-4-4-4, 4-7-8 oder ein eigener
- Sprachen: Deutsch mit Sie oder du, Englisch und jede weitere Sprache, die der Agent übersetzt; ab zwei Sprachen gibt es einen Umschalter in der App
- Übungen, Dauer, App-Name

Heraus kommt ein Ordner mit einer einzigen HTML-Datei, in der alles steckt (Schrift, Logo, Texte), dazu Homescreen-Icons, ein Web-App-Manifest und ein Service Worker für den Offline-Betrieb. Die App überträgt keine Daten, hat kein Tracking und lädt nichts nach.

## Installation

**Claude Code**, als Plugin:

```
/plugin marketplace add Rubwara93/atempacer-skill
/plugin install atempacer@atempacer
```

**Codex CLI**: den Ordner `skills/atempacer` nach `~/.codex/skills/` kopieren.

```bash
git clone https://github.com/Rubwara93/atempacer-skill.git && cp -r atempacer-skill/skills/atempacer ~/.codex/skills/
```

**Andere Agenten**, die das Agent-Skills-Format lesen (Cursor, Gemini CLI und andere):

```bash
npx skills@latest add Rubwara93/atempacer-skill
```

Oder von Hand nach `~/.claude/skills/` kopieren:

```bash
git clone https://github.com/Rubwara93/atempacer-skill.git && cp -r atempacer-skill/skills/atempacer ~/.claude/skills/
```

Voraussetzung ist Python 3 mit Pillow für die Icons (`python3 -m pip install pillow`). Der Skill weist darauf hin, wenn es fehlt.

## Benutzung

```
/atempacer Bitte baue einen Atempacer für die Muster AG, Website https://www.muster.de, Logo liegt unter ./logo.svg
```

In Codex: `$atempacer` oder „nutze den Skill atempacer“. Der Agent greift auch von selbst danach, wenn man ihn um einen Atempacer oder eine Atemübung im Firmendesign bittet.

## Aufs Handy bringen

Eine HTML-Datei, die per Mail, WhatsApp oder AirDrop auf ein iPhone kommt, öffnet sich in der Schnellvorschau. Dort laufen keine Skripte, und „Zum Home-Bildschirm“ gibt es nicht. Für das Icon auf dem Homescreen muss der Ordner deshalb einmal online liegen, zum Beispiel bei Netlify Drop (Ordner ins Browserfenster ziehen), GitHub Pages oder im eigenen Webspace unter `/atem/`. Den Link bekommen die Kunden. Sie öffnen ihn in Safari oder Chrome und tippen auf „Zum Home-Bildschirm“. Ab dem ersten Start funktioniert die App auch ohne Internet.

Auf Laptop und PC läuft die `index.html` auch ohne Hosting, einfach per Doppelklick.

Der Skill erklärt die Wege Schritt für Schritt und schreibt einen fertigen Text für die Kunden mit der Anleitung für iPhone und Android.

## Aufbau

```
skills/atempacer/
  SKILL.md                  Ablauf für den Agenten
  scripts/build.py          config.json → fertiger Ordner (HTML, Icons, Manifest, Service Worker)
  scripts/fetch_font.py     Google Font als woff2 herunterladen
  assets/template.html      die App (Vanilla JS, keine Abhängigkeiten)
  assets/i18n/              Texte: de-sie, de-du, en
  assets/fonts/             Roboto als Standardschrift
  references/               Konfiguration, CD von der Website lesen, Hosting, Kundentext
examples/demo/config.json   Beispiel
```

Ohne Agent geht es auch: `config.json` nach [references/config.md](skills/atempacer/references/config.md) schreiben und `python3 skills/atempacer/scripts/build.py pfad/zur/config.json` aufrufen.

## Hinweise

Der Atempacer gibt einen Rhythmus vor. Er ist kein Medizinprodukt und ersetzt keine Behandlung. Wer Atemübungen anleitet, sollte wissen, für wen lange Haltephasen ungeeignet sind.

Die mitgelieferte Schrift Roboto steht unter der Apache License 2.0. Google Fonts, die der Skill lädt, stehen unter der SIL Open Font License oder der Apache License und dürfen eingebettet werden. Kommerzielle Hausschriften nur mit Web-Lizenz der Firma.

Der Atempacer entstand bei der [Resilienz Initiative](https://www.resilienz-initiative.com). Den Skill hat [Ruben Langwara](https://www.rubenlangwara.de) gebaut.

## English summary

`atempacer` is an agent skill (Claude Code, Codex and other agents that read `SKILL.md`) that builds a breath pacer web app in a company's corporate design. It asks for logo, colours and fonts, or reads them from the company website, then lets you choose the animation (circle, flower, wave, square), the default rhythm (4 s in / 6 s out unless you pick another), the languages (German formal or informal, English, any other language the agent translates) and a few more settings. The output is a folder with one self-contained HTML file, home screen icons, a web app manifest and a service worker for offline use. No tracking, no external requests. To get the home screen icon on phones, upload the folder to any static host (Netlify Drop, GitHub Pages, your own webspace) and share the link; the skill walks you through it and writes the instructions for your clients. Install with `/plugin marketplace add Rubwara93/atempacer-skill` and `/plugin install atempacer@atempacer`, or copy `skills/atempacer` into `~/.claude/skills/` or `~/.codex/skills/`. MIT licence.
