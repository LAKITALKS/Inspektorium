# INSPEKTORIUM v0.1.1: Gegenprobe zum Review-Export 5ee4f40

Erstellt am 14.10.2026 von Claude als unabhängige Gegenprobe zum Paket
`inspektorium-v0.1.1-review-5ee4f40.zip`. Dabei gab es keine Änderung am Repository,
keinen Commit, keinen Push und keinen Modellaufruf. Alle Läufe fanden offline statt;
die CLI-Läufe und Tests liefen mit `unshare -n` ohne Netz.

## Geprüfter Stand

- ZIP-SHA-256 `50189b54…69507cf`, wie angegeben. 420 von 420 Manifest-Einträgen sind bytegleich.
- `4bd0ba9` (öffentlicher main, eigener Klon) plus `review/CHANGESET.patch` ergibt `repo/` exakt
  (`diff -r` leer).
- Das Produkt wurde aus `repo/` installiert. Dessen Produktdateien entsprechen `fae1824`.

## Umgebung

- Python 3.11.17 (Unicode 14.0.0) für Produkt und CLI. Testsuite zusätzlich auf Python 3.13.
- Chromium 141.0.7390.37 über Playwright 1.56.0, Linux. Die Evidence-Läufe nutzten Chromium 153 auf macOS.
- Renderer: cmarkgfm 2025.10.22 im Safe-Modus mit derselben Seitenvorlage wie
  `evidence/v0.1.1/tools/renderers.py`, markdown-it-py 4.2.0, Python-Markdown 3.11.
- Schriften, je Messreihe:
  1. Linux-Standard, also Liberation Serif;
  2. Noto Serif/Sans 2.015 (fontversion 132055) als Standardschrift über
     `scripts/fontconfig-noto-default.conf`; Noto Sans ist die Linux-Schrift im GitHub-CSS;
  3. GitHub-artiges CSS: Noto Sans, 16 px, line-height 1.5.

## Ergebnisse

### Grundprüfung

| Prüfung | Ergebnis |
|---|---|
| Testsuite | 1123 passed auf 3.11 und 3.13, Branch-Coverage 98 %, Import aus site-packages |
| Beispiele | 10/10 bytegleich mit `expected_report.*`; Eingaben und JSON gleich `4bd0ba9` |

### Alte Angriffe vom 12.10. (`scripts/old_probes.py`)

| Angriff | Ergebnis |
|---|---|
| C1 (Zeilen-Fälschung, `<!--` verschluckt Warnungen) | behoben: alle vier h2-Abschnitte vorhanden, keine HTML-Tokens |
| C5 (rohes Bidi) | behoben |
| C4 an der CLI | behoben: Exit 2, `--output` bleibt unberührt |
| C4 über die Bibliotheks-API `model_validate_json` | weiter last-wins, dokumentiert |
| A1–A7 (Semantik) | unverändert, dokumentiert als P09/P14/P15 |
| B1 (Offsets) | unverändert, dokumentiert als P17 |
| C2 und C3 (Fälschung, Herkunft) | unverändert, dokumentiert als P16 |
| Label „Citation-validated“ | entfernt |

### 1. Kombinationszeichen (Überdeckung)

`scripts/gen_cases.py` erzeugt 75 Berichte, alle über die echte CLI (`inspect --input --proposals`):
- Grundlage ist Beispiel 05 mit einem echten Fehlschlag (claim-2).
- Es gibt fünf Kanäle: Begründung über bzw. unter dem Fehlschlag, letzte Begründung über den
  Warnungen, die geprüfte Antwort selbst (claim_text) und das Quellenzitat.
- Je Kanal werden n = 0 bis 80 Zeichen pro Buchstabe getestet; n = 0 ist der Zwilling ohne Zeichen.

`scripts/shoot.py` misst danach pro Host-Zeile die zusätzliche Tinte gegenüber dem Zwilling,
jeweils in der Textbox dieser Zeile. Als Rauschschwelle gelten 10 px.

