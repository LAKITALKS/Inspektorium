# Paket B — Gesamtdiagnose P1–P10 mit Übergängen

Stand: 12.10.2026 (nach Korrekturrunde 2 der Paket-B-Kritik). Auftrag: „AGENT ARENA — C25 korrigieren,
verpflichtende P9-Konfliktprüfung und Gesamtdiagnose P1–P10“, Paket B.

## Vorgehen

- **Je Phase eine Diagnose und eine unabhängige Gegenprüfung:**
  - Diagnose: Opus 5.5, Effort high.
  - Gegenprüfung: Opus 5.5, Effort max. Sie versucht jeden Befund zu widerlegen, meldet fehlende
    materielle Befunde nach und bewertet die Abdeckung.
- **Grundlage:**
  - P1–P7: Ausgangsstand `c4c2a4c`, ausgeführt in einem eigenen, schreibgeschützten Worktree.
  - P8–P10 und die phasenübergreifenden Übergänge (XT): Paket-A-Stand `93cd64d`.
  - **Einschränkung (Gegenprüfung P7-V3):** Zwei Subprozess-Tests (`test_U01` und
    `test_phase7a_cli_exit`) importierten über die editierbare Installation den Code des Hauptbaums.
    Einer davon führte außerdem `git status` im Hauptrepository aus. Für diese beiden Tests belegt das
    Ergebnis also nicht den Worktree.
- **Je Phase geprüft:**
  - dokumentierter Zweck mit Quelle;
  - tatsächlich ausgeführter Code- und Datenfluss;
  - vorhandene Belege, mindestens einer davon neu ausgeführt;
  - repräsentative End-to-End-Spuren;
  - mindestens eine Lücke, mit einem Gegenfall untersucht;
  - die Prüfpunkte (a)–(g).
- **Prüfpunkte (a)–(g):**
  - (a) Claim und Kontext vollständig, kein Gold-Leck.
  - (b) Rolle, Prompt und Profil passen zum ausgeführten Pfad.
  - (c) Zerlegung, Spans und Attribute überstehen die Übergänge.
  - (d) Gegenevidenz, fehlende Evidenz, Extraktionsmangel und Technik bleiben getrennt.
  - (e) Pflichtkontrollen laufen wirklich.
  - (f) Budget, Exklusivität und Resume halten.
  - (g) Installiertes Paket und sauberer Klon funktionieren.
- **Rohergebnisse:** [diagnosis/p1_p7_results.json](diagnosis/p1_p7_results.json) und
  [diagnosis/p8_p10_xt_results.json](diagnosis/p8_p10_xt_results.json), je mit Zeile und Gegenprüfung.
- **Probe-Skripte:**
  - Abgelegt in [diagnosis/p1_p7_probes/](diagnosis/p1_p7_probes/) und
    [diagnosis/p8_p10_probes/](diagnosis/p8_p10_probes/), zusammen mit den kleinen Textausgaben, soweit
    sie als Datei vorlagen. Die meisten P8–P10-Ausgaben gingen nur auf die Konsole und stehen in den
    Ergebnis-JSONs.
  - Ausgeschlossen sind Repo-, Paket- und historische Codekopien.
    - Geprüft: Kein archivierter Inhalt ist mit einem Git-Objekt der Historie identisch.
    - Kein `test_*.py` liegt außerhalb von `tests/`.
    - Ein `python -m pytest -q` aus dem Wurzelverzeichnis sammelt nur die Tests unter `tests/`.
  - **Grenze:** Die Probes verweisen auf Scratchpad-Pfade der Sitzung (Worktrees, Ausgaben). Für einen
    Neulauf müssen die Pfade angepasst werden.
  - **Dauerhafte, ohne Anpassung lauffähige Belege** sind die Regressionstests (siehe unten). Jeder
    davon scheitert am Code vor der Korrektur; die Ausnahme ist die Kontrolle für eingefrorene
    Datensätze.
- **Keine Modellaufrufe.**
  - Live-Pfade liefen nur mit Transport-Double und Wegwerf-Autorisierungen.
  - Gegen die echte Historie -002/-003 lief nur die schreibgeschützte Prüfung; Replays liefen auf Kopien.

## Matrix

