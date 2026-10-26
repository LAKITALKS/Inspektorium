# Endbericht — C25 korrigieren, verpflichtende P9-Konfliktprüfung und Gesamtdiagnose P1–P10

Auftrag vom 11.10.2026, abgeschlossen am 12.10.2026. Branch `c25-p9-conflict/aa-p8-p9-20261011`, lokal, kein
Push. Dieser Bericht fasst zusammen; maßgeblich sind die verlinkten Belege. Er wurde einmal von einem unabhängigen Kritiker
(Opus 5.5, Effort max) gegen Diffs, Tests, Rohantworten, Routing-Nachweise und Ledger abgeglichen; die Sachkorrekturen
(3 Sachfehler, 6 Überzeichnungen, 12 Präzisierungen) sind eingearbeitet.

## Status (getrennt vergeben)

| Bereich | Status | Bedeutung des Status |
|---|---|---|
| C25-/P9-Reparatur und Offline-Abnahme | **ABGESCHLOSSEN** | Alle materiellen Kritikbefunde in höchstens zwei Runden geschlossen; Offline-Abnahme 21/21; Gesamtsuite im sauberen Klon bestanden. Kleinere Restbefunde sind offen dokumentiert. |
| Gesamtdiagnose P1–P10 | **DURCHGEFÜHRT, MIT OFFENEN BEFUNDEN** | Alle zehn Phasen und die Übergänge haben eine Matrixzeile mit Gegenprüfung. Belegte, begrenzte materielle Fehler sind behoben; größere Punkte und Abdeckungslücken (P4, P5, P10, XT) bleiben offen. |
| Live-Nachweis gesamt | **TEILWEISE (PARTIAL)** | Der P9-Pflichtpfad ist live nur auf Sonnet nachgewiesen. Auf dem günstigeren Haiku-Profil wurde er nicht ausgeübt, weil die konfliktfähige Analyse technisch unvollständig war. |

Live-Nachweis je Modell und Pfad (`live_retest/evidence/retest_summary.json`):

| Profil | Pfad | Status | Beleg |
|---|---|---|---|
| Haiku @3 | Primäranalyse → regulärer Entscheid → Testfreigabe | **NACHGEWIESEN** | LR-01 und LR-02: READY_FOR_RELEASE, Testfreigabe RELEASED (LR-01 über die Relation `description`; die kausale `between`-Regel wurde dabei nicht herangezogen) |
| Haiku @3 | Technische Sperre (fail-closed) | **NACHGEWIESEN** | LR-03: ANALYSIS_INCOMPLETE (Span-Offsets), kein Konfliktreview, nicht freigabefähig (kein Freigabeversuch) |
| Haiku @3 | P9-Gegenreview und Stabilität | **NICHT AUSGEÜBT** (nicht erreicht; Auswertung: `not reached`) | Kein Haiku-Slot erreichte die Konfliktroute |
| Sonnet @3 | Primäranalyse → regulärer Entscheid → Testfreigabe | **NACHGEWIESEN** | LR-01: READY_FOR_RELEASE, RELEASED |
| Sonnet @3 | Materieller Konflikt → Gegenreview → Stabilität → HUMAN_REVIEW_REQUIRED, Freigabe gesperrt | **NACHGEWIESEN (technisch)** | LR-03: beide Reviews live gesendet und verarbeitet; Konflikt offen |
| Sonnet @3 | Pflichtreview durch Obergrenze verweigert → UNRESOLVED, gesperrt | **NACHGEWIESEN** | LR-02: Gegenreview `denied`, Stabilität nicht erreicht |
| Wheel-Replay | Neuer Live-Capture offline mit installiertem Paket | **NACHGEWIESEN** | `evidence/replay_check.json`: Sonnet LR-03, identisch zum Live-Lauf, 0 Netzversuche |

Ein fehlerfrei ausgeführter technischer Test ist kein Nachweis wissenschaftlicher Wahrheit oder eines besseren
Modells. Drei synthetische Fälle messen keine Modellgüte.

## 1. Welche bisherigen Fehlerzuschreibungen waren belegt, welche nur Stopp-Regeln oder ungesicherte Interpretation?

- **Belegt** waren die Zählungen und Sperren selbst:
  - Smoke rev. 1: 0/12 erfüllten den strengen P8-Vertrag.
  - R1: LS-01 auf beiden Modellen bis zur Test-Freigabe RELEASED (2/12).
  - Die übrigen 10 R1-Slots scheiterten tatsächlich nur an der damaligen Prüfung C25: in 9 durch den Abgleich von
    `asserted_state` mit dem nicht offengelegten Host-Zustand, in 4 Sonnet-Slots durch leere Extraktions-`from_attributes`.
  - Ebenfalls belegt: Der P9-Gegenreview war vor diesem Auftrag nie live gelaufen.
