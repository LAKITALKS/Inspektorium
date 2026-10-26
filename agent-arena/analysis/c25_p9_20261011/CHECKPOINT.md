# Arbeitscheckpoint — Auftrag „C25 korrigieren, verpflichtende P9-Konfliktprüfung und Gesamtdiagnose P1–P10“

Stand: 11.10.2026. Dieser Checkpoint wird bei jedem Abschnittswechsel aktualisiert. Nach einer
Kompaktierung zuerst hier weiterlesen; abgeschlossene Läufe nicht erneut starten.

## Auftrag (Kurzfassung)

1. Ausgangslage, Nachdiagnose und Kostenhistorie übernehmen.
2. **Paket A (offline):**
   - Modell- und Host-Bewertung getrennt führen; Abweichung als verpflichtenden P9-Konflikt behandeln.
   - Den `unknown`-Ausweg schließen.
   - `comparison` und die Extraktionsregel `from_attributes` (C23/C25) korrigieren.
   - Den Vertrag versionieren.
3. **Paket B:** Gesamtdiagnose P1–P10 mit Übergängen und Matrix. Belegte, begrenzte materielle Fehler
   beheben.
4. Offline-Abnahme und unabhängige Codekritik.
5. **Erst danach:** kleiner, vorab eingefrorener Live-Nachtest aus dem alten Restbudget.
   - Höchstens 3 frische Fälle × 2 Modelle und höchstens 12 Versuche.
   - Höchstens 2 technische Wiederholungen, höchstens 0,30 USD je Aufruf.
6. Endbericht (einmal vom Kritiker geprüft), Autorisierung schließen, kurze deutsche Schlussnachricht.

## Ausgangslage (geprüft)

- **Basis:** Branch `live-integration/aa-p10-live-20261011`, HEAD `c4c2a4c` (R1-Code `f885aae`, Freeze
  `6142dcd`). Arbeitsbranch: `c25-p9-conflict/aa-p8-p9-20261011`.
- **Kein `AGENTS.md`/`CLAUDE.md` im Repo.** Maßgeblich sind README, `docs/phase8_semantic_contract.md`,
  `docs/phase9_review_contract.md`, `docs/phase10_operational_contract.md`,
  `docs/phase10_live_addendum.md` und die Phasentabelle `analysis/phase4_9_retrospective/phase_status_table.md`.
- **Kosten laut Ledgern** (nachgerechnet):
  - -002: 487.679 µUSD, 12 Versuche, `REVOKED`.
  - -003: 749.257 µUSD, 12 Versuche, `REVOKED`.
  - Gesamt 1.236.936 µUSD, 24 Versuche, 0 Wiederholungen, keine ungeklärte Abrechnung.
  - **Rest 763.064 µUSD.**
- 25 fremde unversionierte Einträge im Arbeitsbaum; nicht anfassen, nicht stagen.

## Rollen (höchstens drei gleichzeitig aktiv, keine rekursive Delegation)

| Rolle | Umsetzung | Modell / Effort |
|---|---|---|
| Koordination und Implementierung | Hauptsitzung | `claude-opus-5-5` |
| Diagnose P1–P10 | Workflow-Agenten, höchstens eine Ausführungs- und eine Verifikationsinstanz gleichzeitig | `opus`, Ausführung `high`, Verifikation `max` |
| Kritiker (schreibgeschützt) | neuer General-Purpose-Subagent | `opus`, `max` |

Der frühere R1-Kritiker wird nicht weiterverwendet. Gründe: Der Nutzer verlangt Effort `max`, was sich
nicht nachträglich setzen lässt, und sein Kontext ist sehr groß.

## Rundenzähler