| Phase | Dokumentierter Zweck | Ausgeführter Code-/Datenfluss | Belege (vorhanden + jetzt ausgeführt) | Befund / Wirkung | Korrektur / Restgrenze |
|---|---|---|---|---|---|
| P1 Output-Vertrag | Robuster Parser; abgeschnittene Ausgaben bleiben unvollständig | `runner.run_agent` → `output_contract.parse_structured_output` → P8/P9/P10 und Harness | 86 + 120 Tests; Abschneide-Sweep: 856 Varianten, 0 vollständig | **P1-F1 (materiell):** Bei zwei JSON-Analysen (Entwurf + Selbstkorrektur) gewinnt still der Entwurf. Betroffen sind 2 von 420 Sonnet-S1-Antworten in 5B (P1-A1, Nachtrag unten) | `multiple_objects`, auch für ein am Ende abgeschnittenes Objekt einschließlich einem nackten `{`. P8 unvollständig, P10 ohne Forensik, Harness-Klassifikation ungültig, Fingerprint bindet das Feld. Alte Datensätze werden wie bisher bewertet. P1-F2: Eine gecachte Analyse ohne Rohtext ist nie vollständig |
| P2 Provider-Vertrag | Nie werfende, normalisierte Provider-Antworten | Altadapter senden nur `prompt`; der Live-Builder sendet `prompt` + `context` | 120 Tests; eine Probe sendet einen Bibliotheksfall live über das Double | **P2-F1 (materiell, latent):** Kuratorkommentar im `context` (oft mit Goldlabel) ginge live an das Modell. Die P2-Gegenprüfung hielt das für derzeit nichtmateriell; P3, P6 und XT bestätigen „materiell, latent“ | Kuratierte Fälle werden im P10-Preflight (`input_preflight` 1.1) und beim Nachrichtenbau abgewiesen. Restgrenze unten (Punkt 3) |
| P3 Fallbibliothek | 50 Fälle, 4 Labels, Kuratorregel | YAML → Task → Harness/P10 | 189 Tests; 50 Fälle, 0 Duplikate | **F1 (materiell, latent)** = P2-F1: 18 von 48 aktiven Kontexten nennen ihr eigenes Goldlabel | wie P2-F1; alle 50 Bibliotheksfälle und alle 39 Fälle des Robustheitspools werden abgewiesen |
| P4 Lauf-Harness | Reproduzierbare Mehrfachläufe, Stabilitätsflags | `run_library` → `run_single` → `run_agent` | 126 Tests (nur 26 berühren den Harness); Fake-Lauf | **P4-F1 (materiell):** Der Harness nutzt still den Phase-8-Prompt, der `context` verlangt, den die Altprovider nicht senden. Eine Prompt-Identität wird nicht aufgezeichnet | Vorgabe wieder der historische Prompt; nur kontextfreie Prompts erlaubt. Prompt-Version und Bedingung stehen im Manifest; Version, Bedingung und System-Prompt-Hash stehen in jedem Datensatz |
| P5 Benchmark-Integrität (5A/5B) | Bedingungsbewusster Vertrag, versiegelter Holdout, Einmal-Läufe | `phase7a_real_run._run_registered_condition`, Lease, Resume | 305/306 Tests (der eine Fehlschlag kommt nur vom PYTHONPATH der Diagnose); Aggregate reproduziert; Holdout-Siegel geprüft | **P5-F1 (materiell, latent):** Die Einmal-Sperre hängt nur an der Lease-Datei. Bei verlorener Lease oder Abbruchresten lief eine zweite volle Charge | Ein Namespace mit Altartefakten ohne Lease wird verweigert (Finder-Metadaten ausgenommen). **Größer, offen:** Punkt 1 unten |
| P6 Kalibrierung/Konfidenz | Konfidenz übersteuert UNKNOWN nicht; Leck-Audit | Parser → Konfidenzzustand; `packet_integrity` | 331 Tests; 6.4A regeneriert (6.3-Beispiele weichen ab, P6-F2) | **P6-F1 (materiell, latent):** Das Leck-Audit rekonstruiert nur `prompt` (v1) und sieht den Live-`context` nicht | Leck an der Quelle geschlossen (P2-F1). `packet_integrity` bleibt eine Prüfung des historischen Pfads, der nur den Prompt sendet |
| P7 Robustheit/Release-Gates | Deterministische Darstellungs-QA-Gates | P8 `_phase7_controls` → Neuausführung in P10 | 431/432 Tests (1 Umgebung); Probes W1–W5 | **P7-F1/V1 (materiell):** `material=false` schaltet die Symmetrieprüfung ab; eine ausgelassene Gegenrichtung wird freigegeben | Gate `evidence_symmetry` 1.1.0: jede vom Elternbefund gebundene Evidenz zählt. **Größer, offen:** Punkt 2 unten |
| P8 Semantik | Getrennte Modell-/Host-Urteile, fail-closed | `assess_agent_result` → `evaluate_phase8` → Taxonomie | 235 Tests; Prompt-Pins geprüft; K12 ohne Abweichung | **P8-F1/AF1 (materiell):** Ein als nichtmateriell eingestuftes UNKNOWN (Konflikt oder einig) bestimmt allein das freigegebene Taxonomie-Label. **P8-F2 (materiell):** Die Rollen-/Beobachtungsprüfung C15 lief nur für Pflichtpropositionen | F1/AF1: Die Materialität umfasst das abgeleitete Label (Sensitivitätsprüfung in P9). F2: C15 gilt für jede Proposition. P8-F3: Brückengründe tragen Ordnungsnummern. Version AA-P8/1.2 |
| P9 Review | Konflikt- und Materialitätsrouting, begrenzte Reviews, nur menschliche Auflösung | `assess_case`, `execute_review`, Adjudikation | 164 + 35 Tests; Abnahme 21/21 | **P9-F1 (materiell)** = P10-F1. **P9-F2 (materiell, grenzwertig):** Die Modell-Adjudikation behauptete bei Live-Reviews „offline recording … first verdict withheld“ | F2: Herkunft und Unabhängigkeit werden aus der gebundenen Review-Position abgeleitet, auch für nie gesendete Reviews. P9-F5: Konflikte auf Claim-Ebene tragen Begründungen beider Seiten. Version AA-P9/1.2 |
| P10 Betriebspfad + Live | Lokaler Audit- und Freigabepfad, Live-Budget, Replay | `run_audit` / `_run_live`, Kontrollen, Projektion, Ledger | 107 Tests; Abnahme 21/21; Replay beider Historien | **P10-F1/G1 (materiell):** Das Replay der R1-Historie endete in 10 von 12 Fällen mit PREFLIGHT_BLOCKED, mit irreführender Ursachenangabe (Herkunft statt nie ausgeführtem Review). Ein unterbrochener Live-Review ergab nie ein Bundle. **K1:** Replay war nur aus dem Originalpfad möglich | Neue Replay-Regel; R1 ergibt 2 READY / 10 REVIEW_REQUIRED, alle gültig. Die Verzeichnisbindung gilt nur noch live. Beim Replay sind festgeschriebene IDs an ihre Bytes gebunden, und der Ledger-Hash steht in der Replay-Evidenz. Der CLI-Replay schreibt seinen Zustand neben die Ausgabe |
| XT Übergänge | Ein kanonischer Pfad P1→P10 | Offline, Live (Double), Replay, Harness | 613 Tests; vier End-to-End-Spuren (T1, T2, T2b, T3) | **XT-F1/F2** = P2-F1 und P4-F1; **XTV-A1/A2** = P10-F1 und P1-F1 | siehe oben |