- **Nur Stopp-Regel:** „Ein von der Host-Ableitung abweichender `asserted_state` ist Modellqualität“ (Smoke-Bericht §11.3,
  Addendum `phase10_live_addendum.md` §8). Das war eine vorab festgelegte Regel gegen nachträgliches Anpassen, kein empirischer
  Befund.
  - In Wahrheit verglich C25 das Modellurteil mit dem Host-Zustand. Jede Modell/Host-Abweichung wurde so zum Formatfehler.
  - Nachdiagnose der 12 abweichenden R1-Propositionen in 9 Slots: 8 Darstellungsartefakte, 2 wissenschaftliche Vorsicht des
    Hosts, 2 unklar, **0 belegte Modellfehler**. Jede Modellaussage ist aus dem Quelltext vertretbar, zwei nur teilweise.
  - Belege: [nachdiagnose_r1/README.md](nachdiagnose_r1/README.md), `second_opinion_result.json`.
- **Ungesicherte Interpretation:** „Leere Extraktions-`from_attributes` sind ein Modellfehler gegen C25“ (§11.4).
  - Der Vertrag war widersprüchlich: C23 nannte das Feld nicht, C25 prüfte es. Die Ursache liegt mindestens teilweise im Vertrag.
  - Betroffen waren 4 Sonnet-Slots und 0 Haiku-Slots.
- **Belegter Host-Fehler:** Sonnet LS-04 erhielt bei leerem `comparison` die falsche Begründung „within-arm“. Korrigiert durch
  die neue `comparison`-Regel (Frage 4).
- **Nachtrag aus Paket B (P1-F1):**
  - Phase 5B Sonnet S1 zählte bei zwei Antworten mit eigener Selbstkorrektur den Entwurf.
  - Einstimmigkeit 82/84 statt 84/84; die Richtungen der Vergleiche bleiben außer bei der Einstimmigkeit gleich.
  - Die eingefrorenen 5B-Dateien sind unverändert. Neuberechnung in [PACKAGE_B_DIAGNOSIS.md](PACKAGE_B_DIAGNOSIS.md), Abschnitt
  „Nachtrag“.
- Historische Berichte, Rohantworten und Bundles wurden nicht umgeschrieben. Die Korrekturen zu C25/C23 stehen als Nachtrag in
  [docs/phase8_9_conflict_addendum.md](../../docs/phase8_9_conflict_addendum.md) §1, die 5B-Korrektur im Abschnitt „Nachtrag“
  von [PACKAGE_B_DIAGNOSIS.md](PACKAGE_B_DIAGNOSIS.md).

## 2. Wie werden Modellurteil, Host-Ableitung und Konflikt jetzt dargestellt?

Seit AA-P8/1.1 (jetzt AA-P8/1.2, Host-Regeln AA-P8-HOST/1.1; Addendum §2) gibt es je Proposition und Gesamtaussage zwei
getrennte Bewertungen:

- **Modellseite:** `reported_verdict`, unverändert, und `model_composite_state`.
- **Hostseite:** `host_state` und `host_composite_state`, die reine Evidenzableitung ohne Rückgriff auf das Modellurteil, mit
  Host-Gründen (`host_reasons`), die nur der Host formuliert und die Ordnungsnummern statt Modell-IDs tragen.
- **Wirksamer Zustand** (`derived_state`/`composite_state`): bei Gleichheit der gemeinsame Zustand, bei Abweichung `unknown`.
- **Konflikte:** `model_host_conflicts` je Proposition und auf Gesamtebene.

Kein Modellurteil wird überschrieben, kein `asserted_state` wird aufgefüllt. Technische Vollständigkeit, wissenschaftlicher
Zustand, Konflikt, Reviewpflicht und Freigabe bleiben getrennte Felder.

Grenzen der Host-Seite: Der Host ist kein Goldstandard, sondern eine deterministische Ableitung aus den vom Modell dargestellten
Feldern (Addendum §2). Insbesondere übernimmt er den Zustand einer vom Modell deklarierten Brücke (etwa `unsupported`) ohne eigene
Evidenzprüfung; Haiku LR-02 erhielt den Host-Zustand `unsupported` genau so.

Live sichtbar in den Markdown- und HTML-Berichten. Eine nachträgliche, nicht vorab registrierte Prüfung
(`live_retest/postrun/check_render_release.py`, Ergebnis `live_retest/evidence/postrun_render_release_check.json`) zeigt: Alle 9 Revisionen enthalten die
Zeilen für Modellurteil, Host-Ableitung, Konflikte, Review-Route, Pflichtreview und lokalen Status. Alle sind gültig, und die
Berichts-Hashes stimmen. Geprüft wurde das Vorhandensein der Zeilen, nicht ihr Inhalt. Bei Haiku LR-03 (ANALYSIS_INCOMPLETE)
lauten Modellurteil und Host-Ableitung „Not supplied“, obwohl die Rohantwort Urteile enthält (claim:p1 supported, claim:p2
unsupported); eine unvollständige Analyse wird nicht ausgewertet.