| Paket | Erstkritik | Korrekturrunden (höchstens 2) | Status |
|---|---|---|---|
| A — C25/P9/comparison/Extraktion | 1 (3 materiell, 9 klein, 8 Notizen) | 2 (Nachprüfung 1: 2 materiell offen A-R1/A-R2, 1 klein A-R3; Nachprüfung 2: keine materiellen und keine kleinen Befunde) | **abgeschlossen**, Commit `93cd64d` |
| B — Gesamtdiagnose P1–P10 | 1 (0 materiell, 11 klein, 14 Notizen) | 2 (Nachprüfung 1: 1 materiell RF1/RE1; Nachprüfung 2: 0 materiell, 1 klein, 8 Notizen — offen dokumentiert) | **abgeschlossen**, Commit `21a2849` |
| Live-Plan (Fälle, Erwartungen, Skripte) | 1 (LS1, LS2, LO2 materiell) | 2 (Nachprüfung 1: LS2-1 materiell; Nachprüfung 2: 0 materiell, 3 klein bestätigt + LO2-2 teilweise, Notizen — als Leseregeln in `live_retest/RESIDUALS_BEFORE_RUN.md`) | **eingefroren** (Freeze-Commit) |
| Endbericht | 1 Sachabgleich (3 Sachfehler, 6 Überzeichnungen, 12 Präzisierungen; eingearbeitet) | — (keine Code-Auditschleife) | **abgeschlossen** (`ENDBERICHT.md`) |

## Live-Budget (nur alter Rest)

- Neue Autorisierung `-004` nur mit verifizierter Bindung an `-002`/`-003`.
- Gesamt ≤ 2.000.000 µUSD; damit für `-004` ≤ 763.064 µUSD.
- Versuche: ≤ 12 in diesem Auftrag und ≤ 40 insgesamt (bisher 24).
- Wiederholungen: ≤ 2 in diesem Auftrag und ≤ 4 insgesamt.
- Noch keine Provideraufrufe. Live erst nach abgeschlossenem Paket A und B samt Kritik.

## Festgelegte Designentscheidungen (Paket A)

Vertrag: `docs/phase8_9_conflict_addendum.md` (AA-P8/1.1, AA-P8-HOST/1.1, AA-P9/1.1).

- **Getrennte Positionen:** `reported_verdict` ist das Modellurteil, `host_state` die reine Evidenzableitung
  (Regelversion und Gründe). `derived_state` ist bei Gleichheit der gemeinsame Zustand, sonst `unknown`
  mit offenem Konflikt. Dazu Modell- und Host-Composite getrennt, `model_host_conflicts` mit Scope
  `proposition` oder `composite`.
- **C25:** `asserted_state` gibt das eigene Modellurteil wieder; das ganze Claim folgt AND/OR der eigenen
  Urteile. Ein Konflikt mit dem Host ist kein Formatfehler.
- **C23:** Extraktions-`from_attributes` ist entweder gleich `P.attributes` oder vollständig leer. Bei leer
  nutzt der Host sichtbar `P.attributes`; Teilbefüllung bleibt ein Attributwechsel-Befund.
- **comparison:** `between` regulär; `within` → unsupported (within-arm); null/unknown → unknown ohne
  Schluss auf das Studiendesign; ein anderer Wert → unknown.
- **P9-Routing:** Harte Blockaden und `HUMAN_REVIEW_REQUIRED` haben Vorrang.
  - Ein materieller Modell/Host-Konflikt ist ein verpflichtender Trigger: `REVIEW_RECOMMENDED`, Konflikt
    auf Claim-Ebene immer.
  - Nach abgeschlossenem Gegenreview bleibt der Fall `HUMAN_REVIEW_REQUIRED`.
  - Wird der Review verweigert, schlägt er fehl, stoppt am Budget oder wird abgelehnt, ist der Fall
    `UNRESOLVED`.
  - Auflösen kann nur eine menschliche Entscheidung, nämlich eine konfliktfreie, nicht-`unknown`
    Position oder eine revalidierte Korrektur.
- **Review-Paket:** Bei einem Konflikt erhält es beide Positionen als nicht vertrauenswürdige Daten. Ohne
  Konflikt bleibt der Review blind.
- **Versionen:**
  - Prompts `…-contract-r2`, Hash `3d0550e5…`, und `…-r2-review-p9-2`, Hash `662125d4…`.
  - Profile `claude-haiku-5-5@3` (max_tokens 48000), Hash `f8f8f9ba…`, und `claude-sonnet-5-5@3`, Hash
    `d464c62a…`.
  - Registry `phase8_semantics_taxonomy` und `phase9_history_review` = 1.1.
  - Historische Prompt- und Profil-Hashes sind unverändert und gepinnt.
