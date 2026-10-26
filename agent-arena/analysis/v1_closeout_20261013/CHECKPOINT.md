# Checkpoint — interner technischer v1-Abschluss (Auftrag vom 13.10.2026)

Nach einer Kompaktierung hier weiterlesen; abgeschlossene Schritte nicht erneut starten.

## Ausgangsstand (geprüft 13.10.2026)

- Repository `__LOCAL_HOME__/Documents/Projects/agent-arena`.
  - Branch `c25-p9-conflict/aa-p8-p9-20261011`, HEAD `558e920`.
  - Nichts gestaged, nur fremde unversionierte Dateien (bleiben unberührt).
  - Keine `AGENTS.md`/`CLAUDE.md`. Kein Tag `v1*`.
- Paketversion `agent-arena` 0.1.0 (`pyproject.toml`, `agent_arena.__version__`).
- Verträge AA-P8/1.2, AA-P9/1.2, Host AA-P8-HOST/1.1. Getesteter Produktcode `21a2849`. Seitdem nur Analyse und
  Dokumentation.
- Geschlossene Ledger -002/-003/-004 (REVOKED, Rest 0) und geschützte Evidenzbäume gehasht:
  [hashes_before.json](hashes_before.json).
- Vorhandene v1-Struktur: [docs/v1_release_gates.md](../../docs/v1_release_gates.md) friert als v1.0-Gate R1 einen
  Wirksamkeitsbenchmark ein. Dieser Auftrag ist ausdrücklich ein *technischer* v1-Abschluss ohne Wirksamkeitsnachweis;
  V1_SCOPE muss das abgrenzen und darf R1 nicht als erfüllt darstellen.
- Werkzeuge:
  - Google Chrome 154 und Node 26 sind lokal vorhanden; das Playwright-Modul fehlt (Installation nur isoliert).
  - Bestehende Render-QA: `scripts/phase10_render_qa.mjs`. Der Abnahmekorpus enthält `long_hostile_render`.

## Abnahmematrix A–D (vor Änderungen festgelegt)

| ID | Testfall | Erwartetes Verhalten | Evidenzpfad |
|---|---|---|---|
| A1 | Kanonischer Offline-Replay von Sonnet LR-02, Sonnet LR-03 und Haiku LR-03 aus Kopien der Aufnahmen | Gültiges, vollständig geschriebenes Bündel auch bei ungeklärtem Ergebnis; keine Behauptung vollständiger wissenschaftlicher Analyse | `analysis/v1_closeout_20261013/evidence/A/` |
| A2 | Ausgabe der drei Fälle (Record, Markdown, HTML) | Ursachen unterschieden: Pflichtreview nicht ausgeführt (Obergrenze) / Reviews ausgeführt, Konflikt offen / technisch unvollständig mit Grund. Hinweis „automatische Bearbeitung beendet, nicht automatisch geklärt, keine fachliche Freigabe“; keine menschliche Warteschlange vorausgesetzt | dito, Tests |
| A3 | Erhalt der Historie | Offene Konflikte, Pflichtprüfungen, Originalpositionen und tatsächlich ausgeführte Reviews bleiben im Replay-Bündel | dito |
| A4 | Testfreigabe der gesperrten Fälle | RELEASE_BLOCKED, keine fingierte menschliche Prüfung | dito, Tests |
| A5 | Wiederaufnahme desselben abgeschlossenen Laufs mit instrumentiertem Fake-Provider (synthetische Autorisierung, temporäres Verzeichnis); wiederholtes Inspect/Replay | 0 zusätzliche generierende Anfragen; Replay/Inspect ohne Modellgenerierung | Tests |
| A6 | Neu beauftragter Lauf desselben Inputs (neue synthetische Autorisierung, temporär) | Als neue Laufidentität möglich; keine ewige Sperre über Claimtext oder Fall-ID | Tests |
| B1 | Synthetisches Offline-Paar über die echte Materialitätslogik: nichtmaterieller Modell/Host-Konflikt | Konflikt sichtbar, offen, nichtmateriell, nicht aufgelöst; keine falsche Gegenprüfungs- oder Übereinstimmungsbehauptung; Freigabe allein dadurch nicht gesperrt; Record, Markdown und HTML stimmen überein | Tests, `evidence/B/` |
| B2 | Eng verwandter materieller Gegenfall ohne weitere Sperrgründe | Pflichtprüfung ausgelöst; Freigabe gesperrt | dito |
| C1 | `agent-arena run` (Altpfad) und kanonisches `audit run` offline mit Fake- bzw. aufgezeichnetem Provider | Erzeugte Artefakte; Verwechslungsgefahr mit P8–P10-Audit; Freigabestatus ohne Pflichtkontrollen möglich?; Hilfe und Dokumentation zeigen den unterstützten Befehl | Tests, `evidence/C/` |
| C2 | Ergebnis | Ein eindeutig dokumentierter kanonischer v1-Pfad; Alternativen abgewiesen oder sichtbar abgegrenzt, ohne irreführende v1-Freigabe | dito |
| D1 | Adversariale lokale Freitexte (Begründung, Claim, Zitat): Zeilenumbrüche mit Kontroll-Überschriften und fingierten „passed“-Zeilen, Codezäune, Backticks, Listen und Tabellen, HTML-Kommentare und -Tags, Bidi- und unsichtbare Steuerzeichen; dazu ein Bericht mit echter fehlgeschlagener Kontrolle | Host-Kontrollen, Status und Gründe sichtbar und richtig zugeordnet; Pflichtwarnungen erhalten; keine aktive Struktur aus Modelltext; Modelltext erkennbar; Freigabe unabhängig; Evidenz unverändert | Regressionstests, DOM-/Sichtbarkeitsprüfung, `evidence/D/` |