## 3. Was löst den verpflichtenden P9-Pfad aus, und welche stärkeren Sperren bleiben vorrangig?

**Auslöser** (Addendum §5 und §8):

- Jeder materielle Modell/Host-Konflikt, also immer auf Gesamtebene und bei einer Proposition, wenn ihr Zustand die
  Gesamtaussage, eine entscheidende Ausgabe oder seit AA-P9/1.2 das abgeleitete Taxonomie-Label ändern kann.
- Ein materielles UNKNOWN (`necessary_unknown`).
- Beides führt bei technisch vollständiger Analyse zu REVIEW_RECOMMENDED mit `mandatory=true`.
- Danach folgt der kanonische Gegenreview mit beiden Positionen als nicht vertrauenswürdige Daten. Ist er abgeschlossen, folgt
  die einzige Stabilitätsvariante (umgekehrte Evidenzreihenfolge).
- Nichtmaterielle Konflikte bleiben als `bounded_model_host_conflict` sichtbar und sperren nicht.

**Vorrang, von stark nach schwach:**

1. Harte Sperren: PREFLIGHT_BLOCKED, ANALYSIS_INCOMPLETE, Herkunfts- und Quellenkontrolle.
2. Zwingende menschliche Prüfung: technischer Fehler, materieller Positionskonflikt (HUMAN_REVIEW_REQUIRED).
3. Pflicht-Gegenreview.
4. Regulärer Weg.

Ein Konfliktflag umgeht keine stärkere Sperre. Auflösen kann nur eine dokumentierte menschliche Adjudikation; Modellreviews
liefern nur weitere Positionen. Ein fehlender, verweigerter, budgetbedingt nicht ausgeführter, fehlgeschlagener oder unklarer
Pflichtreview ergibt UNRESOLVED und sperrt.

**Live beobachtet:**

- Haiku LR-03: Die harte Sperre (ANALYSIS_INCOMPLETE) ging dem Review vor. P9 führte den Fall über technische Auslöser auf
  HUMAN_REVIEW_REQUIRED (`mandatory=true`, `pending`), nicht über die Konfliktroute.
- Sonnet LR-03: Nach zwei abgeschlossenen Reviews blieb der Fall HUMAN_REVIEW_REQUIRED.
- Sonnet LR-02: Der durch die Obergrenze verweigerte Review führte zu UNRESOLVED.
- Freigabe: Für Sonnet LR-03 und LR-02 wurde die Testfreigabe versucht und mit RELEASE_BLOCKED abgewiesen. Haiku LR-03 war als
  ANALYSIS_INCOMPLETE nicht freigabefähig; ein Freigabeversuch fand dort nicht statt. Keine freigegebene Revision trägt einen
  offenen Pflichtreview oder einen materiellen Konflikt.

## 4. Ist unknown als Umgehung ausgeschlossen? Was ergab die comparison-Prüfung?

**unknown ist als Umgehung ausgeschlossen:**

- Die Vermischungsregel C29 (gemeldetes unknown erzwingt unknown) ist entfallen.
- Modell-`unknown` gegen ein klares Host-Urteil ist ein Konflikt.
- unknown/unknown an materieller Stelle ist `necessary_unknown`, nie Freigabebeweis.
- Ein nichtmaterielles UNKNOWN, das allein das freigegebene Taxonomie-Label bestimmt, ist seit Paket B (P8-F1/AF1) materiell.

Prüfkriterien K1–K3 (alle 16 Kombinationen Modell × Host, beide Richtungen) in `tests/test_phase8_9_conflict.py`. K12: Die
Neuauswertung der 24 historischen Captures ergab 10 × REVIEW_RECOMMENDED, 12 × HUMAN_REVIEW_REQUIRED und 2 × AUTO_RESOLVABLE,
ohne Freigabe eines offenen unknown.

**comparison** (Addendum §4, K8):

| Situation | Ergebnis |
|---|---|
| `between` | regulär |
| `within` | `unsupported` (Veränderung innerhalb eines Arms) |
| leer oder unbekannt | `unknown`, ausdrücklich ohne Schluss auf das Studiendesign |
| anderer Wert | `unknown` mit zitiertem, gekürztem Wert |

- Bei deskriptiven und assoziativen Relationen zieht die Fähigkeitsregel `comparison` nicht heran.
- Die falsche „within-arm“-Begründung bei Sonnet LS-04 ist damit behoben.
- Live: Sonnet LR-01 (randomisiert, `between`) ergab „identified effect in studied setting permitted“ → supported.

## 5. Wie wurde der Extraktionsvertrag geklärt, ohne dem Modell nachträglich Inhalte zuzuschreiben?

C23 neu (Addendum §3):

