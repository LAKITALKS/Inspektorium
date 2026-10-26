# Agent Arena — Umfang des internen technischen v1-Stands (v1.0.0)

> **Publication update — 2026-10-26:** technical research prerelease **1.0.1**
> is published with P1–P10 source. See [public scope and provenance](PUBLICATION.md).
> Historical closeout wording below refers to the original internal 1.0.0.
> The scientific Final v1 gate remains NOT MET. No new live run is authorized.

Stand 13.10.2026. Dieser Stand ist ein **begrenzter technischer Entwicklungsstand**. Er belegt weder wissenschaftliche
Treffsicherheit noch einen Vorteil gegenüber einem guten Einzelprompt.

Der interne v1-Stand führt definierte automatische Prüfungen aus und dokumentiert erkannte Konflikte und technische
Mängel. Nicht nachgewiesen ist, dass sämtliche relevanten Fehler erkannt werden.

Das v1.0-Freigabekriterium „Harness Efficacy Benchmark“ ([docs/v1_release_gates.md](docs/v1_release_gates.md), R1)
ist **nicht** erfüllt und bleibt eine eigene, gesondert zu beauftragende Aufgabe.

## Unterstützter Weg

- **Installation:** Python ≥ 3.11 in einer frischen Umgebung, `python -m pip install '.[dev,providers]'` (Details im
  [README](README.md)). Paket `agent-arena` 1.0.0.
- **Eingabe:**
  - Eine Task-Datei mit der zu prüfenden Aussage (`prompt`) und den vorgelegten Quellen (`context`).
  - Geprüft wird ausschließlich gegen diese vorgelegten Quellen; es gibt keine externe Suche.
  - Fälle mit Gold-, Kurator- oder Bibliotheksfeldern werden abgewiesen. Diese Prüfung ist feldbasiert: Kuratortext
    innerhalb von `context` erkennt sie nicht.
- **Ausführung:** ausschließlich `agent-arena audit`:
  - `audit validate` prüft die Eingabe.
  - `audit run` nimmt genau einen von drei Modi: `--offline` (aufgezeichnete Antwort), `--live` (nur mit gültiger
    AA-P10-LIVE-Autorisierung und Budget-Ledger) oder `--replay` (Nachspielen gespeicherter Live-Antworten ohne
    Modellaufruf).
  - Danach `audit inspect`, `audit review` und `audit release`.
- **Ausgabe:** ein unveränderliches Bündel aus `record.json`, `decision.json`, `report.md`, `report.html` und
  `manifest.json`.
  - `record.json` enthält die exakten Rohantworten.
  - Die Berichte zeigen Modellurteil, Host-Ableitung, wirksamen Zustand, Konflikte, Pflichtprüfungen und Kontrollen
    getrennt.
- **Nicht unterstützt:**
  - `agent-arena run` und `official-release` sind in v1 abgewiesen.
  - Alle anderen Befehle sind in der Hilfe als Alt- oder Diagnosewerkzeug markiert und erzeugen keine v1-Freigabe.
  - Direkt aufgerufene Python-Forschungsmodule wie `python -m agent_arena.run_library` sind keine v1-Einstiege. Sie
    können Provider ohne AA-P10-LIVE-Autorisierung aufrufen.

## Profile, Modi und tatsächliche Erprobung

- **Modi:** aufgezeichnet offline, live (Claude Haiku 5.5 `claude-haiku-5-5@3`, Claude Sonnet 5.5 `claude-sonnet-5-5@3`)
  und Replay.
- **Verträge:**
  - Bewertung AA-P8/1.3, Review AA-P9/1.3, Host-Regeln AA-P8-HOST/1.1.
  - Das Ausgabeformat der Modellantwort (Ledger AA-P8/1.0) und die Prompts (`…-contract-r2`) bleiben unverändert.
- **Live erprobt** wurde der Vorgängerstand `21a2849` (AA-P8/1.2, AA-P9/1.2):
  - 8 Aufrufe an drei **synthetischen Entwicklungsfällen**.
  - 5 von 6 Primäranalysen technisch vollständig.
  - Die P9-Gegenprüfung lief live nur bei Sonnet LR-03; bei Haiku wurde sie nicht ausgeübt.
  - Das ist kein Genauigkeitsmaß.
- **Der v1-Code selbst ist nicht live erprobt.** Er wurde offline und per Replay der gespeicherten Live-Antworten
  geprüft.
- **Budget:** Alle bisherigen Live-Autorisierungen sind geschlossen. Der verbleibende Spielraum unter den kumulativen
  Code-Obergrenzen würde Haiku-, aber keine Sonnet-Aufrufe decken. Ein neuer Live-Lauf braucht ohnehin einen neuen
  Auftrag.

## Bedeutung der Zustände

| Begriff | Bedeutung |
|---|---|
| **beendet** | Die automatische Bearbeitung ist abgeschlossen. Jede Revision sagt das ausdrücklich („Automatic processing has ended“). |
| **ungeklärt** | Beendet, aber nicht abschließend geklärt und **nicht fachlich freigegeben** (`REVIEW_REQUIRED` u. a.). Die Zeile „open cause“ nennt den Grund. |
| **technisch unvollständig** | Die Analyse konnte nicht vollständig an die Quellen gebunden werden (`ANALYSIS_INCOMPLETE`), etwa wegen falscher Textpositionen. Es lief kein Konflikt-Review; der Grund steht im Bericht. |
| **Pflichtprüfung nicht ausgeführt** | Ein materieller Konflikt verlangte ein Gegenreview, das nicht lief, etwa wegen Obergrenze, Budget oder fehlender Autorisierung. Der Fall bleibt gesperrt und wird nie automatisch freigegeben. |
| **freigegeben** (`RELEASED`) | Lokale Artefaktentscheidung nach bestandenen technischen Kontrollen und ausdrücklicher Freigabeabsicht. Keine fachliche, wissenschaftliche oder Kundenfreigabe. |