PASS-Kriterien wie im Auftrag §4–§7.

## Untersuchung A–D (13.10.2026)

Workflow mit acht Agenten (Opus 5.5): je ein Prüfer (high) und ein adversarialer Verifizierer (max) pro Bereich. Alles
offline, 0 Provider- und Netzversuche, keine Live-Session auf echten Autorisierungen, Repository nur gelesen.

Ein Nebeneffekt: Zwei Prüfer erzeugten zwei gitignorierte `__pycache__`-Dateien in `src/agent_arena/` neu. Keine
versionierte Datei hat sich geändert.

| Punkt | Befund vor Reparatur |
|---|---|
| A1, A3, A4, A5, A6 | PASS: Bündel gültig, Historie erhalten, Freigabe gesperrt, 0 neue Anfragen bei Wiederaufnahme, neue Laufidentität möglich |
| A2 | FAIL: keine Aussage „automatische Bearbeitung beendet“; Ursachen (i)/(ii) in Statuszeile, Konfliktzeile und CLI-JSON identisch; Fehlgründe lesen sich wie Erfolg (XT-F3); Haiku LR-03 zeigt „none recorded“ / „no recorded conflicts“ |
| B1 | Kern-PASS über die echte Materialitätslogik, aber falsche Texte: „no recorded conflicts“ (B-D1), P8-Text „mandatory review decides“ bei nichtmateriellem Konflikt (B-D2), „not reviewed“ nach Adjudikation (NEW-VB-2) |
| B2 | PASS |
| NEW-VB-1 (in B gefunden, MATERIAL, latent) | Eine Zusammenfassung mit `asserts_whole_claim` aus einer optionalen, konfliktbehafteten oder nicht gestützten Proposition wird als „supported“ freigegeben. In den echten Ledgern nicht aufgetreten. Irreführender Freigabepfad nach §8 des Auftrags |
| C | `agent-arena run` ist ein ungesicherter Live-Pfad ohne Autorisierung und Ledger und sendet keinen Kontext (C-D2, MATERIAL; P2-F2). `official-release` schreibt ein „official_release_authorized“-Paket ohne P8/P9/P10 (C-D1). Die Root-Hilfe nennt den v1-Pfad nicht (C-D4). `run_library` ist ein zweiter Forschungspfad |
| D | CR in Modelltext bricht aus Markdown-Tabellen aus und schmiedet Status- und Kontrollanzeigen in allen 8 geprüften CommonMark-Renderern (D1, MATERIAL). `markdown_qa` bestätigt das (D2). Bidi- und unsichtbare Zeichen bleiben unmarkiert und können Host-Text umdrehen (D3). Modell-IDs stehen in Host-Überschriften (D4). Modell-Schlüssel überschreiben Host-Felder (M1). Kanonisches HTML ist in allen Varianten sicher |