- Extraktions-`from_attributes` sind entweder gleich den Propositionsattributen oder vollständig leer.
- Bei leer verwendet der Host für die Bedeutungsprüfung die bereits validierten Propositionsattribute und vermerkt das sichtbar
  in `host_derived_copies` („host-derived copy, not model content“).
- Teilweise gefüllte, abweichende Werte bleiben eine Attributänderung.
- Alten Antworten wird kein fehlender Inhalt zugeschrieben.

C25 neu: Ein gesetzter `asserted_state` muss dem **eigenen** Modellurteil entsprechen; eine Abweichung davon ist weiter ein
harter Befund. Kriterien K9 (C23) und K2 (C25, Test `test_K2_asserted_state_must_restate_the_models_own_judgment`).

Live beobachtet: Haiku LR-02 lieferte leere Extraktions-`from_attributes`. Der Host vermerkte genau eine Host-Kopie, und die
Analyse blieb vollständig und freigabefähig.

## 6. Was wurde in jeder der zehn Phasen tatsächlich geprüft, korrigiert oder als offen dokumentiert?

Vorgehen: je Phase eine Diagnose (Opus 5.5, high) und eine Gegenprüfung (Opus 5.5, max), mit Zweck, Code- und Datenfluss,
neu ausgeführten Belegen, Gegenfall und Prüfpunkten (a)–(g). P1–P7 liefen auf `c4c2a4c`, P8–P10 und die Übergänge auf
`93cd64d`. Volle Matrix: [PACKAGE_B_DIAGNOSIS.md](PACKAGE_B_DIAGNOSIS.md); Rohergebnisse in `diagnosis/`.

| Phase | Geprüft (Auszug) | Korrigiert | Offen |
|---|---|---|---|
| P1 Output-Vertrag | 86 + 120 Tests, Abschneide-Sweep mit 856 Varianten | P1-F1 `multiple_objects`; P1-F2: ohne Rohtext nie vollständig | P1-A3/A4 (nichtmateriell) |
| P2 Provider-Vertrag | 120 Tests, Live-Double mit Bibliotheksfall | P2-F1: Tasks mit Gold-, Kurator- oder Bibliotheksfeldern werden vor jeder Modellnachricht abgewiesen (`input_preflight` 1.1, feldbasiert) | Kuratortext innerhalb von `context` wird nicht erkannt; P2-F2 altes Run-CLI |
| P3 Fallbibliothek | 189 Tests, 50 Fälle | wie P2-F1 (18 von 48 aktiven Kontexten nannten ihr Goldlabel) | Lücke 4 (P8 im Fake-Lauf nie ausgeführt) |
| P4 Lauf-Harness | 126 Tests, Fake-Lauf | P4-F1: Prompt-Identität fest und aufgezeichnet | Abdeckungslücken |
| P5 Benchmark-Integrität | 305/306 Tests, Aggregate, Holdout-Siegel | P5-F1: Namespace ohne Lease mit Altartefakten verweigert | **Größer:** Lease ohne Ablauf und Klon-Bindung |
| P6 Kalibrierung | 331 Tests, 6.4A regeneriert | Leck an der Quelle geschlossen (P2-F1) | P6-F2 (6.3-Beispiele) |
| P7 Release-Gates | 431/432 Tests, Probes W1–W5 | P7-F1/V1: Symmetrie-Gate 1.1.0 ohne `material`-Ausnahme | **Größer:** Evidenzrichtung hängt an der Modellrolle; Lücke 4 |
| P8 Semantik | 235 Tests, K12 | P8-F1/AF1 (Label-Materialität), P8-F2 (C15 für jede Proposition), P8-F3 | — |
| P9 Review | 164 + 35 Tests, Abnahme | P9-F2 (Herkunft der Adjudikation), P9-F5 | F3, F4, F6, F7, I2 |
| P10 Betrieb und Live | 107 Tests, Replay beider Historien | P10-F1/G1, K1 (Replay-Regel, Ortsbindung nur live) | G2, F3 |
| Übergänge (XT) | 613 Tests, vier End-to-End-Spuren | wie oben | Abdeckungslücken |

Kritik von Paket B: Erstkritik 0 materiell und 11 klein; Nachprüfung 1 ein materieller Befund (RF1, geschlossen); Nachprüfung 2
kein materieller Befund, 1 klein und 8 Notizen, offen dokumentiert. 44 Mutationen geprüft.

Die Kritikergebnisse von Paket A und B sind nur zusammengefasst (CHECKPOINT, PACKAGE_B_DIAGNOSIS.md); ihre Protokolle wurden nicht
archiviert. Die Protokolle der Live-Plan-Kritik liegen vollständig in [live_plan_critique/](live_plan_critique/).

## 7. Was zeigt die neue Offline-Analyse historischer Captures, und was wurde tatsächlich neu live ausgeführt?

**Offline (K12, Herkunftsklasse 2, keine neue Generierung)**, aus [historical_reanalysis.json](historical_reanalysis.json):