- **Live-Pfad:**
  - Nachfolge-Autorisierungsschema `aa-p10-live-authorization/1.1` mit verifizierter Bindung an die
    Vorgänger-Ledger und kumulativen Obergrenzen (2.000.000 µUSD / 40 / 4).
  - Review-Obergrenze je Modell (Gegenreview und Stabilität je ≤ 1). Bei erreichter Grenze wird ohne
    Request abgelehnt, und der Review bleibt offen.

## Belege Paket A (offline)

- `tests/test_phase8_9_conflict.py` mit 33 Tests: K1–K10, 16 Kombinationen, beide Richtungen,
  unknown/unknown, Vorrang, Paket, Fehler/Ablehnung, Persistenz, comparison, Extraktion.
- `tests/test_phase10_live.py`:
  - K11: Konflikt im Live-Pfad mit Transport-Double, verpflichtendem Gegenreview mit beiden Positionen
    und blockierter Freigabe.
  - Nachfolge-Autorisierung und Review-Obergrenze.
  - Pins für r2/@3.
- Alte Akzeptanzzeilen AA-P8/1.0 bleiben eingefroren; die 1.1-Erwartungen stehen getrennt
  (`tests/test_phase8_acceptance.py`).
- K12: Alle 24 Captures neu analysiert (`historical_reanalysis.json`, Skript `reanalyse_captures.py`,
  Provenienzklasse 2).
  - Dasselbe Skript reproduziert mit dem Originalcode `c4c2a4c` alle 24 Archivergebnisse ohne Abweichung
    (`harness_check_original_code_c4c2a4c.json`).
  - Neu: 12 statt 2 Slots technisch `completed`, 9 Slots mit Konflikt, 12 Konfliktpropositionen; das
    sind genau die Nachdiagnose-Zeilen.
- Nachdiagnose-Evidenz: `nachdiagnose_r1/` mit Tabelle, Second-Opinion-Ergebnis und Skripten.
- Ergebnisse (11.10.2026, vor der Erstkritik):
  - P8–P10-Testdateien: 497 bestanden.
  - Ruff auf allen geänderten Dateien: sauber.
  - P10-Abnahme: 21/21.

## Korrekturrunde 1 (Paket A)

| Befund | Korrektur |
|---|---|
| A-C1 ausgelassener oder kopierter Vorgänger | Kette abgeschlossen unter supersedes/predecessors; Vorgänger nur aus eigenem `canonical_directory`; festgeschriebene Historie `KNOWN_CLOSED_AUTHORIZATIONS` (-002/-003 mit Ledger-Hash) |
| A-C2 paralleler Nachfolger | `successor_claim.json` einmalig per `O_EXCL` im Verzeichnis des jüngsten Vorgängers; zweiter Nachfolger abgewiesen |
| A-C3 frisches Schema 1.0 | Für neue Live-Budgets abgewiesen, solange die Historie festgeschrieben ist; Replay bleibt möglich |
| A-C4 Reviewgrenzen | nur 0 oder 1 |
| A-C5 Replay der Grenzentscheidung | Entscheidung vor dem Request im Ledger (`review_cap_claims`); Replay folgt ihr. Ein live erlaubter, aber nie gesendeter Review wird als nicht gesendet nachgespielt (gültige Herkunft). Ablehnungsgrund steht im P9-Versuch |
| A-C6 abgeschwächte Tests | `evaluate_phase8` in den Semantiktests prüft wieder den Host-Zustand. Mutationsprüfung erkennt wieder 12 Fälle (5/2/1/4) |
| A-C7 Modelltext als Host-Grund | `host_reasons` nur vom Host geschrieben |
| A-C8 Prompt „jede Abweichung Pflichtreview“ | r2 unterscheidet materiell und nichtmateriell und ersetzt die AA-P8/1.0-Verweise; neue Hashes `e92bba73…` und `725f35b0…`; Profile `07406852…` und `537510e9…` |
| A-C9 Reviewprompt/Profile | offline AA-P9/1.1-Prompt bei Konfliktpaket, Unabhängigkeitsvermerk korrigiert; Nachfolger nur mit r2-Profilen |
| A-C10 Projektion | Konfliktzeile über die ganze Historie (Auswahl und andere Positionen) |
| A-C11 comparison bei deskriptiven Relationen | Addendum präzisiert (C14 unverändert, konservativ) |
| A-C12/N5 Neuanalyse-Label | Label aus dem tatsächlich geladenen Code; materiell/nichtmateriell aus den Triggern |
| N2/N3/N4/N6 | Addendum-Verweis §5, Registry-Kommentar, Konfliktkennzeichnung in `render_phase8`, r2-Kopfsatz |
| N1 | bleibt nach Auftrag: nur materielle Abweichungen sind pflichtig; nichtmaterielle bleiben sichtbar offen (Addendum §5) |