## Reparaturentscheidungen (Koordinator)

Spezifikation: Scratch `v1/IMPLEMENTATION_SPEC.md`, wird mit dem Abschluss archiviert.

| Stufe | Inhalt |
|---|---|
| P | Abgeleitete Ausgabe „automatic processing \| ended“ und „open cause“ sowie ein Satz zur beendeten automatischen Bearbeitung (A2); sprechende Fehlgründe für `analysis_source`, `phase8_semantics_taxonomy` und `phase9_history_review`; Konfliktzeile und Historiensatz korrigiert (B-D1, B-D2 nur in der Projektion, NEW-VB-2); Anzeige-Transformation ⟦U+XXXX⟧, CR-Entities und strengere `markdown_qa` (D1–D3); Ordnungszahl-Überschriften (D4); Schlüsselkollision (M1); Hinweis zu `reasons`. Registry: `analysis_source` 1.1, `phase9_history_review` 1.3, `markdown_qa`/`html_qa` 1.1 |
| C | `run` und `official-release` werden mit Verweis auf `audit` abgewiesen, die API bleibt; die Root-Hilfe nennt den v1-Pfad und markiert alle Altbefehle; cleandoc-Korrektur; `run_library` als Forschungspfad gekennzeichnet |
| S | NEW-VB-1 (P9-Materialität ohne Ausnahme für die Gesamtaussage; P8-Teil-zu-Ganz-Prüfung über die Quellpropositionen); AA-P8/1.3, AA-P9/1.3, `phase8_semantics_taxonomy` 1.3; Host-Regeln AA-P8-HOST/1.1 und Ausgabeformat unverändert; Live-Preflight bei geteiltem Review-Zustand (A-D8); Rohtreue beim Einlesen (D7); Paketversion 1.0.0 |