## Abdeckung laut Gegenprüfung (noch offene Lücken)

- **Ausreichend:** P1, P2, P3, P6, P7, P8 und P9.
  - Auch bei ausreichender Abdeckung offen: **P7 Lücke 4.** Die vom Produzenten gelieferte
    `allowed_summary_strength` des Elternbefunds wird auf dem P8-Pfad vom Host nicht abgeleitet. Das
    wurde nicht untersucht, obwohl dieselbe Gate-Familie die `material`-Umgehung (P7-F1) hatte.
  - Ebenfalls offen: **P3 Lücke 4.** Der Fake-End-to-End-Lauf hat Phase 8 nie ausgeführt; alle 48
    Datensätze sind `not_executed`.
- **Mit Lücken: P4, P5, P10 und XT.** Noch offen:
  - **P4:**
    - Nur 26 der 126 ausgeführten Tests berühren den Harness.
    - Die Vergleichbarkeitsverzerrung durch den Prompt wurde nicht beziffert.
    - Der Live-Pfad des Harness (max_tokens, temperature/thinking) ist nur dokumentarisch geprüft.
  - **P5:** 5A-Diagnostik und 5R sind nur auf innere Konsistenz prüfbar, weil die rohe
    Laufbibliothek nicht in Git liegt.
  - **P10:**
    - Es gibt keine feldgenaue P7→P10-Projektionsspur.
    - Die CLI-Befehle `audit review` und `audit release` wurden nur über die API-Funktionen geprüft.
  - **XT:**
    - Volle Suite und Reproduktion mit sauberem Klon und Wheel liefen in der Diagnose nicht.
    - Beide folgen als verbindlicher Gesamtlauf nach der letzten Produktänderung.