**Vorfall beim Nachprüfen (11.10.2026, ca. 21:00):**
- Ein Neulauf des Kritiker-Skripts `cc_successor.py` mit dem neuen Code öffnete eine Live-Session für
  einen Wegwerf-Nachfolger der echten Historie.
- Dabei entstand `analysis/live_smoke_20261011/repair_r1/successor_claim.json`.
- Kein Request und keine Kosten. Ledger und Autorisierungen von -002/-003 blieben bytegleich (Hashes
  geprüft).
- Die Datei ist entfernt und `git status` des Ordners ist leer.
- Die 46 Wegwerf-Nachfolger im Scratchpad, die auf die echten Vorgänger zeigten, sind gelöscht.
- Regel ab jetzt: Gegen die echten Vorgänger nur `load_authorization` (schreibgeschützt) aufrufen, nie
  eine Live-Session öffnen.

Entwicklungsprüfung nach Runde 1:
- Ruff sauber.
- P8–P10: 504 bestanden.
- Gesamtsuite im Entwicklungsbaum: 2434 bestanden. Das ist nicht der verbindliche Lauf; der folgt im
  sauberen Klon.
- Abnahme: 21/21.
- K12 neu erzeugt, Skriptprüfung 0 Abweichungen.

## Korrekturrunde 2 (Paket A, letzte erlaubte)

| Befund der Nachprüfung 1 | Korrektur |
|---|---|
| A-R1 festgeschriebene ID mit frischem 1.0-Ledger | Pin enthält Ledger- und Autorisierungs-Hash; live öffnet eine festgeschriebene ID nur als sie selbst (unveränderte Datei, vorhandener geschlossener Ledger) |
| A-R2 Anspruch umleitbar (Byte-Kopie, handgeschriebener Kopf, gefälschte 1.1-Glieder) | Jeder Vorgänger-Ledger muss an seine Autorisierungsdatei gebunden sein; festgeschriebene Vorgänger nur mit gepinntem Autorisierungs-Hash; nicht festgeschriebene nur als Schema 1.1, deren eigener jüngster Vorgänger sie im Anspruch (ID, Verzeichnis, Hash) ausweist |
| A-R3 Abbruch bei nicht ACTIVE Ledger | Review mit wahrem Grund abgelehnt, Bundle wird geschrieben; Replay unterscheidet Grenze und fehlende Live-Freigabe |
| N-R2 Modell-IDs in Host-Gründen | Ordnungsnummern statt Bindungs- und Brücken-IDs; unbekannter comparison-Wert gekürzt zitiert |
| N-R4 K12-Herkunftsklasse | Klasse und Hinweis aus dem geladenen Code abgeleitet |
| N-R1/N-R3/N-R5 | im Addendum §6a als Grenzen dokumentiert |

Entwicklungsprüfung nach Runde 2:
- Ruff sauber.
- Live-Tests: 58 bestanden.
- Konflikttests: 35 bestanden.
- Gesamtsuite im Entwicklungsbaum: 2436 bestanden.
- Abnahme: 21/21.
- K12: 0 Abweichungen.
- Echte -002/-003-Verzeichnisse unverändert.

## Paket B (Stand nach Umsetzung, vor der Erstkritik)

- **Diagnose:**
  - P1–P7 auf `c4c2a4c` mit 14 Agenten (Diagnose high, Gegenprüfung max).
  - P8–P10 und XT auf `93cd64d` mit 8 Agenten.
  - Ergebnisse: `diagnosis/`.