- Alle 24 Captures von -002/-003 sind neu ausgewertet.
- Technisch vollständig nach Phase 8: 12 statt 2.
- 9 Slots mit Modell/Host-Konflikt und 12 Konfliktpropositionen, genau die Zeilen der Nachdiagnose.
- Routen: 10 × REVIEW_RECOMMENDED, 12 × HUMAN_REVIEW_REQUIRED, 2 × AUTO_RESOLVABLE.
- Dasselbe Skript reproduziert mit dem Originalcode alle 24 Archivergebnisse ohne Abweichung in Status, Gesamtzustand und Route
  ([harness_check_original_code_c4c2a4c.json](harness_check_original_code_c4c2a4c.json)). Das Feld `difference_causes` zeigt dort
  bei 9 R1-Captures noch C25/P9-Etiketten; sie stammen aus dem Textabgleich der Klassifikation und sind keine echte Abweichung.
- Das R1-Replay unter neuem Code ergab 2 READY und 10 REVIEW_REQUIRED, alle gültig.

**Neu live:** 8 Aufrufe unter -004 nach eingefrorenem Plan
([live_retest/manifest.json](live_retest/manifest.json), Freeze `63399dd`):

| Slot | Status | Modell / Host / wirksam | Erwartung | Tokens ein/aus | Kosten µUSD | Latenz |
|---|---|---|---|---|---|---|
| Haiku LR-03 | ANALYSIS_INCOMPLETE | — (technisch) | `not_evaluable`, Status `not_acceptable` | 14.984 / 25.198 | 14.098 | 96 s |
| Haiku LR-01 | READY_FOR_RELEASE → RELEASED (Test) | supported / supported / supported | erfüllt | 15.054 / 20.667 | 11.839 | 76 s |
| Haiku LR-02 | READY_FOR_RELEASE → RELEASED (Test) | unsupported / unsupported / unsupported | erfüllt | 14.991 / 13.632 | 8.316 | 50 s |
| Sonnet LR-03 | REVIEW_REQUIRED, gesperrt | unsupported / unknown / unknown | erfüllt | 14.984 / 8.318 | 113.148 | 49 s |
| ↳ Gegenreview | completed | unsupported / unknown / unknown | — | 16.102 / 7.268 | 104.884 | 41 s |
| ↳ Stabilität | completed | unsupported / unknown / unknown | — | 16.102 / 7.079 | 102.994 | 39 s |
| Sonnet LR-01 | READY_FOR_RELEASE → RELEASED (Test) | supported / supported / supported | erfüllt | 15.054 / 6.722 | 97.328 | 36 s |
| Sonnet LR-02 | REVIEW_REQUIRED, gesperrt | unsupported / unknown / unknown | Host und wirksam konservativ | 14.991 / 6.701 | 96.992 | 38 s |

Gemeinsam für alle Aufrufe:

- Transport HTTP 200, Abschluss `end_turn`, zurückgegebenes Modell gleich dem angeforderten.
- Kosten aus der Nutzung bestätigt; keine Wiederholung, kein Overrun.
- Alle Bundles sind gültig.

Einordnung der Abweichungen nach den vorab festgelegten Leseregeln
([live_retest/RESIDUALS_BEFORE_RUN.md](live_retest/RESIDUALS_BEFORE_RUN.md)):

- **Haiku LR-03:**
  - Die Antwort war vollständig, aber die Span-Offsets der Behauptung sind um ein Zeichen verschoben (`start` 25 statt 24). Der
    Spantext selbst stimmt wörtlich.
  - Die Quellbindung von Phase 7 sperrt korrekt; es gibt keine Modell- oder Host-Bewertung.
  - Dieselbe Fehlerklasse trat in 2 von 24 historischen Captures auf (Sonnet @1, dort neben weiteren Sperrgründen). Sie ist
    nicht neu; unter den @3-Profilen war sie 1 von 6 Primärläufen die einzige Sperrursache. Wir werten sie deshalb nicht als neuen
    systematischen Fehler; die Pausenregel des Auftrags greift nicht.
  - Eine Gegenprobe des Berichtskritikers (Offsets um eins zurückgesetzt, nur offline, nicht archiviert) ergibt eine vollständige
    Analyse mit materiellem Modell/Host-Konflikt (unsupported gegen unknown). Ohne den Offset-Fehler hätte Haiku LR-03 also
    voraussichtlich die Konfliktroute erreicht.
- **Sonnet LR-02:**
  - Host `unknown` (konservativ) über „preserved observation: inconclusive“ an beiden Bindungen.
  - Nach Leseregel 2 ist das keine Fähigkeitsregel, sondern die eigene Beobachtungsangabe des Modells (siehe Frage 9).