- **Geschlossen:**
  - P10 Lücke 1 (unterbrochener Review, G1) durch die Korrekturen.
  - P10 Lücke 2 (Paketdrift) durch die Probe der Gegenprüfung; der Befund G2 selbst bleibt als Punkt 5
    offen.
  - XT Lücken 1–3 (Replay der Historie, unterbrochener Review, Parserübergang) durch die Korrekturen.

## Behobene Befunde und ihre Belege

Regressionstests:
- [tests/test_package_b_regressions.py](../../tests/test_package_b_regressions.py): 29 Tests.
- Abschnitt „Package B“ in [tests/test_phase10_live.py](../../tests/test_phase10_live.py): 5 Tests.
- Die Kritik prüfte mit Mutationen, dass jede Korrektur mindestens einen Test scheitern lässt; die
  Lücken aus Runde 1 sind in Runde 2 geschlossen.

| Befund | Änderung | Test |
|---|---|---|
| P1-F1/A2 | `output_contract.multiple_objects` (zwei Zäune, zwei Rohobjekte, abgeschnittenes Folgeobjekt inkl. nacktem `{`, nackter Zaun vor JSON-Zaun); Verbraucher in `phase8_pipeline`, `phase10_pipeline.reconstruct`, `run_library`, `phase7a_execution.is_classification_valid`; `record_fingerprint` bindet das Feld, wo es vorhanden ist | `test_P1_*`, `test_BF4_*`, `test_BF8_*` |
| P1-F2 | Eine gecachte Analyse ohne Rohtext ist nie vollständig (jeder `finish_reason`) | `test_P1_F2_*` |
| P2-F1/P3-F1/P6-F1/XT-F1 | `anthropic_live.benchmark_fields` + `build_user_message`, `phase10_pipeline.preflight` (`input_preflight` 1.1) | `test_P2_P3_*` |
| P4-F1/XT-F2 | `run_library`: `LIBRARY_PROMPT_VERSIONS`, `--prompt-version`, Identität in Manifest und Datensätzen | `test_P4_*` |
| P5-F1 | `phase7a_real_run._run_registered_condition`: Ein Namespace ohne Lease, aber mit Altartefakten wird verweigert; `.DS_Store` allein zählt nicht | `test_P5_*`, `test_BF6_*` |
| P7-F1/V1 | `artifact_binding`: Symmetrieprüfung und Population ohne `material`-Ausnahme, Gate 1.1.0 | `test_P7_*` |
| P8-F1 | `phase9_review._decides_derived_label` | `test_P8_F1_*` |
| P8-AF1 | wie P8-F1, für ein einiges UNKNOWN am Auslöser | `test_BF5_*` |
| P8-F2 | `phase8_semantics._validate_semantic_trace`: C15 für jede Proposition | `test_P8_F2_*` |
| P9-F2 | `phase9_adjudication._model_review_statements` (offline, live, Replay, nie gesendet) und Vermerk im P9-Versuch (`phase9_runtime`) | `test_a_live_review_adjudication_…`, `test_a_refused_live_review_…`, `test_P9_F2_offline_…` |
| P10-F1/G1, P9-F1/A1, XTV-A1, K1 | `phase10_live.review_allowance` (Replay-Regel), `load_authorization` (Verzeichnisbindung nur live, Pins beim Replay), `ReplayProvider` (`replay_ledger_sha256`), `phase10_cli` (Replay-Zustand neben der Ausgabe) | `test_replay_from_a_copy_…`, `test_an_interrupted_live_review_…`, `test_cli_replay_keeps_…` |
| Versionen | AA-P8/1.2, AA-P9/1.2; Registry `phase8_semantics_taxonomy`/`phase9_history_review` 1.2, `input_preflight` 1.1, `evidence_symmetry` 1.1.0; gespeicherte 1.1-Fallzustände scheitern geschlossen | `test_BF2_*`, `test_registry_versions_of_package_b` |
| P8-F3, P9-F5 (nichtmateriell, eigene Paket-A-Stellen) | Brückengründe mit Ordnungsnummer bei der Erzeugung; Claim-Konflikt mit Begründungen | `test_P8_F3_*`, `test_P9_F5_*` |