- **Behobene materielle Befunde:** P1-F1/A2, P2-F1/P3-F1/P6-F1, P4-F1, P5-F1 (begrenzter Teil),
  P7-F1/V1, P8-F1/AF1, P8-F2, P9-F2, P10-F1/G1 (= P9-F1/A1, XTV-A1) und K1. Dazu P8-F3 und P9-F5 an
  eigenen Paket-A-Stellen.
- **Tests:** `tests/test_package_b_regressions.py` mit 18 Tests (außerhalb der gezählten QA-Umfänge)
  sowie 3 Live-Regressionen in `tests/test_phase10_live.py`.
- **Entwicklungsprüfung:**
  - Ruff sauber.
  - Gesamtsuite im Entwicklungsbaum: 2457 bestanden.
  - Abnahme: 21/21.
  - Lokale historische Verifikation bestanden.
  - K12 unverändert.
  - R1-Replay: 2 READY / 10 REVIEW_REQUIRED, alle Bundles gültig, Verzeichnis bytegleich.
- **Nachtrag 5B-S1** (82/84 statt 84/84 einstimmig) und Liste der offenen größeren Punkte:
  `PACKAGE_B_DIAGNOSIS.md`.

## Offene Punkte / nächster Schritt

- [x] Paket A implementieren.
- [ ] Paket A Erstkritik (Kritiker opus/max, schreibgeschützt). Danach höchstens 2 Korrektur- und
  Nachprüfrunden.
- [ ] Diagnose P1–P7 läuft (Workflow `w9je3on17`, schreibgeschützt auf Worktree `c4c2a4c`); danach
  P8–P10 und die Übergänge auf dem neuen Code.
- [ ] Paket-B-Kandidat: Replay aus einem sauberen Klon scheitert an der `canonical_directory`-Prüfung,
  auch im Replay-Modus.
- [ ] @3-Höchstexposition ≤ 300.000 µUSD je Aufruf an den frischen Live-Fällen prüfen (count_tokens beim
  Manifest).

## Unterbrechung 12.10.2026 (Nutzungslimit) — hier fortsetzen

- **Paket A:** abgeschlossen, Commit `93cd64d`.
- **Paket B:**
  - Diagnose abgeschlossen, Korrekturen und Tests umgesetzt, aber **nicht committet** (Arbeitsbaum).
  - Erstkritik wurde gestartet und wegen des Limits abgebrochen; **neu starten**: Opus, Effort max,
    schreibgeschützt.
  - Sie gilt für `git diff 93cd64d` plus `tests/test_package_b_regressions.py`,
    `PACKAGE_B_DIAGNOSIS.md` und `diagnosis/`.
- **Live-Nachtest:**
  - Entwurf `prepare_retest.py` liegt nur im Scratchpad (`live_retest_draft/`): Fälle LR-01..03,
    Autorisierung -004 nach Schema 1.1, Manifest.
  - Noch nicht eingefroren, keine Erwartungsdatei, keine Kritik der Erwartungen, **kein Aufruf**.
- **Offene Schritte in dieser Reihenfolge:**
  1. Paket-B-Kritik mit höchstens 2 Runden.
  2. Commit von Paket B.
  3. `scripts/phase10_clean_reproduce.py --full-suite` zusammen mit der Abnahme.
  4. Live-Freeze: Erwartungen schreiben, Kritiker prüft sie, Freeze-Commit.
  5. Live-Lauf nach festgelegter Reihenfolge.
  6. Replay mit dem installierten Wheel.
  7. -004 schließen.
  8. Evidenz-Commit.
  9. Endbericht mit einer Kritikrunde.
  10. Memory aktualisieren.
  11. Kurze deutsche Schlussnachricht.
- **Kosten bisher:** 1.236.936 µUSD (nur -002/-003). In diesem Auftrag gab es keinen Modellaufruf.

## Paket B, Korrekturrunde 1 (12.10.2026)