**Es gibt keine menschliche Begutachtung.** Die interne Kennung `HUMAN_REVIEW_REQUIRED` bedeutet im Betrieb ohne Prüfer
„automatisch nicht abschließend klärbar“. Eine Warteschlange oder ein Prüfer wird nicht vorausgesetzt.

Eine Revision ist unveränderlich. Nur eine aufgezeichnete menschliche Entscheidung (`audit review`) oder ein neuer,
ausdrücklich beauftragter Lauf erzeugt eine neue Revision.

## Was die Prüfungen sind — und was nicht

- **Host-Kontrollen** sind eine deterministische Verarbeitung von Feldern, die das Modell zum Teil selbst liefert.
  - Stimmen Modell und Host überein, ist das **keine** unabhängige wissenschaftliche Bestätigung.
  - Der Host ist kein Goldstandard.
- **Übersehene Informationen** innerhalb der vorgelegten Quellen bleiben möglich: Die Vollständigkeit der Extraktion
  wird nicht bewiesen.
- **Modelltext** wird in den Berichten als Daten dargestellt. Steuer-, Bidi- und unsichtbare Zeichen erscheinen als
  `⟦U+XXXX⟧`; `record.json` behält die exakten Zeichen.

## Bekannte Grenzen

- **Negative Kausalurteile:**
  - Modelle drücken „die Evidenz trägt die Kausalaussage nicht“ oft als Beobachtung `inconclusive` aus, und der Host
    leitet daraus `unknown` ab.
  - Korrekt verneinte Aussagen enden daher häufig als offener Pflichtkonflikt (live 2 von 3 technisch vollständigen
    verneinenden Antworten).
- **Textpositionen (Offsets):**
  - Ein um ein Zeichen verschobener Offset sperrt die ganze Analyse (fail-closed).
  - Drei solche Fälle unter 30 Primärantworten aus verschiedenen Revisionen sind **keine** belastbare allgemeine
    Fehlerrate.
  - Es gibt keine Toleranz und keine automatische Neupositionierung.
- **Konfliktgranularität:** Nach Reviews entstehen viele materielle Positionskonflikte, auch aus Darstellungsunterschieden
  (Sonnet LR-03: 24). Sie werden nicht automatisch aufgelöst.
- **Haiku-P9** ist live nicht nachgewiesen.
- **Formatierung** kann ein Ergebnis nur verschärfen, nie lockern:
  - ``` in einer Modellantwort führt zu ANALYSIS_INCOMPLETE.
  - Task-Dateien liest ein YAML-Lader: Ein rohes NEL (U+0085) wird zu einem Zeilenumbruch gefaltet
    (ANALYSIS_INCOMPLETE), und ein roher Zeilentrenner vor einer Zeile `---` führt zu PREFLIGHT_BLOCKED. Ohne diese
    Konstellation bleiben U+2028/U+2029 exakt erhalten.
  - Eine Task-Datei mit ASCII-maskierten Zeichen außerhalb der Basisebene (Surrogatpaare, z. B. U+1D6FC) besteht
    `audit validate`. `audit run` endet dann aber ohne Bündel mit RELEASE_BLOCKED, weil der YAML-Lader die Paare
    trennt.
- **Historische Bündel** sind nur mit ihrer erzeugenden Codebasis prüfbar: im passenden Checkout mit passenden
  Paketmetadaten. Unter v1-Code gelten sie bewusst als nicht verifizierbar; die Meldung nennt dann ein Symptom statt
  der Ursache.
- **Größere offene Punkte** (nicht erledigt):
  - P5: Lease-Bindung ohne Ablauf und Klon-Sicherheit.
  - P7: Die Evidenzrichtung hängt an der vom Modell vergebenen Rolle.
  - Die feldbasierte Eingabeprüfung.
  - Irreführende Meldungen bei Prüfung außerhalb eines Git-Checkouts (P10-F3/G2).
  - Liste: [PACKAGE_B_DIAGNOSIS.md](analysis/c25_p9_20261011/PACKAGE_B_DIAGNOSIS.md).

## Drei getrennte Aussagen

1. **Softwaretests:**
   - Saubere Reproduktion des getesteten Codecommits: volle Suite, P10-Abnahme 21/21 und Wheel-Tests bestanden.
   - Zahlen und Belege: [analysis/v1_closeout_20261013/CLOSEOUT.md](analysis/v1_closeout_20261013/CLOSEOUT.md).
2. **Technische Live-Erprobung:** 8 Aufrufe an drei synthetischen Fällen, mit dem Vorgängercode.
   - Die Folge 0/12 → 2/12 → 5/6 technisch vollständiger Läufe entstand unter geänderten Bedingungen und ist **kein**
     Wirksamkeitsvergleich.
3. **Wirksamkeit:** nicht nachgewiesen.
   - Keine Aussage „findet alle Fehler“, „wissenschaftlich validiert“ oder „unabhängiger Gutachter“.
   - Historischer Hinweis (Phase 5B, Sonnet S1): Korrigiert ist die Einstimmigkeit 82/84 statt 84/84; die
     Antwortgenauigkeit liegt je nach Lesart bei 350/418 oder 352/420. Die Originale bleiben unverändert; siehe den
     Nachtrag in PACKAGE_B_DIAGNOSIS.md.