## Nachtrag zu früheren Deutungen (historische Artefakte unverändert)

**Phase 5B, Sonnet S1** (`analysis/phase5b_sonnet_full_replication/run/sonnet/PHASE5B_SONNET_S1_FINAL_REPORT.md` §11–13):
- **Ursache:** Zwei Antworten (P7A-BND-018 Lauf 3, P7A-PRT-08-P2 Lauf 4) enthalten nach
  „CORRECTION AFTER SELF-CHECK“ beziehungsweise „CORRECTED RESPONSE“ eine zweite JSON-Analyse.
  - Entwurf: `mechanism_vs_evidence`, Konfidenz 0,75.
  - Korrektur: `overclaim`, Konfidenz 0,85 beziehungsweise 0,92.
  - Gezählt wurde der Entwurf.
- **Neuberechnung:** in zwei Lesarten, entweder beide Antworten als mehrdeutig ausschließen oder die
  eigene Korrektur des Modells werten.

| Kennzahl | veröffentlicht | Ausschluss | eigene Korrektur |
|---|---|---|---|
| Einstimmige Einheiten | 84/84 | 82/84 | 82/84 |
| Antwortgenauigkeit | 350/420 = 0,8333 | 350/418 = 0,8373 | 352/420 = 0,8381 |
| Brier | 0,14902 | 0,14704 | 0,14641 |
| ECE-5bin | 0,10243 | 0,09933 | 0,09831 |
| Mittlere Konfidenz | 0,9358 | 0,9367 | 0,9364 |
| Einheiten-Modalgenauigkeit | 70/84 | 70/84 | 70/84 |
| Δ S0→S1 einstimmig | +2 | +0 | +0 |
| Δ S0→S1 Antwortgenauigkeit | +0,0548 | +0,0587 | +0,0595 |
| Δ S0→S1 Brier | −0,0522 | −0,0542 | −0,0549 |
| Δ S0→S1 ECE-5bin | −0,0659 | −0,0690 | −0,0700 |
| ECE-10bin | 0,10243 | 0,09933 | 0,09831 |
| Δ S0→S1 ECE-10bin | −0,0725 | −0,0756 | −0,0766 |

- **Grundlage der Deltas:** die eingefrorenen S0-Werte aus `sonnet_historical_comparison.json`
  (Antwort 0,7786, Brier 0,20126, ECE-5 0,16831).
- **H1↔S1 (§14–15, laut Bericht der sauberere Vergleich), veröffentlicht → Ausschluss / Korrektur:**
  - Δ Replikationsgenauigkeit: −0,0952 → −0,0913 / −0,0905.
  - Δ Brier: +0,0809 → +0,0789 / +0,0782.
  - Δ ECE-5: +0,0955 → +0,0924 / +0,0914.
  - Δ ECE-10: +0,0862 → +0,0831 / +0,0821.
  - Δ mittlere Konfidenz: +0,0002 → +0,0011 / +0,0009.
  - Δconf je Einheit (S1−H1): BND-018 −0,060 → −0,025 / −0,040; PRT-08-P2 −0,140 → −0,125 / −0,106.
- **Vierfeldervergleich (§16–17):** Die S1-Spalte (Brier, ECE-5, ECE-10, mittlere Konfidenz) und
  ΔSonnet verschieben sich entsprechend; ΔSonnet mittlere Konfidenz −0,009 → −0,008.
- **Unverändert:** Richtungen aller Vergleiche, Einheiten-Modalgenauigkeit, Modal-Delta (+0,0595),
  Übergangskategorien und Per-Gold-Einheitenwerte.
- **Quellen:**
  - Gegenprüfung P1-A1: `diagnosis/p1_p7_probes/P1/verify/s1_counterfactual.py`. Dieses Skript setzt
    die Korrekturkonfidenzen fest ein.
  - Unabhängige Nachrechnungen der Paket-B-Kritik (zwei Runden, auch ohne Projekt-Metrikcode):
    Korrekturkonfidenzen aus dem Rohtext gelesen; alle Werte der Tabelle und der H1↔S1-Angaben stimmen.