Erwartungsprüfung: 4 von 6 Slots erfüllt; Sonnet LR-02 mit konservativer Host- und wirksamer Seite; Haiku LR-03 technisch nicht
bewertbar. Keine der drei Seiten (Modell, Host, wirksam) ist `not_acceptable`; die Statusprüfung von Haiku LR-03 ist
`not_acceptable`, weil ANALYSIS_INCOMPLETE nicht zu den zulässigen Status gehört. Kein Label „Darstellungsartefakt“ gesetzt.

Haiku LR-01 kam über die Relation `description` („descriptive inference permitted“) zu supported; Designgrenzen und die kausale
`between`-Regel wurden dabei nicht herangezogen. Nur Sonnet LR-01 (kausal, randomisiert, `between`) übte diese Regel aus.

## 8. Welche P9-Gegenprüfungen und Stabilitätsauswertungen liefen? Welche Konflikte bleiben offen?

| Slot | P9-Routing erreicht | P9-Modellaufruf erfolgt | Antwort vollständig verarbeitet | Konflikt |
|---|---|---|---|---|
| Sonnet LR-03 | ja | ja: Gegenreview `attempt-005` und Stabilität `attempt-006` | ja, beide Positionen technisch vollständig | **offen, materiell** |
| Sonnet LR-02 | ja | nein (Gegenreview durch Obergrenze verweigert) | nein; Stabilität nicht erreicht | **offen, materiell** (UNRESOLVED) |
| Haiku LR-03 | nein (nur technische Route HUMAN_REVIEW_REQUIRED) | nein | nein; Gegenreview und Stabilität nicht erreicht | keiner erfasst (Analyse unvollständig) |
| übrige 3 | nein | nein | — | keiner |

- **Inhalt der Sonnet-LR-03-Reviews:**
  - Original, Gegenreview und Stabilität urteilen gleich: Modell `unsupported`, Host `unknown`.
  - Jede hält ihre Evidenz für `inconclusive`.
  - Zwischen den Positionen entstanden bei gleichem Modell- und Host-Urteil 24 materielle P9-Positionskonflikte: 13 Proposition,
    5 Evidenz, 2 Kausalstärke, 2 Label, 2 Suchumfang. Sie betreffen Attributbelegung und Wortlaut (u. a. comparator „previous
    year“ gegen leer, endpoint_type, Direktheit, Suchumfang) und das abgeleitete Label (null gegen correlation_vs_causation).
    Eine Einordnung als reine Darstellungsunterschiede wurde nicht vorgenommen.
  - Die Route bleibt HUMAN_REVIEW_REQUIRED (`pending`). Ein abgeschlossener Aufruf ist kein erfolgreicher fachlicher Review und
    löst nichts auf.
- **Offen bleiben:**
  - Die beiden Live-Konflikte (Sonnet LR-03, LR-02).
  - Alle 12 Konfliktpropositionen der historischen R1-Captures.
  - Eine menschliche Adjudikation wurde nicht durchgeführt und nicht in deinem Namen simuliert.
- **Replay:** Sonnet LR-03 wurde mit dem Wheel von `21a2849` ohne Netz und ohne Schlüssel nachgespielt.
  - Capture verifiziert, Request identisch.
  - Beide Urteile, Konflikt und Review-Historie bleiben erhalten (`same_as_live: true`).
  - Retest-Verzeichnis unverändert, kein Ledger-Schreibzugriff.
  - Ausgeführt mit entfernter Schlüsselvariable (`env -u ANTHROPIC_API_KEY`) und blockiertem Netz. In `replay_check.json` ist
    nur die Netzsperre protokolliert, die entfernte Variable nicht.

## 9. Welche materiellen Fehler, Grenzen und optionalen Verbesserungen bleiben?

**Materielle Codefehler:** Nach der jeweils letzten erlaubten Kritikrunde von Paket A, Paket B und Live-Plan ist keiner offen.
Das schließt unentdeckte Fehler nicht aus.

**Grenzen aus dem Live-Lauf:**

1. **Vokabular-Divergenz bei verneinten Kausalbehauptungen.**
   - Beide Modelle drücken „die Evidenz trägt die Kausalaussage nicht“ als Beobachtung `inconclusive` aus.
   - Der Host leitet daraus `unknown` ab, bevor seine Fähigkeitsregeln greifen. Er kommt nur über eine deklarierte
     `unsupported`-Brücke auf `unsupported` (Haiku LR-02).
   - Folge: Korrekt verneinte Behauptungen landen regelmäßig im Pflichtkonflikt und brauchen menschliche Adjudikation. Das zeigte
     sich schon in R1 bei Haiku LS-05 (claim:p1; Nachdiagnose: „state vocabulary divergence“, Klasse unklar).
   - Das Verhalten ist regelkonform und sicher, aber eine Vertragsfrage für eine spätere Revision. Es wurde hier nicht geändert.