Erstkritik (Workflow mit zwei Kritikern, Opus max): 0 materiell, 11 klein, 14 Notizen. Umgesetzt:
- **BF1:** Adjudikation eines nie gesendeten Live-Reviews ehrlich formuliert, auch im Replay.
- **BF2/BE13:** AA-P8/1.2, AA-P9/1.2, Registry 1.2; gespeicherte 1.1-Zustände scheitern geschlossen.
- **BF3:** Pins gelten auch beim Replay; `replay_ledger_sha256` in der Replay-Evidenz.
- **BF4/BF5/BE2:** Tests für das Flag im Harness und für ein einiges UNKNOWN am Taxonomie-Auslöser.
- **BE10:** Ein abgeschnittenes nacktes `{` wird erkannt.
- **BE11:** Ohne Rohtext gibt es keine vollständige Analyse.
- **BF6:** Die P5-Sperre ignoriert `.DS_Store`.
- **BF8:** Der Fingerprint bindet `parse_multiple_objects`, wo das Feld vorhanden ist.
- **BE14/P10-F4:** Der CLI-Replay-Zustand liegt neben der Ausgabe.
- **Dokumente:** Matrix, Abdeckungslücken, vollständiger 5B-Nachtrag, Restgrenzen, archivierte
  P8–P10-Probes, Addendum §6/§8.

Entwicklungsprüfung:
- Ruff sauber.
- Gesamtsuite im Entwicklungsbaum: 2461 bestanden.
- Abnahme: 21/21.
- Historische Verifikation bestanden.
- K12 unverändert (jetzt unter AA-P8/1.2 + AA-P9/1.2).
- R1-Replay: 2/10, Verzeichnis bytegleich.

## Paket B, Korrekturrunde 2 (12.10.2026, letzte erlaubte)

Nachprüfung 1: 1 materiell (RF1 = RE1, von zwei Prüfern bestätigt), 5 klein, 2 Notizen. Umgesetzt:
- **RF1/RE1 (materiell):** Sechs bytegleiche `93cd64d`-Kopien sind aus dem P8–P10-Probe-Archiv entfernt.
  - Kein archivierter Inhalt entspricht einem Git-Objekt der Historie.
  - `python -m pytest -q` aus dem Wurzelverzeichnis sammelt wieder nur `tests/`.
- **RF2:** Der Vermerk im P9-Versuch eines nie gesendeten Reviews ist ehrlich formuliert, live und im
  Replay.
- **RE2:** 13 kleine P1–P7-Ausgaben sind archiviert.
- **RE3:** Der Nachtrag nennt zusätzlich ECE-10, H1↔S1 und den Vierfeldervergleich.
- **RE4/RF3:** Tests für nacktes `{`, Rohtext ohne `finish_reason`, Fingerprint, `.DS_Store`,
  Registry-Versionen, Adjudikationstexte offline und im Replay sowie CLI-Replay ohne Schreiben ins
  Autorisierungsverzeichnis.
- **RE5/RE6:** Bezeichnungen korrigiert, P3-Lücke 4 ergänzt, Registry-Änderungen und Titel des Addendums.
- **Pflichtkommando für die Gesamtsuite:** `python -m pytest -q` aus dem Wurzelverzeichnis, nicht
  `pytest -q tests`.

Letzte Nachprüfung (Runde 2):
- **Ergebnis:** 0 materiell, 1 klein (SE1), 8 Notizen. Offen dokumentiert in `PACKAGE_B_DIAGNOSIS.md`
  („Offene Restbefunde“), nicht mehr korrigiert, weil höchstens 2 Runden erlaubt sind.
- **Entwicklungsprüfung nach Runde 2** (vor der Nachprüfung, Hauptbaum):
  - `.venv/bin/ruff check` auf allen geänderten Dateien: sauber.
  - `.venv/bin/python -m pytest -q -p no:cacheprovider` aus dem Wurzelverzeichnis: 2470 bestanden.
  - `scripts/phase10_acceptance.py --output <scratch>`: 21/21.
  - `verify_local_historical_asa('.')`: HISTORICAL_VERIFICATION_PASSED.
  - R1-Replay aus dem echten Verzeichnis im Replay-Modus mit Zustand im Scratchpad:
    2 READY_FOR_RELEASE / 10 REVIEW_REQUIRED, Verzeichnis bytegleich, 0 Netzzugriffe.
  - K12-Neuauswertung: bytegleich zur abgelegten Datei.
- **Bestätigung durch die Nachprüfung:** Die Kritiker haben diese Zahlen unabhängig bestätigt (2470 im
  echten Baum, 2470 gesammelt im sauberen Klon) und dazu 44 Mutationen geprüft.