- **Abgrenzung:** Die eingefrorenen 5B-Dateien bleiben unverändert. Der Parser kennzeichnet solche
  Antworten jetzt; alte Datensätze ohne das neue Feld werden wie bisher bewertet.

## Nicht behobene Punkte (größer oder nichtmateriell), priorisiert

1. **P5 (größer):** Der Klon eines autorisierten Commits kennt die verbrauchte Lease nicht. Dasselbe gilt,
   wenn der ganze Namespace im selben Checkout gelöscht wird (Diagnosefall C2: 420 neue Anfragen).
   - Autorisierungen haben kein Ablaufdatum.
   - Heute latent, weil beide 5B-Pläne verbraucht und widerrufen sind.
   - Ein neuer 5B-Lauf braucht vorher eine Bindung mit Ablaufdatum oder außerhalb des Baums.
2. **P7 (größer):** Die Evidenzrichtung hängt an der vom Modell vergebenen Rolle. Umetikettierung (R1)
   und Nicht-Extraktion (W0) bleiben möglich und sind als Grenze dokumentiert. P7 Lücke 4
   (`allowed_summary_strength`) ist ungeprüft.
3. **P2-F1, Restgrenze der Korrektur:**
   - Die Abweisung ist feldbasiert. Ein Bibliotheksfall, dessen Gold- und Kuratorfelder entfernt
     wurden, dessen Kuratorkommentar aber im `context` blieb, wird weiter gesendet.
   - Kuratortext innerhalb von `context` erkennt der Code nicht.
   - Abhilfe wäre ein ausdrückliches Audit-Eingabeschema.
4. **P2-F2, Rest auf dem alten Run-CLI:** `agent-arena run` (`runner.run_task`) nutzt mit den Altadaptern
   weiter den Phase-8-Prompt ohne `context`. Korrigiert wurde nur der Bibliotheks-Harness (P4-F1).
5. **P10-G2:** Ändert sich nach einem Live-Review der Paketaufbau, wird dessen Replay PREFLIGHT_BLOCKED;
   die Meldung klingt nach Manipulation. Ebenso blockiert ein terminaler Review-Slot mit fehlender
   Aufnahme. Das wirkt künftig, nicht auf die heutige Historie.
6. **P10-F3:** Ein Bundle aus einem Git-Checkout scheitert bei der Prüfung unter einem installierten
   Paket mit bytegleichen Modulen. Das schließt geschlossen, aber die Meldung nennt die falsche Ursache.
7. **P9:**
   - F3: Ein unklarer Abschluss während des Requests wird als „denied“ statt „unklar“ festgehalten.
     Schon ein Absturz zwischen `ledger.reserve` und dem Speichern von „begun“ reicht.
   - F4: Offline wird die Prompt-Version des Reviews nicht persistiert.
   - F6: Der Pfad für nichtmaterielle Konflikte ist ungetestet.
   - F7: Veraltete Doku.
   - I2: Das Löschen des ganzen P9-Zustands gewährt offline eine neue Erlaubnis.
8. **XT-F3:** Fehlgeschlagene P10-Kontrollen behalten einen fest verdrahteten, erfolgsartigen
   Begründungstext.