2. **Span-Offsets:**
   - Ein um ein Zeichen verschobener Offset bei wörtlich korrektem Spantext sperrt die ganze Analyse.
   - Aufgetreten in 3 von 30 Primärantworten: 2× Sonnet @1 neben weiteren Sperrgründen, 1× Haiku @3 als einzige Sperrursache.
     Unter @3 ist das 1 von 6, eine grobe Schätzung.
   - Eine Toleranz wäre eine Designänderung der Quellbindung.
3. **P9 auf Haiku nicht live nachgewiesen.** Die Obergrenzen von 1/1 je Modell lassen weitere Pflichtreviews offen; das ist so
   gewollt.

**Grenzen aus der Live-Planung** (Leseregeln vor dem Lauf, [RESIDUALS_BEFORE_RUN.md](live_retest/RESIDUALS_BEFORE_RUN.md)):

- Das Etikett „Darstellungsartefakt“ trennt Wortlaut-Artefakt und echte Bereichsdifferenz nicht.
- „capability“ ist eine Restklasse.
- Unterbrochene Slots werden nur über Ledger und P9-Zustand dokumentiert.

**Größere offene Punkte aus der Diagnose** ([PACKAGE_B_DIAGNOSIS.md](PACKAGE_B_DIAGNOSIS.md)):

- P5: Lease-Bindung ohne Ablauf und Klon-Sicherheit.
- P7: Die Evidenzrichtung hängt an der Modellrolle.
- P2-F1: Feldbasierte Abweisung, Kuratortext im `context` wird nicht erkannt.
- P10-G2/F3: Irreführende Meldungen.
- P9-F3/F4/F6/I2.
- XT-F3.
- P2-F2 (altes Run-CLI), P9-F7, P3/P7 Lücke 4, P6-F2 und die übrigen nichtmateriellen Punkte der Matrix.
- Abdeckungslücken P4, P5, P10 und XT.
- Restbefund SE1 (Archivierung kleiner JSON-Ausgaben) und die Notizen.

**Optionale Verbesserungen:**

- Explizites Audit-Eingabeschema.
- Toleranz oder klarere Meldung bei Offset-Fehlern.
- Präzisere Host-Route-Etiketten.
- Persistierung der Review-Prompt-Version offline.
- Replay unterbrochener Slots.

## 10. Kosten, Versuche, ungeklärte Exposition, Restbudget, geschlossene Autorisierung

| | -002 | -003 | -004 (dieser Auftrag) | kumuliert | Obergrenze |
|---|---|---|---|---|---|
| Bestätigte Kosten | 487.679 µUSD | 749.257 µUSD | **549.599 µUSD** | **1.786.535 µUSD (1,786535 USD)** | 2.000.000 |
| Generierungsversuche | 12 | 12 | **8** (Grenze des Auftrags 12) | **32** | 40 |
| Technische Wiederholungen | 0 | 0 | **0** (Grenze 2) | **0** | 4 |
| Ungeklärte Exposition | 0 | 0 | 0 | 0 | — |

- **Einzelaufrufe unter -004** (Grenze 300.000 µUSD je Aufruf):
  - höchste bestätigte Kosten: `attempt-004` mit 113.148 µUSD bei 241.756 µUSD Reservierung;
  - höchste Reservierung: `attempt-005` und `-006` mit je 248.444 µUSD, bestätigt 104.884 bzw. 102.994 µUSD.
  - Über alle drei Autorisierungen ist der teuerste bestätigte Aufruf 135.450 µUSD (-003 `attempt-009`).
- **-004** ist geschlossen: REVOKED mit ORDER_COMPLETE, ausführbarer Rest 0, Ledger-SHA-256 `ccbbdc4f…`
  ([evidence/closure.json](live_retest/evidence/closure.json)). Maßgeblich ist der widerrufene Ledger; die eingefrorene
  `authorization.json` bleibt unverändert und zeigt weiter `ACTIVE`.
- **Rechnerischer Rest** unter der Gesamtgrenze: 213.465 µUSD, nicht ausführbar und nicht übertragen.
- **-002/-003** sind unverändert REVOKED, und ihre Ledger-Hashes sind gleich den Pins.
- Der Nachfolgeanspruch `repair_r1/successor_claim.json` bindet -004 an -003.
- **Vorfall am 11.10. (ohne Kosten):** Ein Kritiker-Skript öffnete eine Live-Session für einen Wegwerf-Nachfolger der echten
  Historie und erzeugte dabei `repair_r1/successor_claim.json`. Kein Request, keine Kosten. Die Datei wurde entfernt, die Bytes von
  -002/-003 als unverändert geprüft und 46 Wegwerf-Nachfolger gelöscht (CHECKPOINT). Der heutige Anspruch stammt von -004.
- Replay bleibt möglich.

## 11. Getesteter Codecommit, Freeze vor Live und Evidenz-/Berichtscommit