## Paket B committet, saubere Reproduktion, Live-Freeze (12.10.2026)

- **Paket B:** Commit `21a2849`.
- **Saubere Reproduktion** von `21a2849`, AA-P10-REPRO/1.1, nicht editierbares Wheel, Belege in
  `clean_reproduction/`:
  - Gesamtsuite 2470 bestanden.
  - Abnahme 21/21.
  - Wheel-P10-Tests 49 bestanden.
  - Installierte Bytes gleich der Quelle.
  - 0 Provideraufrufe.
- **Live-Plan:**
  - Drei synthetische Fälle: LR-01 gestützt, LR-02 klar nicht gestützt, LR-03 konfliktfähig.
  - Erwartungen Schema 2.1 mit drei Seiten (Modell, Host, effektiv), `not_evaluable` für technische
    Fehlschläge, Host-Route und P9-Status je Reviewart.
  - Skripte: run, summarize, replay, close und prepare.
  - Kritik: drei Runden (Erstkritik plus zwei Nachprüfungen), Protokolle in `live_plan_critique/`.
  - Offline-Selbsttest: 15 Szenarien, `live_plan_critique/offline_selftest_regression_v3.txt`.
  - Letzte Nachprüfung: kein materieller Befund. Die offenen kleinen Befunde und Notizen sind als
    verbindliche Leseregeln vor dem Lauf festgehalten (`live_retest/RESIDUALS_BEFORE_RUN.md`) und nicht
    mehr korrigiert, weil höchstens 2 Runden erlaubt sind.
- **Freeze:** `live_retest/` mit `authorization.json` (-004, ACTIVE, 763.064 µUSD, 12 Versuche,
  2 Wiederholungen, 0,30 USD je Aufruf, Ablauf 15.10.2026), `manifest.json`, `expectations.json`,
  `tasks/` und `scripts/`. Gebunden an `tested_code_commit` `21a2849`.
- **Nächste Schritte:**
  1. Runner losgelöst starten, Schlüssel nur im Kindprozess.
  2. `close_retest.py`.
  3. `replay_retest.py` mit dem Wheel-venv.
  4. `summarize_retest.py`.
  5. Evidenz-Commit inklusive `repair_r1/successor_claim.json`.
  6. Endbericht mit einer Kritikrunde.

## Live-Lauf und Abschluss (12.10.2026)

- **Lauf:** Freeze `63399dd`, Runner losgelöst gestartet, Vorprüfungen bestanden, alle 6 Primärslots gelaufen.
  - 8 Aufrufe: 6 Primär, 1 Gegenreview und 1 Stabilität bei Sonnet LR-03.
  - Kosten 549.599 µUSD aus der Nutzung bestätigt.
  - Keine Wiederholung, kein Overrun, keine ungeklärte Exposition.
- **Ergebnisse:**
  - Haiku LR-03: ANALYSIS_INCOMPLETE, Span-Offsets um eins verschoben.
  - Haiku LR-01/LR-02 und Sonnet LR-01: READY_FOR_RELEASE, Testfreigabe RELEASED.
  - Sonnet LR-03: Konflikt, beide Reviews abgeschlossen, HUMAN_REVIEW_REQUIRED, gesperrt.
  - Sonnet LR-02: Konflikt, Gegenreview durch Obergrenze verweigert, UNRESOLVED, gesperrt.
- **Nach dem Lauf:**
  - `close_retest.py`: -004 REVOKED (ORDER_COMPLETE), Rest 0.
  - Wheel-Replay von Sonnet LR-03: identisch zum Live-Lauf, 0 Netzversuche.
  - `summarize_retest.py` ausgeführt.
  - Evidenz-Commit `705865a`.
- **Nachträgliche Prüfung** von Markdown, HTML und Freigabeentscheid: `live_retest/postrun/check_render_release.py`.
- **Endbericht:** `ENDBERICHT.md`, einmal vom Kritiker abgeglichen, Korrekturen eingearbeitet.
- **Kosten kumuliert:** 1.786.535 µUSD, 32/40 Versuche, 0/4 Wiederholungen. Kein ausführbares Budget mehr.
- **Abgeschlossen:** Diagnose-Worktrees `diag_base` und `diag_new` werden entfernt, Gedächtnis ist aktualisiert.