9. **P1–P7, nichtmateriell:**
   - **P1-A3:** Eine gültige Roh-JSON-Antwort mit ``` in Zeichenketten wird falsch zerlegt.
   - **P1-A4:** Eine Selbstkorrektur über einen doppelten Top-Level-Schlüssel nimmt still den letzten
     Wert; `multiple_objects` erkennt das nicht.
   - **`multiple_objects` ist bewusst vorsichtig:** `{"` oder ```json in Prosa kennzeichnet auch eine
     einzelne Analyse. Auf allen aufgezeichneten Ausgaben gibt es keinen Fehlalarm.
   - **P2-V1 (kanonischer Pfad):** Ein Zeilenumbruch am Ende eines YAML-Blocks bricht
     `exact_claim_text` und führt zu ANALYSIS_INCOMPLETE.
   - **P2-V4 (Live-Pfad):** Abgewandelte Begrenzungs-Tags passieren.
   - **P2:** Normalisierung der Altadapter (V2, V3, I3).
   - **P3:** Intake-Checkliste nicht erzwungen; Taxonomie-Kuratorregel widerspricht der Leitlinie (V1, V2).
   - **P4:** Stabilitätsflags mischen Technik und Qualität; Doku-Drift (F2, F3).
   - **P5:** Konstanten in `execution_evidence.json` (V2); falsche Überschrift im Sonnet-Vergleich (V1).
   - **P6:** Das Leck-Audit meldet bei null geprüften Fällen PASS (A1); die 6.3-Beispiele
     regenerieren nicht mehr bytegleich (F2).
   - **P7:** F2, I3, V2–V4.

   Die vollständige Liste mit Belegen steht in den Ergebnis-JSONs.
10. **Live-Grenzen:**
    - K2: Ein nie gesendeter Review wird mit allgemeinem Grund nachgespielt; Status und Positionen
      stimmen.
    - K3: Live-Ausgaben sind nur aus diesem Checkout möglich.
    - Beim Replay ist eine festgeschriebene Historie an ihre Bytes gebunden. Nicht festgeschriebene
      Historien tragen den Ledger-Hash in der Replay-Evidenz.

## Offene Restbefunde der letzten Nachprüfung (nach Runde 2, nicht mehr korrigiert)

- **Ergebnis der letzten erlaubten Nachprüfung:** kein materieller Befund. Alle früheren Befunde sind
  behoben; die Ausnahme ist RE2, nur teilweise behoben.
- **Prüfung:** zwei Kritiker, Opus 5.5 mit Effort max.
  - 44 Mutationen; alle bis auf zwei Versionstexte (SF1) werden von Tests gefangen.
  - `python -m pytest -q` aus dem Wurzelverzeichnis: 2470 bestanden, im echten Baum und in einem sauberen
    Klon einer Paket-B-Kopie.
  - Nachtrag reproduziert, echte Historie unverändert.
- **Warum nicht korrigiert:** Der Auftrag erlaubt höchstens zwei Korrekturrunden. Die folgenden Punkte
  sind deshalb unten offen dokumentiert, statt still nachgebessert zu werden.

- **SE1 (klein, Rest von RE2):** Archiviert sind nur `.py` sowie `.txt`/`.out`/`.log`-Ausgaben.
  - Kleine JSON-Zusammenfassungen (zum Beispiel XT `trace*_summary.json`, `acc/results.json`, P10
    `rows.json`) liegen nur im Sitzungs-Scratchpad.
  - Ihr Inhalt steht zusammengefasst in den Ergebnis-JSONs.
- **SE2/SF2 (Notiz):** Gegen `93cd64d` bestehen zwei Regressionstests. Beides sind Kontrollen gegen
  Fehlalarm:
  - eingefrorene Datensätze;
  - ein Namespace nur mit `.DS_Store` (`test_BF6`), der erst gegen die Sperre aus Runde 1 scheitern kann.

  Oben ist nur die erste Kontrolle genannt.
- **SE3 (Notiz):** „Richtungen aller Vergleiche“ gilt außer für die Einstimmigkeit (+2 → 0). S0-ECE-10
  stammt aus `h1_s1_and_four_cell_analysis.json`.
- **SE4 (Notiz):** Addendum §5 beschreibt den Vermerk im P9-Versuch noch allgemein. Für einen nie
  gesendeten Review lautet er seit Runde 2 „No review request sent (…); nothing generated or supplied.“
- **SE5 (Notiz):** Die Entwicklungsprüfungen aus Runde 2 stehen jetzt im CHECKPOINT. Die Zahl 2461 aus
  Runde 1 war ein Lauf von `pytest -q tests`.
- **SF1 (Notiz):** Zwei Stellen der Versionskennung AA-P8/1.2 haben keinen eigenen Test:
  `phase8_pipeline.unavailable` und der Begründungstext von `evaluate_phase8`. Routing und Freigabe lesen
  sie nicht.
- **SE6/SF3 (Notiz, vor Paket B, außerhalb seines Diffs):**
  `tests/test_bounded_harness_mission.py::test_requests_real_sdk_wire_and_shared_C` schreibt bei jedem
  Gesamtlauf `analysis/harness_value_20260913/evidence/dry_request_captures.json` neu.
  - Heute bytegleich; nur die Änderungszeit wechselt, `git status` bleibt sauber.
  - Abhilfe für später: Ausgabe nach `tmp_path` und Vergleich mit der getrackten Datei.