| Commit | Inhalt |
|---|---|
| `93cd64d` | Paket A: AA-P8/1.1 + AA-P9/1.1, getrennte Urteile, Pflichtkonfliktreview, Nachfolgeautorisierung 1.1 |
| `21a2849` | Paket B: Diagnose und begrenzte Korrekturen (AA-P8/1.2, AA-P9/1.2). **Getesteter Codecommit** des Live-Laufs (`manifest.tested_code_commit`) |
| `63399dd` | **Freeze vor jedem Aufruf:** Autorisierung -004, Fälle, Erwartungen, Manifest, Skripte, Restbefunde, Kritikprotokolle, saubere Reproduktion von `21a2849` (2470 bestanden, Abnahme 21/21, Wheel-Tests 49, installierte Bytes gleich der Quelle) |
| `705865a` | Live-Evidenz: Ledger, Rohantworten, Bundles, P9-Zustand, Testfreigaben, Auswertung, Replay, Abschluss, Nachfolgeanspruch |
| Berichtscommit | Dieser Bericht, das Prüfskript `live_retest/postrun/check_render_release.py` mit Ergebnis `live_retest/evidence/postrun_render_release_check.json`, Checkpoint |

- Der Runner prüfte vor dem ersten Aufruf: `src` gleich `21a2849`, eingefrorene Dateien committet und unverändert,
  Freeze-Commit `63399dd` protokolliert.
- Alle Commits haben Autor und Committer Lazaros Varvatis, ohne Co-Author.

## 12. Ist ein separat beauftragter frischer Wirksamkeitsvergleich jetzt sinnvoll vorbereitbar?

**Eingeschränkt ja.**

**Dafür spricht:**

- Der Prüfpfad ist live auf Sonnet bis zur offenen menschlichen Prüfung belegt: getrennte Urteile, Pflichtkonflikt, Gegenreview
  und Stabilität, Sperren, Testfreigabe, Replay. Auf Haiku nur Primärpfad und technische Sperre. Die einzige Auflösung, die
  menschliche Adjudikation, wurde nie live ausgeübt.
- Budget- und Herkunftskontrollen hielten.
- Bibliotheksfälle mit Gold-, Kurator- oder Bibliotheksfeldern werden abgewiesen (`input_preflight` 1.1). Die Prüfung ist
  feldbasiert und erkennt Kuratortext im `context` nicht; ein neuer Fallsatz braucht ein explizites Eingabeschema oder eine eigene
  Leckprüfung.

**Einschränkungen vor einem Vergleich:**

1. Verneinende Urteile landeten bisher meist im Pflichtkonflikt: in R1 8 von 9 verneinenden Propositionen, live 2 von 3 technisch
   vollständigen, beide Sonnet. Live war die Ursache die Beobachtung `inconclusive` (Frage 9.1), in R1 überwiegend andere
   Host-Regeln; Haiku LR-02 entging dem Konflikt über eine deklarierte `unsupported`-Brücke. Ein Vergleich bräuchte entweder
   eine Vertragsklärung oder eine eingeplante menschliche Adjudikation, die noch nie live ausgeübt wurde.
2. Off-by-one-Offsets traten in 3 von 30 Primärantworten auf, unter @3 in 1 von 6 als einzige Sperrursache. Eine solche
   technische Ausfallrate muss vorab registriert werden.
3. Es braucht eine neue, unabhängige Fallmenge mit Quellenherkunft und vorab festgelegten Metriken. Die Bibliotheksfälle sind für
   den Audit-Pfad gesperrt; die drei LR-Fälle sind Entwicklungsfälle.
4. Es braucht ein neues, eigens beauftragtes Budget. Der kumulierte Rest dieses Rahmens ist nicht ausführbar.
5. Für größere Läufe muss vorher die P5-Lease-Bindung geschlossen werden.

## Belege

- Vertragsnachtrag: [docs/phase8_9_conflict_addendum.md](../../docs/phase8_9_conflict_addendum.md)
- Diagnosematrix und Prüfjournal: [PACKAGE_B_DIAGNOSIS.md](PACKAGE_B_DIAGNOSIS.md), [CHECKPOINT.md](CHECKPOINT.md)
- Maschinenlesbare Ergebnisse:
  - [diagnosis/p1_p7_results.json](diagnosis/p1_p7_results.json)
  - [diagnosis/p8_p10_xt_results.json](diagnosis/p8_p10_xt_results.json)
  - [historical_reanalysis.json](historical_reanalysis.json)
  - [live_retest/evidence/retest_summary.json](live_retest/evidence/retest_summary.json)
- Live:
  - [live_retest/ledger.json](live_retest/ledger.json)
  - [live_retest/captures/](live_retest/captures/) (Rohantworten)
  - [live_retest/evidence/](live_retest/evidence/): `run_log.jsonl`, `replay_check.json`, `closure.json`, `test_releases.json`,
    `postrun_render_release_check.json`
- Saubere Reproduktion: [clean_reproduction/](clean_reproduction/)
- Plan-Kritik und Offline-Selbsttest: [live_plan_critique/](live_plan_critique/)
