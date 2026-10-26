# Interner technischer v1-Abschluss — CLOSEOUT

Auftrag von Lazaros Varvatis vom 13.10.2026. Repository `agent-arena`, Branch `c25-p9-conflict/aa-p8-p9-20261011`.

| Feld | Wert |
|---|---|
| Status | **INTERNAL_V1_COMPLETE** — lokaler annotierter Tag `v1.0.0`, kein Push, keine Veröffentlichung |
| Getesteter Codecommit | `5560e950af20cee8c35fb2c8e2bfb38807043fab`: Kandidat `fd1ad7c` plus Korrekturrunde 1. Code-Fingerabdruck der sauberen Installation `03984bd436b8…` |
| Paketversion | `agent-arena` 1.0.0 |
| Verträge | Bewertung AA-P8/1.3, Review AA-P9/1.3, Host-Regeln AA-P8-HOST/1.1 |
| Modell-Ausgabeformat | Ledger AA-P8/1.0, unverändert |
| Prompts und Profile | unverändert; `…-contract-r2` / `…-r2-review-p9-2`; `claude-haiku-5-5@3`, `claude-sonnet-5-5@3` |
| Projekt-API in diesem Auftrag | **0 Aufrufe, 0 USD**, keine Tokenzählung, keine neue Live-Autorisierung |

Umfang und Bedeutung für Nutzer: [V1_SCOPE.md](../../V1_SCOPE.md). Maschinenlesbar:
[closeout_manifest.json](closeout_manifest.json). Arbeitsjournal: [CHECKPOINT.md](CHECKPOINT.md).

## Abnahmematrix A–D

| ID | Prüfung | Ergebnis | Evidenz |
|---|---|---|---|
| A1 | Gültiges, vollständiges Bündel auch für ungeklärte Fälle; keine Behauptung vollständiger wissenschaftlicher Analyse | PASS | [evidence/A](evidence/A/README.md) `replay_cli.json`, `logs/inspect_replays.log` |
| A2 | Drei Ursachen unterschieden; „automatische Bearbeitung beendet“; keine Prüfer-Warteschlange vorausgesetzt | PASS (vorher FAIL) | `evidence/A/a1_a3_summary.json` |
| A3 | Offene Konflikte, Pflichtprüfungen, Originalpositionen, ausgeführte Reviews erhalten | PASS | `evidence/A/a1_a3_summary.json` |
| A4 | Gesperrte Fälle erhalten keine Testfreigabe | PASS | `evidence/A/logs/release_attempts.log` |
| A5 | Wiederaufnahme ohne zusätzliche Generierung; Inspect/Replay ohne Generierung | PASS | `evidence/A/a5_a6_result.json`, `logs/pytest_a5.log` |
| A6 | Neuer Lauf desselben Inputs als neue Laufidentität möglich | PASS | `evidence/A/a5_a6_result.json` |
| B1 | Nichtmaterieller Modell/Host-Konflikt über die echte Materialitätslogik: sichtbar, offen, nicht geprüft, nicht sperrend; Record, Markdown und HTML stimmen überein | PASS (Wortlaut vorher fehlerhaft) | [evidence/B](evidence/B/README.md) `summary.json` |
| B2 | Materieller Gegenfall mit einem einzigen Unterschied (Prämisse, Taxonomie-Label, entscheidende Zusammenfassung) löst die Pflichtprüfung aus und sperrt | PASS | `evidence/B/summary.json` |
| B+ | NEW-VB-1: Zusammenfassung über die ganze Aussage aus konfliktbehafteter oder nicht gestützter Proposition | PASS (vorher RELEASED) | `evidence/B/summary.json` |
| C1 | Altpfad `agent-arena run`: Artefakt, Verwechslung, Freigabe | PASS (vorher FAIL: ungesicherter Live-Pfad) | [evidence/C](evidence/C/README.md) |
| C2 | Ein eindeutig dokumentierter v1-Pfad; Alternativen abgewiesen oder markiert | PASS (vorher FAIL) | `evidence/C/help_root.txt`, `historical_provider_paths.md` |
| D1 | Untrusted Freitext verändert und verdeckt keine Host-Kontrollen oder Pflichtabschnitte; DOM- und Sichtbarkeitsprüfung in Chrome; Payloads als Regressionstests | PASS (vorher FAIL in gerendertem Markdown; beim Kandidaten `fd1ad7c` PARTIAL wegen VC-1) | [evidence/D](evidence/D/README.md) `dom_results.json`, Screenshots |