| Setup | Fälle mit überdeckten Host-Zeilen | Erstes n | DOM-Checks |
|---|---|---|---|
| fae1824, Noto als Standardschrift | 39/75 | 6 (Antwortkanal 8; Warnungen 24) | alle bestanden |
| fae1824, GitHub-artiges CSS | 36/75 | 6–10 (Warnungen 32) | alle bestanden |
| fae1824, Linux-Standardschrift | 0/75 (max. 2 px Rauschen) | – | alle bestanden |
| Prototyp „max. 4 Zeichen“ (Noto bzw. GitHub-artig) | 0/75 bzw. 0/75 | – | alle bestanden |

Erste Treffer auf Fehlschlag-Zeilen (Noto):
- „Reportable … None — deterministic guard failed“ ab n = 24, also 582 Zeichen im Antwortkanal;
- „Deterministic guard: failed“ ab n = 32, also 766 Zeichen;
- die Warnzeile `claim-2 / evidence_span_mismatch` ab n = 24, also 932 Zeichen.

V1s manipulierter Bericht (mk2/warnings2.png) lässt sich regulär erzeugen. `scripts/mk2_via_cli.py`
schreibt die mk2-Nutzlast in `proposals.json` und lässt die CLI bei fae1824 laufen. Das Ergebnis:
- Das Markdown ist bytegleich zu render_markdown(mk2-Bericht) bei fae1824.
- Gegenüber V1s report2.md (7c9d438) ändert sich nur der Absatz mit der Display-Note.
- Ob die Zeichen hoch stapeln, hängt von der Schrift ab. Mit V1s macOS-Schrift stapeln sie; mit Noto
  bilden genau diese Unterstriche einen einzigen Balken, andere Zeichen dagegen stapeln (Screenshots 01–03).

`screenshots/03`: V1-ZG-R bei fae1824 reproduziert die Überdeckung aus V1s zalgo.png (7c9d438);
checkVisibility meldet dabei 50/50.

### 2. E-Mail-Autolinks

Schon eine gewöhnliche Antwort mit einer Adresse (`results/cli_cases/email`) erzeugt in cmark-gfm,
im Safe- und im Unsafe-Modus, drei `mailto:`-Links: in der Behauptung, in der Begründung und im Zitat.
markdown-it und Python-Markdown erzeugen keinen Link.

Der Katalog 1.0 enthält in keinem der 70 Fälle ein `@`.

Getestete Alternativen: `@` als Codespan (`` `@` ``) oder als Marker `⟦U+0040⟧` erzeugt in allen
drei Renderer-Familien 0 Links.

### 3. Ähnliche Klammern

Neben U+301A/B gehen acht weitere Paare roh durch (`screenshots/06`): U+27EC/D, 2E28/9, 3016/7,
FF3B/FF3D, 2045/6, 298B/C, 27E8/9, 2E26/7. Am ähnlichsten sieht 〚〛 aus. Eine strukturelle
Wirkung hat keine dieser Klammern.

## Prototyp (nur zur Bemessung)

`prototype_nur_zur_bemessung/display.py.cap4.diff` umfasst 16 Zeilen. Es zeigt das fünfte und jedes
weitere aufeinanderfolgende Mn/Me-Zeichen als Marker.

- Bestehende Tests: 1123/1123 bestanden.
- Beispiele: unverändert.
- Überdeckung: 0/75.

Der Prototyp ist kein Patch zum Einspielen; er belegt nur, dass die Korrektur eng begrenzt sein kann.

## Nachfahren

```bash
python -I scripts/old_probes.py <repo>
python -I scripts/gen_cases.py <repo> <out> <inspektorium-exe>     # Produkt-venv
FONTCONFIG: scripts/fontconfig-noto-default.conf nach ~/.config/fontconfig/fonts.conf, fc-cache -f
python -I scripts/shoot.py <out> _noto                              # Tools-venv mit Playwright
EXTRA_HEAD='<style>body{font-family:"Noto Sans";font-size:16px;line-height:1.5}</style>' python -I scripts/shoot.py <out> _ghlike
python -I scripts/mk2_via_cli.py <display_limits/1_combining_marks/tampered_report_mk2> <out> <inspektorium-exe>
```