Nicht geändert, als Grenze dokumentiert:
- D6/P10-F3 (Inspect außerhalb eines Git-Checkouts) und D7-A (Meldung nach Codewechsel); beides bekannte Restbefunde.
- A-D5 (konstanter Routing-Grund).
- N2 (Reihenfolge der Preflight-Meldungen).
- D-Notizen: `<br>` bei `html:false`, Fail-closed bei ```, E-Mail-Autolink in cmark-gfm.
- N1: kein Budget für einen neuen Sonnet-Lauf.

## Fortschritt

- [x] Ausgangsstand, Hashes, Matrix.
- [x] Untersuchung A–D (Workflow, Opus; Ausführung high, Prüfung max).
- [x] Umsetzung (Workflow: Stufen P und C parallel, danach S; Opus high).
  - Kandidaten-Commit `fd1ad7c`.
  - Gezielte Gruppen 751 bestanden; die neuen Regressionen scheitern auf `558e920`.
  - Ruff ohne neue Befunde (368 Altbefunde unverändert).
  - Editierbare Entwicklungsinstallation auf Paketmetadaten 1.0.0 aktualisiert (`pip install --no-deps -e .`, nur das
    Build-Backend wurde geladen).
- [x] Saubere Reproduktion `fd1ad7c`: Suite 2531 bestanden, Abnahme 21/21, Wheel 49 bestanden, Bytes gleich, 0 Provider.
- [x] Evidenz A–D (Workflow, vier Agenten, Opus high) unter `evidence/A–D`: alle PASS. D: Formatierung kann nur
  verschärfen.
- [x] Dokumente als Kandidat: V1_SCOPE.md, README, Addendum §9, Live-Addendum-Notiz, Gate-Notiz, CLOSEOUT, Manifest.
- [x] Kritik: ein lesender Kritiker (Opus, max), nach Code, Evidenz und Dokumenten.
  - Ergebnis: A PASS, B PASS, C PASS, D PARTIAL.
  - VC-1 MATERIAL, neu durch `fd1ad7c`: Modell-IDs mit Zeilenumbruch fügen über die sprechenden Kontrollgründe und
    „open cause“ gefälschte Kontrollzeilen ein.
  - VC-2 bis VC-9 MINOR, VC-10 bis VC-12 NOTE. Protokoll: Scratch `v1/critic/`, Zusammenfassung in CLOSEOUT.
- [x] Korrekturrunde 1 (von höchstens 2): Code-Commit `5560e95`.
  - VC-1: Zeilenumbrüche zitierter Texte in host-gebauten Zeilen als Marke.
  - VC-2: CLI-JSON ASCII.
  - VC-3: Präfix-Schlüssel markiert.
  - VC-4: Ursache bei ungültiger Historie.
  - VC-5 und VC-11: Befehlshilfe, Profilbeispiel `@3`, „interrupted“, Satz zur Unveränderlichkeit, „no blocking cause
    recorded“.
  - Dokumente: VC-6 (Begründung korrigiert), VC-8 (README und V1_SCOPE präzisiert, Surrogat-Grenze).
  - 8 neue Regressionen scheitern auf `fd1ad7c` an der beabsichtigten Stelle. Gezielte Gruppen 759 bestanden, Abnahme
    21/21, Ruff sauber.
  - Der Evidenz-Workflow wurde versehentlich mit dem alten Skript gestartet. Er wurde gestoppt, bevor er Dateien
    schrieb (geprüft), und mit dem Kandidaten `5560e95` neu gestartet.
- [x] Saubere Reproduktion `5560e95`: Suite 2539 bestanden, Abnahme 21/21, Wheel 49 bestanden, installierte Bytes
  gleich Quelle, Code-Fingerabdruck `03984bd4…`, Klon sauber.
- [x] Dieselbe Suite unter .pth-Netzsperre im Klon (VC-9): 2539 bestanden, 0 verweigerte Netzversuche.
- [x] Evidenz A–D für `5560e95` (ersetzt den `fd1ad7c`-Stand vollständig): alle PASS; D 1899/1899 Seiten, einschließlich
  der VC-1-Varianten.
- [x] `hashes_after.json`: geschützte Evidenz und Ledger unverändert; `git diff 558e920` der historischen Verzeichnisse
  leer.
- [x] Zweite Korrekturrunde nicht nötig.
- Hinweis VC-10: `tests/test_bounded_harness_mission.py` schreibt bei einem Suite-Lauf im Repository die versionierte
  Datei `analysis/harness_value_20260913/evidence/dry_request_captures.json` bytegleich neu. Volle Suiten laufen
  deshalb nur in Klonen; `git status` blieb sauber.
- [x] Reparaturen, nur bei nachgewiesenem Fehler; je Änderung Gegenfall, Ursache, Eingriff und Nachprüfung (CLOSEOUT).
- [x] Kritik: ein lesender Kritiker, eine von höchstens zwei Korrekturrunden genutzt.
- [x] Verifikation nach der letzten Produktänderung (`5560e95`): A–D, Abnahme 21/21, Ruff, saubere Installation, volle
  Suite.
- [x] V1_SCOPE.md, CLOSEOUT.md (Status INTERNAL_V1_COMPLETE), Manifest.
- [ ] Abschlusscommit (nur Dokumente und Evidenz; Produkt-Diff zu `5560e95` leer), lokaler annotierter Tag `v1.0.0`.
  Ergebnis steht in Commit- und Tag-Metadaten, nicht in dieser Datei.

## Kosten dieses Auftrags

Projekt-API: 0 Aufrufe, 0 USD (Stand: Abschluss). Keine Tokenzählung, keine neue Live-Autorisierung.