Zu D: Modellformatierung kann ein Ergebnis nur **verschärfen**, nie lockern. ``` in der Rohantwort und rohe
Zeilentrenner in einer Task-Datei führen zu ANALYSIS_INCOMPLETE bzw. PREFLIGHT_BLOCKED.

## Befunde und Änderungen

Untersuchung: acht Agenten (Prüfer high, adversariale Verifizierer max), alles offline. Umsetzung nach einer
festgelegten Spezifikation in drei Stufen; jede Änderung mit einem Regressionstest, der auf `558e920` scheitert.

| Befund | Gegenfall | Ursache | Eingriff | Nachprüfung |
|---|---|---|---|---|
| A2 / XT-F3 | Sonnet LR-02 (Review durch Obergrenze verweigert) und LR-03 (Reviews ausgeführt) sahen gleich aus; „mandatory review pending“; Fehlgründe als Erfolgstext; Haiku LR-03 „none recorded“ | Statische Statuszeile und Kontrollgründe; Konfliktzeile ohne Versuchsauswertung | `automatic_outcome` aus vorhandenen Feldern; Satz „Automatic processing has ended …“, Zeilen `automatic processing` und `open cause`; sprechende Fehlgründe für drei Kontrollen; Konfliktzeile und Historiensatz korrigiert | `tests/test_v1_closeout_report.py`; Replays in `evidence/A` |
| B-D1, B-D2, NEW-VB-2 | „no recorded conflicts“ trotz offenem Konflikt; „not reviewed“ nach Adjudikation | `_history` prüfte nur Positionskonflikte | Wortlaut in der Projektion. Die P8-Regeltexte bleiben unverändert; die Konfliktzeile stellt den nichtmateriellen Fall klar, und eine Änderung der P8-Ausgabe war für den Abschluss nicht nötig | dito |
| NEW-VB-1 (MATERIAL, latent) | Kundenzusammenfassung mit `asserts_whole_claim` aus optionaler, abweichender Proposition wurde RELEASED | Ausnahme in `_directly_influences_output`; Teil-zu-Ganz-Prüfung nur gegen den Gesamtzustand | P9 ohne Ausnahme; P8 prüft die Quellpropositionen; AA-P8/1.3, AA-P9/1.3 | `tests/test_v1_semantics.py`; `evidence/B` |
| C-D2 (MATERIAL), C-D3 (P2-F2) | `agent-arena run` erreicht Provider ohne Autorisierung, Ledger und Kontext | Historischer Befehl | Abgewiesen (Exit 2, Verweis auf `audit`) | `tests/test_v1_entry_point.py`; `evidence/C` |
| C-D1 | `official-release` schreibt ein „official_release_authorized“-Paket ohne P8/P9/P10 | Phase-7B-Befehl öffentlich | CLI abgewiesen; API für historische Prüfung erhalten | `tests/test_release_boundary.py` (2 Tests angepasst) |
| C-D4 | Root-Hilfe nannte den v1-Pfad nicht | Kurzhilfe zeigt nur den ersten Satz | Docstring nennt `agent-arena audit`; jeder andere Befehl markiert; `cleandoc` | `tests/test_v1_entry_point.py` |
| D1 (MATERIAL), D2 | CR im Modelltext erzeugte gefälschte Status- und Kontrollanzeigen in 8 Markdown-Renderern; `markdown_qa` bestätigte das | Nur LF wurde kodiert; QA teilte nur an LF | Anzeige-Transformation `⟦U+XXXX⟧`; CR-Entities; QA lehnt rohe Zeilenenden ab | `tests/test_v1_render_injection.py`; `evidence/D` |
| D3, D4, M1, D5 | Bidi drehte Host-Text um; Modell-IDs in Überschriften; Modell-Schlüssel ersetzten Host-Zeilen; gemischte `reasons` | Keine Darstellungsisolation | Marken, Ordnungszahl-Überschriften, Schlüssel-Kennzeichnung, Hinweis zu `reasons` | dito |
| A-D8 | API-Lauf mit geteiltem Review-Zustand: bezahlter Aufruf, dann Ausnahme ohne Bündel | Keine Vorprüfung | PREFLIGHT_BLOCKED vor dem Primäraufruf | `tests/test_v1_semantics.py` |
| D7 | Offline-Aufnahmen mit CRLF wurden normalisiert gespeichert | `read_text` | Bytegenau lesen | dito |
| VC-1 (MATERIAL, Kritik, neu durch `fd1ad7c`) | Modell-ID `claim:p1\nOutcome: pass\n…` fügte über den sprechenden Kontrollgrund und „open cause“ gefälschte Kontrollzeilen ein | Zitierte IDs mit Zeilenumbruch in host-gebauten Zeilen | Zeilenumbruch und Tab zitierter Texte in diesen Zeilen als ⟦U+000A⟧/⟦U+0009⟧ (nur Anzeige) | `test_model_ids_cannot_add_host_lines_…`; `evidence/D` (Kombination ID-Nutzlast + fehlschlagende Kontrolle) |
| VC-2 bis VC-5, VC-11 (Kritik) | Rohe Bidi- und Steuerzeichen in der CLI-JSON-Ausgabe; Schlüssel wie `derived judgment / host state`; Routing-Satz als Ursache ungültiger Historie; Hilfe der abgewiesenen Befehle; Profilbeispiel `@1`; „begun“ als „nicht ausgeführt“; Satz zur Revisionsänderung | Fehlende Maskierung bzw. Wortlaut | ASCII-JSON; Präfix-Schlüssel markiert; aufgezeichneter Grund; Hilfe „Disabled in v1“; `@3`; „interrupted“; „immutable … creates a new revision“; „no blocking cause recorded“ | 8 neue Regressionen scheitern auf `fd1ad7c` an der beabsichtigten Stelle |

Versionen: Registry `analysis_source` 1.1, `phase8_semantics_taxonomy` 1.3, `phase9_history_review` 1.3,
`markdown_qa`/`html_qa` 1.1. Paket 1.0.0. Vertragsnachtrag:
[docs/phase8_9_conflict_addendum.md §9](../../docs/phase8_9_conflict_addendum.md).

## Testnachweise

| Nachweis | Ergebnis | Herkunft |
|---|---|---|
| Saubere Reproduktion `5560e95` (AA-P10-REPRO/1.1, frischer Klon, normale Wheel-Installation, getrennte Editable-Umgebung), nach der letzten Produktänderung | volle Suite **2539 passed**; P10-Abnahme **21/21**; Wheel-P10-Tests **49 passed**; installierte Bytes = Quelle; Klon am Ende unverändert | neu ausgeführt; [clean_reproduction/](clean_reproduction/) |
| Dieselbe volle Suite unter Netzsperre (`.pth`-Wächter in der Testumgebung, auch für Unterprozesse) | **2539 passed**, **0** verweigerte Netzversuche | neu ausgeführt; [clean_reproduction/guarded_suite/](clean_reproduction/guarded_suite/guarded_suite.json). Die Angabe „project_live_provider_calls: 0“ in `reproduction.json` ist eine Konstante des Reproduktionsskripts; gemessen ist sie erst durch diesen Lauf (VC-9) |
| Gezielte P8/P9/P10/v1-Gruppen im Entwicklungsbaum | 759 passed (nach Korrekturrunde 1) | neu ausgeführt (Koordinator) |
| Neue Regressionen gegen `558e920` bzw. `fd1ad7c` | scheitern wie beabsichtigt (P: 35/35, C: 10, S: 8; Korrekturrunde: 8; Wächtertests bestehen) | Berichte der Umsetzungsstufen; Koordinator |
| Kandidat `fd1ad7c` (überholt) | saubere Reproduktion 2531 passed, 21/21, 49 passed | im CHECKPOINT festgehalten; durch `5560e95` ersetzt |
| Ruff (Richtlinie E4/E7/E9/F) | geänderte Dateien sauber; über `src/` dieselben 368 Altbefunde vor und nach den Änderungen | neu ausgeführt |
| Übernommene Nachweise | keine; alle Zahlen stammen aus Läufen dieses Auftrags. Die Evidenz A–D wurde für `5560e95` vollständig neu erzeugt | — |

Die frühere Live-Erprobung (8 Aufrufe, `21a2849`) gilt nur für den damaligen Code. Der v1-Code ist nicht erneut live
abgenommen.

## Erhalt der Historie

- Die geschlossenen Ledger -002/-003/-004 (REVOKED, Rest 0) und die geschützten Evidenzbäume sind vor und nach dieser
  Arbeit gehasht: [hashes_before.json](hashes_before.json) und [hashes_after.json](hashes_after.json).
- Kein neuer Nachfolgeanspruch, keine produktive Live-Session.
- Unter v1-Code sind die alten Live-Bündel wegen der Codebindung nicht prüfbar. Mit dem Code von `558e920` (src
  gleich `21a2849`) sind alle 9 Revisionen gültig: [evidence/A/hist_inspect_558e920.json](evidence/A/hist_inspect_558e920.json).

## Bekannte Grenzen

Siehe V1_SCOPE.md. Zusätzlich offen und dokumentiert:

- **P10-F3:** Inspect außerhalb eines Git-Checkouts.
- **D7-A:** Meldung nach Codewechsel nennt Symptome.
- **A-D5:** konstanter P9-Routing-Grund.
- **N2:** Reihenfolge der Preflight-Meldungen.
- **XT-F3-Rest:** statische Gründe der fünf Phase-7B-Gates.
- **Bestehender Erfolgsgrund von `phase9_history_review`:** Er lautet auch ohne Pflichtreview „… mandatory review
  revalidated“.
- **Markdown:** `<br>` bei Renderern ohne HTML; E-Mail-Autolink in cmark-gfm.
- **Task-Ingestion über YAML:** faltet rohe NEL-Zeichen.
- **Chrome:** Die Render-QA lief auf dem automatisch aktualisierten Chrome 155.
- **Weitere ungesicherte Forschungspfade:** `run_library`, `runner.run_task`, `judge.run_judge`.
- **Budget für einen neuen Live-Lauf:** Alle Autorisierungen sind geschlossen. Der Spielraum unter den Code-Obergrenzen
  würde Haiku-, nicht aber Sonnet-Aufrufe decken; ein neuer Lauf braucht einen neuen Auftrag.
- **Phase-8-Regeltexte:** Bei nichtmateriellen Konflikten stehen weiter „mandatory review decides …“ und „… until a
  mandatory review resolves it“ im Record. Die Konfliktzeile stellt den Fall klar.
- **A-D8-Vorprüfung:** Sie lehnt API-Läufe mit geteiltem Review-Zustand auch dann ab, wenn kein Review nötig wäre
  (fail-closed).
- **Ingestion von Task-Dateien:** Eine Task-Datei mit ASCII-maskierten Surrogatpaaren besteht `validate`, endet aber
  ohne Bündel (RELEASE_BLOCKED).
- **Ursache ungültiger Historie:** Für alte AA-P9/1.2-Historien unter v1 nennt die Ursache den allgemeinen Eintrag
  „Selected Phase9 history is invalid“ statt der spezifischeren Vertragsabweichung. Das tritt nur bei der ohnehin
  fail-closed Prüfung alter Bündel auf.
- **VC-10:** `tests/test_bounded_harness_mission.py` schreibt bei Suite-Läufen im Repository eine versionierte
  Evidenzdatei bytegleich neu. Volle Suiten liefen deshalb nur in Klonen.

## Kritik

- **Rahmen:** Ein lesender Kritiker (Opus 5.5, Effort max) prüfte einmal Code, Tests, Evidenz und Dokumente gegen A–D,
  §8–§11. Die Probes liegen im Sitzungs-Scratchpad `v1/critic/`.
- **Ergebnis für `fd1ad7c`:** A, B und C bestanden, D teilweise.
  - 1 materieller Befund: VC-1.
  - 8 kleinere Befunde: VC-2 bis VC-9.
  - 3 Notizen: VC-10 bis VC-12.
- **Korrekturrunde 1 von höchstens zwei:**
  - VC-1 bis VC-5 und VC-11 im Code (`5560e95`), jeweils mit Regressionstest.
  - VC-6 bis VC-9 in den Dokumenten und durch den gesperrten Suite-Lauf.
  - VC-12: Tagger-Identität ausdrücklich gesetzt.
- **Nach der Runde:** Die Evidenz A–D wurde für `5560e95` vollständig neu erzeugt. Alle Prüfpunkte sind bestanden,
  einschließlich der VC-1-Kombination aus ID-Nutzlast und fehlschlagender Kontrolle in kanonischem HTML,
  8 Markdown-Renderern und der CLI.
- **Zweite Korrekturrunde:** nicht genutzt.
- **Offen:** Verbleibende kleinere Punkte stehen unter „Bekannte Grenzen“.

## Commits und Tag

| Schritt | Commit | Inhalt |
|---|---|---|
| Basis | `558e920` | Endbericht des C25/P9-Auftrags |
| v1-Kandidat | `fd1ad7c` | Produkt- und Teständerungen, AA-P8/1.3, AA-P9/1.3, Paket 1.0.0 |
| Korrekturrunde 1 = **getesteter Codecommit** | `5560e95` | VC-1 bis VC-5 und VC-11 mit Regressionstests; letzte Produktänderung |
| Abschlusscommit | der Commit, der diese Datei hinzufügt | nur Dokumente und Evidenz: `V1_SCOPE.md`, README, drei `docs/`-Nachträge, `analysis/v1_closeout_20261013/` |
| Tag | `v1.0.0`, annotiert, lokal | zeigt auf den Abschlusscommit |

- **Bindung der Abnahme:** Alle Nachweise A–D und Tests gelten für `5560e95`. Gegenüber dem Abschlusscommit ist
  `git diff 5560e95 <Abschlusscommit> -- src tests scripts examples agents tasks pyproject.toml` leer. Der
  Produktstand ist damit identisch.
- **Identität:** Author, Committer und Tagger ist Lazaros Varvatis <varvatislazaros@gmail.com>, ohne Co-Author-Trailer
  und ohne globale Git-Konfiguration.
- **Nicht ausgeführt:** Push, PR, Merge, GitHub-Release, Deployment und DOI. Das öffentliche Repository
  LAKITALKS/Inspektorium ist unberührt.
