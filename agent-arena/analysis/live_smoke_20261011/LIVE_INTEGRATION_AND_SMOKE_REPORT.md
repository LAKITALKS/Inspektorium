# Live-Anbindung und Live-Funktionstest — Abschlussbericht

Stand: 11.10.2026, mit Nachtrag zum Reparaturzyklus R1 (§11) nach der Statusanfrage vom selben Tag.
Auftrag: „AGENT ARENA — Live-Anbindung und Live-Funktionstest vollständig abschließen".
Vertrag: [AA-P10-LIVE/1.0](../../docs/phase10_live_addendum.md), Reparaturrevision R1 in §8 des Addendums.

| Ergebnis | Urteil |
|---|---|
| Implementierung und Offline-Nachweise (Revision 1 und R1) | **LIVE_INTEGRATION_PASS** |
| Live-Smoke nach vorab festgelegten technischen Kriterien | **LIVE_SMOKE_PARTIAL** |
| Strikter P8-Vertrag, Revision 1 (`@1`, Prompt `v3-phase8`) | 0/12 Läufe erfüllen ihn |
| Strikter P8-Vertrag, R1 (`@2`, Prompt `v3-phase8-contract-r1`) | 2/12 Läufe (LS-01, beide Modelle): P8 und Taxonomie vollständig, P9-Routing `AUTO_RESOLVABLE` ohne P9-Aufruf, P10 bis `READY_FOR_RELEASE`, testweise lokal freigegeben ohne menschlichen Prüfer. Die übrigen 10 scheitern nur an der Ausgabeprüfung C25: Zustandsabgleich in 9 Plätzen; leere Extraktions-`from_attributes` in 4 Sonnet-Plätzen (LS-03/-04/-05/-06), bei Sonnet LS-05 als einziger Grund. |
| Fachliche Richtigkeit | Nicht Gegenstand dieser Urteile; KI-Prüfung ohne menschliche Validierung, siehe §5 und §11.6 |

**Partial-Grund:** Alle 24 Primärplätze (12 je Revision) bestehen technisch. Kein Fall erreichte
aber die P9-Route `REVIEW_RECOMMENDED`:
- LS-01 war in R1 `AUTO_RESOLVABLE` und braucht keine Prüfung;
- alle anderen Fälle blieben `HUMAN_REVIEW_REQUIRED`.

Gegenprüfung und Stabilitätsauswertung wurden daher live **nicht ausgeübt** (`not_exercised`).
Weitere Fallserien, um einen Trigger zu erzwingen, wurden auftragsgemäß nicht eröffnet.

Die Abschnitte 1–10 beschreiben Revision 1, wo nicht anders vermerkt. §11 beschreibt Zyklus R1.

## 1. Was jetzt live funktioniert (Implementierung, Paket A und B)

- **`agent-arena audit run --live`:** Ein Fall läuft über Runner → Parser → P8 → P9 → P10-Bundle
  → Markdown/HTML → Integritätsprüfung. `--replay` analysiert gesicherte Live-Antworten ohne
  Modellaufruf erneut. `--offline` ist unverändert.
- **5.5-Adapter** `providers/anthropic_live.py`:
  - Ein HTTP-Request je Versuch, fester Endpunkt `https://api.anthropic.com/v1/messages`,
    `trust_env=False`, keine SDK-Retries, keine Samplingparameter.
  - Adaptive Thinking mit `output_config.effort`.
  - Die Fachantwort stammt nur aus `text`-Blöcken. Trunkierung, Ablehnung und fehlender Text sind
    explizite Zustände.
  - Der 4.5-Adapter bleibt byte-identisch.
- **Herkunft:**
  - Der Bundle-Modus `recorded_offline | live_generation | offline_replay_of_live` wird aus allen
    Trägern abgeleitet.
  - Live- und Replay-Bundles binden über die Kontrolle `provenance/live-1.0` folgende Belege:
    Modell (angefordert und zurückgegeben), Request-ID, Profil-Fingerprint, Prompt- und
    Nachrichtenhashes, Slot, Versuche, Usage, Kosten und Capture-Hash.
  - Gemischte, umdeklarierte, fallfremde oder unbelegte Träger sperren.
  - Offline bleiben Notice, Config, Kontrollregister und P9-Texte byte-identisch.
- **Budget:** `LiveBudgetLedger` erweitert das bestehende `BudgetLedger`.
  - Vor jedem Provideraufruf wird die konservative Maximalexposition reserviert.
  - Bei bekannter Usage wird auf die bestätigten Kosten abgerechnet; unbekannte Abrechnung bleibt
    gebunden.
  - Grenzen und Schutz: Versuchs-, Wiederholungs- und Gesamtgrenze, exklusive Lease, an ein
    Verzeichnis gebundene Autorisierung.
  - Wiederaufnahme mit Abgleich; beantwortete und unklare Slots werden nie neu gesendet.
- **P9 (implementiert, live nicht ausgeübt):** Gegenprüfung und Stabilität laufen im Live-Modus
  unter derselben Ledger-Bindung, aber nur auf ihren dokumentierten Triggern (Addendum §5). Belegt ist
  das bisher nur offline mit Transport-Double (§4).

**Acceptance-Matrix L1–L9:** 33 Tests in `tests/test_phase10_live.py`. Der Transport läuft über ein
httpx-Double, und die Tests prüfen den echten Einstieg einschließlich CLI-Replay.

## 2. Was tatsächlich geprüft wurde

| Prüfung | Ergebnis | Beleg |
|---|---|---|
| Acceptance L1–L9 plus Kritikerkorrekturen | 33/33 | `tests/test_phase10_live.py` |
| Offline-Abnahmekorpus AA-P10 (unverändert) | 21/21 | `evidence/offline_acceptance_21_results.json` |
| Volle Offline-Suite nach letzter Produktänderung | **2372 passed** (Baseline 2339 + 33) | `evidence/full_suite_pre_live.log` |
| Saubere Reproduktion (`phase10_clean_reproduce.py`, Commit `a695f91`) | Wheel normal, Bytes = Quelle, Abnahme 21/21, Suite 2372 passed, Checkout sauber, 0 Live-Aufrufe | `evidence/clean_reproduction/` |
| Replay einer echten Live-Antwort mit dem sauberen Wheel | gültig, Live-Herkunft erhalten, keine Generierung | `evidence/clean_wheel_replay.json` |
| 12 Live-Primärläufe über die kanonische CLI | 12/12 technisch bestanden | `evidence/smoke_summary.json`, `evidence/run_log.jsonl` |
| Replay aller 12 Live-Antworten (ohne Netz, ohne Schlüssel) | 12/12 gleicher Status, Herkunft live, Capture verifiziert, `inspect` gültig, Ledger unverändert | `evidence/replay_log.jsonl`, `evidence/replay_bundles.tar.gz` |
| Lokaler Freigabeentscheid an echten Live-Bundles | 2/2 korrekt `RELEASE_BLOCKED`, keine Revision geschrieben | `evidence/release_attempts.jsonl` |
| Ruff (neue/geänderte Dateien), `git diff --check` | sauber | — |

Historische Ruff-Befunde in unveränderten Altdateien bleiben getrennt und sind nicht Teil dieser
Prüfung.

## 3. Alle 12 Primärplätze

- **Gemeinsam für alle Zeilen:**
  - Transport HTTP 200, `end_turn`, finaler `text`-Block vorhanden. Zehn Antworten enthielten
    zusätzlich einen `thinking`-Block; Sonnet LS-05 und LS-06 lieferten nur `text` (0 Thinking-Tokens).
  - Parser `parse_ok`; Bundle und `inspect` gültig; Markdown und HTML vorhanden.
  - P8 `incomplete`, Taxonomie `incomplete`, P9-Route `HUMAN_REVIEW_REQUIRED`, keine P9-Ausführung.
  - Status `ANALYSIS_INCOMPLETE`.
  - Freigabe: gesperrt (geprüft an LS-01 beider Modelle).
- **Eingabe:** jeweils rund 11.000 Tokens, laut Provider-Usage.
- **Rohes Modelllabel und Propositionsurteile:** stammen aus der Rohantwort und sind wegen
  unvollständigem P8 nicht validiert.

| Modell | Fall | Rohes Label (Konfidenz) | Rohe Propositionsurteile | Ausgabetokens | Kosten USD | Latenz s | Request-ID |
|---|---|---|---|---|---|---|---|
| Haiku 5.5 | LS-01 | solid (0.82) | p1 supported | 8.048 | 0.005127 | 29.2 | req_011CfuRm1vQt9VhvmoGJ5cof |
| Haiku 5.5 | LS-02 | overclaim (0.85) | p1 unsupported | 10.505 | 0.006348 | 39.3 | req_011CfuRqF7XNoL5W3Dw3mU1c |
| Haiku 5.5 | LS-03 | overclaim (0.86) | UND: p1 supported, p2 unsupported | 13.698 | 0.007960 | 47.8 | req_011CfuRtCkDanetwFAym46Sk |
| Haiku 5.5 | LS-04 | solid (0.60) | ODER: p1 supported, p2 unknown | 15.505 | 0.008856 | 57.9 | req_011CfuRwnxr5Ha4V1dVUXdUW |
| Haiku 5.5 | LS-05 | overclaim (0.45) | p1 unsupported | 10.022 | 0.006104 | 37.4 | req_011CfuS28ePytqkkScZ5WGGX |
| Haiku 5.5 | LS-06 | correlation_vs_causation (0.80) | p1 unknown | 11.115 | 0.006672 | 40.9 | req_011CfuS4x6UYKNasEaPtE7VV |
| Sonnet 5.5 | LS-01 | solid (0.90) | UND: p1 supported, p2 supported | 5.576 | 0.077808 | 31.2 | req_011CfuS82QWKZ1Jzy2rJcQjH |
| Sonnet 5.5 | LS-02 | mechanism_vs_evidence (0.80) | p1 unsupported | 5.275 | 0.074644 | 30.9 | req_011CfuSDeHuDs6tymPZy52WF |
| Sonnet 5.5 | LS-03 | overclaim (0.90) | UND: p1 supported, p2 unsupported | 8.168 | 0.103890 | 45.4 | req_011CfuSFz9oTZQmSx8XbDFR6 |
| Sonnet 5.5 | LS-04 | solid (0.72) | ODER: p1 supported, p2 unknown | 5.822 | 0.080284 | 34.9 | req_011CfuSKRm13b7yS5XZxRQeo |
| Sonnet 5.5 | LS-05 | overclaim (0.60) | p1 unsupported (Ledger fälschlich unter `phase8.ledger` verschachtelt) | 2.620 | 0.048042 | 15.6 | req_011CfuSN4iZeUr2FQntDaXsW |
| Sonnet 5.5 | LS-06 | correlation_vs_causation (0.93) | p1 contradicted | 3.966 | 0.061944 | 21.6 | req_011CfuSPGi9huKtkgGj1gpTZ |

Der Sonnet-LS-01-Lauf wurde nach seinem regulären Abschluss angehalten (§6). Seine CLI-Ausgabe ist
daher nicht erfasst; der Lauflog-Eintrag ist ausdrücklich als aus dem Bundle rekonstruiert markiert.

## 4. P9-Pfade

| Pfad | Live ausgeführt | Offline geprüft | Grund |
|---|---|---|---|
| Gegenprüfung (Haiku, Sonnet) | **nein — not_exercised** | ja (L7, Transport-Double) | Kein natürlicher Trigger: P8 unvollständig, Route `HUMAN_REVIEW_REQUIRED`; Modell-Gegenprüfung nur bei `REVIEW_RECOMMENDED` |
| Stabilitätsauswertung (Haiku, Sonnet) | **nein — not_exercised** | ja (L7, generierend und No-op) | Setzt eine abgeschlossene Gegenprüfung voraus |
| Menschliche Adjudikation | nein | — | Nicht erfunden; die nötigen menschlichen Entscheidungen bleiben offen |

Offline-Tests ersetzen den Live-Nachweis dieser Pfade nicht.

## 5. Fachliche Beobachtungen (KI-Prüfung, nicht validiert, eigenständig vom technischen Ergebnis)

Die Prüfung stützt sich auf die rohen Modellantworten und die gesendeten Quelltexte
(`live_run/tasks/*.json`). Es handelt sich um eine KI-Prüfung ohne menschliche Bestätigung.
Strittige Punkte bleiben strittig.

- **LS-01 positive Kontrolle** (Quelle: „Students were randomly assigned … reading proficiency was on
  average two and a half months ahead"): Beide Modelle urteilen supported/solid. Erwartungsgemäß.
- **LS-02 Zellbefund → Patienten** (Quelle: „killed up to 90% of cultured human tumour cells in a
  petri dish … No animal or human data are described"):
  - Beide Modelle urteilen unsupported. Erwartungsgemäß, nicht als gestützt gewertet.
  - Die Labels unterscheiden sich: Haiku `overclaim`, Sonnet `mechanism_vs_evidence`. Welches Label
    präziser ist, bleibt strittig.
- **LS-03 UND-Claim** (Quelle: „reduced LDL cholesterol by 65 percent … no cardiovascular events were
  tracked"):
  - Beide Modelle zerlegen korrekt in UND mit LDL supported und Herzinfarkt unsupported.
  - Haiku zitiert dabei ungenau: „…were tracked." statt „…were tracked and no outcomes trial…".
- **LS-04 ODER-Claim** (Quelle: „gained roughly two additional months of reading progress"):
  - Beide Modelle zerlegen in ODER mit einer gestützten Alternative (Lesefortschritt) und einer
    unbekannten (Absentismus). Label solid; erwartungsgemäß.
  - Sonnet formuliert p2 ohne Subjekt („reduced their school absenteeism").
- **LS-05 unzureichende Evidenz** (Quelle: „60 participants over four weeks reports no serious
  adverse events"):
  - Kein Modell wertet den Claim als widerlegt; die zentrale Grenze ist eingehalten.
  - Beide Modelle urteilen unsupported statt des präziseren unknown; strittig.
  - Sonnet extrahiert die Proposition, verschachtelt das Ledger aber unter `phase8.ledger`. Das ist
    ein Schemaverstoß in der Struktur, keine fehlende Extraktion.
- **LS-06 widersprüchliche Evidenz** (Quelle: Beobachtungsassoziation gegen RCT-Metaanalyse „did not
  cause weight loss"):
  - Sonnet urteilt contradicted, Haiku unknown; beide Label `correlation_vs_causation`.
  - Kein Modell urteilt supported. Erwartungsgemäß, mit unterschiedlicher Stärke.

**Kernbefund Extraktion:** 0/12 Läufe erfüllen den strikten AA-P8-Ausgabevertrag
(`evidence/extraction_failure_categories.json`). Betroffene Plätze je Kategorie:

| Kategorie | Betroffene Plätze |
|---|---|
| Transformations-Audit | 10 |
| Evidenz-/Bindungsspur | 9 |
| ungültige Enum-/Dimensionswerte | 7 |
| ungelöste `value_origin` | 6 |
| ungenaue Zitate | 3 |
| Ledger-Schemaverstoß | 2 |
| fehlende Pflichtpropositionen | 1 |

Der Validator verlangt im Transformations-Audit exakte Feldkopien:
- `from_text` gleich dem Propositionstext,
- `from_attributes` gleich den Attributen,
- Zieltexte in festem Format.

Der Phase-8-Prompt beschreibt diese Pflichten nur teilweise. Bisher hat es niemand bemerkt, weil
alle Offline-Aufzeichnungen von Hand erstellt wurden.

**Revidiert (§11):** Hier stand ursprünglich, eine Korrektur sei in diesem Auftrag ausgeschlossen.
Das war zu eng gefasst. Die Offline-Diagnose zeigt überwiegend eine Spezifikationslücke: 65 von 86
Fehlergründen betreffen Prüferregeln, die der Prompt nicht nennt. Die Reparaturregel des Auftrags
erlaubt eine solche technische Korrektur, solange der Prüfer unverändert bleibt.

Diese Ergebnisse erlauben weder einen Haiku-vs-Sonnet-Sieger noch eine Accuracy- oder
Wirksamkeitsaussage noch einen Vergleich ohne Harness.

## 6. Korrekturen, Revisionen, Wiederholungen

- **Paket A+B, Kritik 1:** zwei materielle Befunde.
  - M1: P9-Träger waren nicht an ihren Fall gebunden.
  - M2: Budget-Reset bei verlorenem Ledger oder kopierter Autorisierung; Capture-Überschreibung.
  - Dazu nicht-materielle Befunde: `trust_env`, robuste Fehlerkörper, Credential vor Reservierung,
    Hash des gelieferten Texts, Terminalschritt nach Absturz, CLI-Tests.
  - Korrekturrunde 1 behob alle; die Nachprüfung fand keinen materiellen Befund mehr.
- **Korrekturrunde 2 (nicht-materiell):** Überschreibprüfung vor dem Versand, fremde Captures
  werden bei der Wiederaufnahme nicht verrechnet, eine unterbrochene Einzelwiederholung kann
  fortgesetzt werden.
- **Abgelehnter Kritikerpunkt:** Der Sonnet-5.5-Cache-Read-Preis von 0,10 USD/MTok stimmt laut
  offizieller Preisseite vom 11.10.2026 („0.05x the base input price").
- **Getesteter Codecommit:** `3dd22fb`. Profile `claude-haiku-5-5@1` und `claude-sonnet-5-5@1`
  wurden vor dem ersten Ergebnis eingefroren (Commit `a695f91`) und nicht geändert.
- **Live-Reparaturzyklen:** zunächst 0 von 2. Nach der Statusanfrage wurde 1 von 2 genutzt
  (R1, §11). Die ursprüngliche Begründung („erfordert eine materielle Vertragsänderung“) ist dort
  revidiert. Ein Zyklus R2 wurde nicht ausgelöst.
- **Technische Wiederholungen:** 0 von 4. Semantische Wiederholungen: keine.
- **Pause:** Die Sonnet-Serie wurde nach LS-01 für etwa 45 Sekunden angehalten (Abrechnung
  attempt-007 um 23:36:15 UTC, Reservierung attempt-008 um 23:37:00 UTC). Anlass war das einheitliche
  `ANALYSIS_INCOMPLETE` bei Haiku. Die gesicherten Antworten wurden offline geprüft (kein
  Harnessfehler). Danach lief die Serie mit unverändertem Profil weiter.
- **Kritik des Abschlussberichts (einmalig):**
  - Alle Zahlen, Request-IDs, Capture-Hashes und beide Urteile wurden bestätigt.
  - Eine materielle Abweichung wurde behoben: Sonnet LS-05 hatte ich fälschlich als „keine
    Propositionen" beschrieben.
  - Zwei nicht-materielle Punkte wurden präzisiert: Thinking-Blöcke fehlten bei Sonnet LS-05/06;
    P9 und Wiederaufnahme sind nur offline belegt.
  - Die leere Laufzeit-Lease-Datei wurde entfernt.
- **Logs:** Zwei Lauflogs waren wegen eingebetteter mehrzeiliger CLI-Ausgabe zunächst kein gültiges
  JSONL. Sie wurden aus den unveränderten Objekten neu geschrieben, nichts wurde erneut ausgeführt.

## 7. Kosten und Budget

- **Bestätigte Generierungskosten:** **0,487679 USD**.
  - Haiku: 0,041067 USD (66.171 Eingabe- und 68.893 Ausgabetokens).
  - Sonnet: 0,446612 USD (66.171 Eingabe- und 31.427 Ausgabetokens).
- **Ungeklärte Abrechnung:** keine. Alle 12 Versuche sind aus der Usage bestätigt.
- **Ledger:** offene reservierte Exposition 0. Gebunden sind 0,487679 USD; das Restbudget betrug
  1,512321 USD von 2,00 USD, 12 von 40 Versuchen und 0 von 4 Wiederholungen waren verbraucht.
  Vor R1 wurde dieser Ledger geschlossen (`REVOKED`); der Rest ging in Autorisierung `-003` über.
  Gesamtkosten des Auftrags siehe §11.7.
- **Reservierungsgrenze:** Die größte Einzelreservierung betrug 0,218318 USD.
  - Die konservative Eingabegrenze lag bei 28.989 Tokens; tatsächlich waren es 11.024 laut
    `count_tokens`, also Faktor 2,6.
  - Die tatsächliche Eingabe lag in jedem Versuch unter der Grenze.
- **Nicht-generative Aufrufe:** 2 × `messages.count_tokens` (kostenlos, 0 Generierungen).
- **Frühere Autorisierung:** Die Smoke-Autorisierung des ersten Auftrags ist als
  `CLOSED_NOT_EXECUTABLE` ausgeschlossen. Sie hatte nie ein Ledger.
- **Claude Code selbst:** Die Sitzung hat keinen `ANTHROPIC_API_KEY` und nutzt OAuth. Der
  Projektschlüssel wurde nur in Kindprozesse geladen. Ob Claude Code über dasselbe Guthaben
  abgerechnet wird, ist von hier nicht prüfbar.
- **Schlüsselmaterial:** keines in Logs, Captures, Bundles oder Commits.

## 8. Rollen

| Rolle | Umsetzung |
|---|---|
| Koordinator und Implementierer | Diese Claude-Code-Sitzung (`claude-opus-5-5`) |
| Kritiker | Eine schreibgeschützte Claude-Code-Rolle (Explore), in zwei Instanzen derselben Rolle: Erstkritik und Nachprüfung |

- Die erste Kritiker-Instanz war nach ihrer Rückgabe nicht mehr adressierbar.
- **R1:** Die früheren Kritiker-Instanzen waren nach der Kompaktierung der Sitzung nicht mehr
  erreichbar. Deshalb gab es eine neue schreibgeschützte Kritiker-Instanz (General-Purpose-Subagent).
  - Nach eigener Angabe lief sie als `claude-opus-5-5`; ihre Effort-Einstellung ist nicht sichtbar.
  - Sie arbeitete ohne Netzwerk und Schlüssel. Den Preisabgleich machte sie nur gegen lokal
    vorliegende Unterlagen.
  - Vier Durchgänge derselben Rolle: Erstkritik, Nachprüfung 1, Nachprüfung 2 und die Kritik dieses
    Berichts.
- Effort-Einstellungen der Kritikerrollen sind nicht auslesbar.
- Keine rekursive Delegation; keine Astra-Konfiguration.
- Keine kostenpflichtige Projekt-API für Codekritik.

## 9. Git und Artefakte

Branch `live-integration/aa-p10-live-20261011`, abgezweigt vom Blockerbericht `0fd4745`.

| Commit | Inhalt |
|---|---|
| `3dd22fb` | Live-Integration (getesteter Codecommit, Revision 1) |
| `a695f91` | Fall- und Autorisierungs-Freeze vor Generierung |
| `871a66a` | Evidenz und Bericht Revision 1 |
| `f885aae` | Reparaturrevision R1 (getesteter Codecommit R1) |
| `6142dcd` | R1-Freeze vor Generierung: `-002` geschlossen, `-003`, Manifest |

Danach folgt der Evidenz-/Berichtscommit zu R1 mit dem Ledger von `-003`, nach Auftragsende
geschlossen. Er ist in der Abschlussantwort ausgewiesen.

- **Prüfbefehle:**
  - `pytest tests/test_phase10_live.py`
  - `pytest` (vollständig)
  - `scripts/phase10_acceptance.py`
  - `scripts/phase10_clean_reproduce.py --full-suite`
  - `agent-arena audit run --live|--replay`
  - `agent-arena audit inspect|release`
- **Artefakte:** `live_run/`
  - Autorisierung, Manifest, Erwartungen, Tasks,
  - `ledger.json`, `captures/` (12 Rohantworten ohne Zugangsdaten),
  - 12 Live-Bundles: byte-genau in `evidence/live_bundles.tar.gz` mit Prüfsummenindex
    `evidence/live_bundles_index.json`. Pfade in den Logs beziehen sich auf
    `live_run/bundles/<profil>/<revision>/` innerhalb des Archivs; nach dem Entpacken prüfen
    12/12 Bundles mit `audit inspect` gültig. Die kanonischen `report.md` enden mit einer
    Leerzeile; sie bleiben unverändert archiviert, statt sie für `git diff --check` anzupassen.
- **Evidenz:** `evidence/` (Lauf-, Replay- und Freigabelogs, Auswertung, Fehlerkategorien,
  Tokenzählung, Suite, Abnahme, saubere Reproduktion).

## 10. Ist ein frischer Wirksamkeitsbenchmark jetzt technisch vorbereitbar?

Stand nach R1 (ursprüngliche Fassung zu Revision 1 sinngemäß ersetzt).

**Der Ablauf ja, die Messung noch nicht sinnvoll.**
- **Live belegt:** Transport, Budgetdurchsetzung, Herkunft, Bundles, Replay und lokaler
  Freigabeentscheid. Seit R1 auch ein Durchlauf echter Antworten bis `RELEASED` (LS-01, beide
  Modelle): ohne P9-Aufruf, denn das Routing ergab `AUTO_RESOLVABLE`. Die Freigabe erfolgte
  testweise ohne menschlichen Prüfer.
- **Nur offline geprüft:** Wiederaufnahme nach Absturz und die P9-Pfade Gegenprüfung und Stabilität.
- **Hauptgrund gegen eine Messung jetzt:** Bei 2/12 strikt vollständigen P8-Analysen würde ein
  Benchmark vor allem die Ausgabeprüfung C25 messen. Gemeint ist die Übereinstimmung des
  modellbehaupteten Zustands mit der nicht offengelegten Host-Ableitung, nicht die fachliche
  Urteilsqualität.

**Genau ein nächster Schritt:** ein Folgeauftrag zu C25, also der Frage, wer den Zustand der
Ausgabe festlegt. Es ist eine Designentscheidung des Projekts und keine Reparatur:
- **Variante A:** Der Host trägt seinen abgeleiteten Zustand selbst in die Ausgabe ein und prüft das
  Modell nur noch auf Überhöhung. Das ist eine Änderung der P8-Semantik.
- **Variante B:** Die wissenschaftliche Ableitungsregel wird offengelegt. Das steuert die Modelle
  allerdings auf die Erwartungen der Fangfälle und muss mit frischen Fällen gemessen werden.

Danach folgt ein kleiner Smoke mit frischen Fällen, einschließlich eines Falls mit natürlichem
`REVIEW_RECOMMENDED`-Trigger.

## 11. Reparaturzyklus R1 (Phase-8-Vertrag)

**Anlass:** die Statusanfrage vom 11.10.2026 mit dem Auftrag zur Fortsetzung. Zu diesem Zeitpunkt
waren die beiden erlaubten Live-Reparaturzyklen ungenutzt. R1 ist Zyklus 1 von höchstens 2 und lief
innerhalb derselben Grenzen von 2,00 USD, 40 Versuchen und 4 Wiederholungen. Ein Auftrag zur
Diagnose aller zehn Phasen lag dieser Sitzung nicht vor. Diagnostiziert wurde daher nur der Live-Pfad
P7-Bindung → P8 → P9 → P10.

### 11.1 Ursache (offline, an den 12 gesicherten Antworten)

- **86 Fehlergründe** (`repair_r1/diagnosis_rev1.json`):
  - 65 betreffen Prüferregeln, die `v3-phase8` nicht nennt;
  - 5 betreffen abweichend formulierte Regeln;
  - 9 betreffen nur angedeutete Regeln;
  - 7 betreffen ausdrücklich genannte Regeln, also echte Modellfehler.
- **Beispiele für ungenannte Regeln:**
  - zulässige Werte für `value_origin`, `relation` und Dimensionsnamen;
  - exakte Kopierfelder der Transformationsprüfung;
  - Negativ-Aussage zu jedem „no evidence found“;
  - wörtliches Identifikationsargument.
- **In den Antworten beobachtet:** `value_origin` lautete zum Beispiel `reported_by_source`, `reported`
  oder fehlte. Nur `source_reported` ist gültig.

### 11.2 Korrektur, Kritik und Prüfungen

- **Prompt `study_forensics_prompt/v3-phase8-contract-r1`:** die unveränderten `v3-phase8`-Bytes plus
  die bestehenden Prüferregeln C1–C29.
  - Die Vokabulare werden aus den Prüfer-Konstanten erzeugt.
  - Kein Fallinhalt, keine erwartete Antwort, keine neue Regel; der Prüfer bleibt unverändert.
  - Die wissenschaftliche Zustandsableitung des Hosts bleibt bewusst verborgen, weil sie auf die
    Erwartungen der Fangfälle steuern würde. Offengelegt ist nur die Buchhaltung C29.
- **Profile `@2`:**
  - Haiku: `max_tokens` 32000 statt 16000, weil `@1` bis 15505 nutzte.
  - Sonnet: unverändert bis auf den Prompt.
  - Die Promptbindung geht samt SHA-256 in den Fingerprint ein. `@1` bleibt byte- und
    fingerprintgleich.
- **Live-Pfad:**
  - Fremde Promptversionen werden vor dem Versand verweigert.
  - Die Herkunftskontrolle prüft Version und Hash des Prompts je Träger.
  - Replay hängt nicht mehr vom Ablaufdatum der Autorisierung ab.
  - Die Vorgänger-Autorisierung wird über die bestehende Ledger-Sperre geschlossen
    (`close_for_successor`).
- **Kritik:** separater, schreibgeschützter Kritiker ohne Netzwerk.
  - **Erstkritik**, drei materielle Punkte:
    - der Zustandsabgleich C25: Entscheidung „nicht offenlegen“ plus Vorab-Festlegung;
    - drei falsche Vertragssätze: C17, C19 und Binding-IDs;
    - eine fehlende Stopp-Regel.
  - **Korrekturrunde 1:** alle drei Punkte behoben.
  - **Nachprüfung 1:** C14 war falsch formuliert; behoben in **Korrekturrunde 2**.
  - **Nachprüfung 2:** Urteil vor dem Live-Lauf „nicht bereit“, weil in C14 noch die Ausnahme für
    `effect_direction` bei `contradiction` fehlte. Der Kritiker gab den Wortlaut vor und stufte die
    Prüfung als mechanisch ein (Test und neue Pins). Ich habe sie als Abschluss von Runde 2
    eingefügt, ohne dritte Kritikrunde.
  - **Nachträgliche Bestätigung:** In der Berichtskritik hat der Kritiker die eingefügte Klausel,
    den Test und die Pins gegen `f885aae` und alle 12 Requests bestätigt.
- **Offline-Test der Korrektur** (`repair_r1/offline_simulation/`): Die Kritiker-Simulation lief auf
  den gesicherten Antworten und ist keine Modellausgabe.
  - Wörtliche Regelbefolgung: 0/12 strikt vollständig.
  - Mit C12/C14: 2/12.
  - Orakel mit Host-Zustand (keine zulässige Reparatur): 11/12.
- **Prüfungen:**
  - 14 neue Tests; `tests/test_phase10_live.py` 47/47.
  - Volle Offline-Suite **2386 passed**, Offline-Abnahme 21/21, Ruff sauber.
  - Revision-1-Replays unter R1-Code: 12/12 gleicher Status, Ledger-Hash unverändert
    (`repair_r1/evidence/replay_check_rev1_under_r1_code.json`).
  - Saubere Reproduktion: siehe §11.8.

### 11.3 Vorab-Festlegungen (Commit `6142dcd`, vor dem ersten R1-Ergebnis)

- Feste Reihenfolge: Haiku LS-01…06, dann Sonnet LS-01…06.
- Ein verweigerter Slot gilt als nicht ausgeführt; es gibt keine Umverteilung.
- Beide Hälften bilden einen Zyklus. Jede Änderung dazwischen wäre R2.
- Weicht der `asserted_state` vom Host-Zustand ab (C25), gilt das als Befund der Ausgabeprüfung,
  also als Modellqualität. Es ist kein Grund für R2.
- R2 nur bei einem neu gefundenen technischen Defekt.
- Revision 1 und R1 werden getrennt berichtet; es gibt keine zusammengeführte Erfolgsquote.

### 11.4 Alle 12 R1-Primärplätze

- **Gemeinsam für alle Zeilen:**
  - HTTP 200, `end_turn`, `thinking`- und `text`-Block, `parse_ok`.
  - Bundle und `inspect` gültig, Markdown und HTML vorhanden.
  - Kein P9-Aufruf.
- **Eingabe:** 14.696–14.917 Tokens laut `count_tokens`. Die Reservierungsgrenze lag bei rund 40.300.
- **Grenze:** Haiku `@2` nutzte bei LS-04 31.121 und bei LS-03 27.962 von 32.000 Ausgabetokens. Die
  neue Grenze hat also kaum Reserve. Es wurde nichts gekürzt, alle Antworten endeten mit `end_turn`.
- **Urteile:** „Modell → Host“ zeigt das rohe Modellurteil je Proposition und den vom Host
  abgeleiteten Zustand.

| Modell | Fall | Status | P8 | P9-Route | Modelllabel (Konfidenz) | Modell → Host je Proposition | Ausgabetokens | Kosten USD | Latenz s | Request-ID |
|---|---|---|---|---|---|---|---|---|---|---|
| Haiku 5.5 | LS-01 | READY_FOR_RELEASE | completed | AUTO_RESOLVABLE | solid (0.85) | UND: p1 supported→supported; p2 supported→supported | 25.300 | 0.014130 | 94.6 | req_011CfvfQasbgcGWxvhHabE3A |
| Haiku 5.5 | LS-02 | ANALYSIS_INCOMPLETE | incomplete | HUMAN_REVIEW_REQUIRED | mechanism_vs_evidence (0.6) | p1 unsupported→unknown | 14.354 | 0.008650 | 51.8 | req_011CfvfXcL6tSTk9a95Q498L |
| Haiku 5.5 | LS-03 | ANALYSIS_INCOMPLETE | incomplete | HUMAN_REVIEW_REQUIRED | overclaim (0.86) | UND: p1 supported→unknown; p2 unsupported→unsupported | 27.962 | 0.015469 | 104.2 | req_011CfvfbVQFHrNm9QUrR8cqE |
| Haiku 5.5 | LS-04 | ANALYSIS_INCOMPLETE | incomplete | HUMAN_REVIEW_REQUIRED | solid (0.7) | ODER: p1 supported→unknown; p2 unsupported→unknown | 31.121 | 0.017042 | 119.3 | req_011CfvfjF3mHb8QFvw1xWYsd |
| Haiku 5.5 | LS-05 | ANALYSIS_INCOMPLETE | incomplete | HUMAN_REVIEW_REQUIRED | overclaim (0.6) | p1 unsupported→unknown | 12.903 | 0.007922 | 49.2 | req_011Cfvft7fG4Xi8gf3ka6f6E |
| Haiku 5.5 | LS-06 | ANALYSIS_INCOMPLETE | incomplete | HUMAN_REVIEW_REQUIRED | correlation_vs_causation (0.8) | p1 contradicted→unknown | 21.720 | 0.012352 | 83.0 | req_011CfvfwoM3mXxWwFG7eqvzv |
| Sonnet 5.5 | LS-01 | READY_FOR_RELEASE | completed | AUTO_RESOLVABLE | solid (0.85) | p1 supported→supported | 8.577 | 0.115368 | 48.5 | req_011Cfvg7y6iYxs1G1JjJeon4 |
| Sonnet 5.5 | LS-02 | ANALYSIS_INCOMPLETE | incomplete | HUMAN_REVIEW_REQUIRED | overclaim (0.9) | p1 unsupported→unknown | 6.301 | 0.092454 | 35.9 | req_011CfvgBbxLGCDxpHC9e6gFz |
| Sonnet 5.5 | LS-03 | ANALYSIS_INCOMPLETE | incomplete | HUMAN_REVIEW_REQUIRED | overclaim (0.9) | UND: p1 supported→unknown; p2 unsupported→unknown | 10.569 | 0.135450 | 60.4 | req_011CfvgEJr2wTGqcHqMQC2so |
| Sonnet 5.5 | LS-04 | ANALYSIS_INCOMPLETE | incomplete | HUMAN_REVIEW_REQUIRED | solid (0.85) | ODER: p1 supported→unsupported; p2 unsupported→unknown | 10.376 | 0.133374 | 59.4 | req_011CfvgJqLTFatWry6NNZQFW |
| Sonnet 5.5 | LS-05 | ANALYSIS_INCOMPLETE | incomplete | HUMAN_REVIEW_REQUIRED | overclaim (0.55) | p1 unknown→unknown | 6.398 | 0.093372 | 38.5 | req_011CfvgPH29VMWjACJHxX7S3 |
| Sonnet 5.5 | LS-06 | ANALYSIS_INCOMPLETE | incomplete | HUMAN_REVIEW_REQUIRED | correlation_vs_causation (0.8) | p1 contradicted→unknown | 7.384 | 0.103674 | 41.0 | req_011CfvgSB5HqDm3hHFC8gDBG |

**Verbleibende Fehlerklassen** (`repair_r1/evidence/extraction_failure_categories_r1.json`). Beide
gehören zur Ausgabeprüfung C25:
- **Zustandsabgleich:** in 9 Plätzen. Das behauptete Zustandsfeld weicht vom Host-Zustand ab.
- **Leere `from_attributes` bei der Extraktion:** in 4 Sonnet-Plätzen (LS-03/-04/-05/-06). Bei
  Sonnet LS-05 ist das der einzige Grund; dort stimmen Modell- und Host-Zustand überein (unknown).
- Alle Vertrags- und Strukturfehler der Revision 1 sind verschwunden.

**Prüfpunkte:**
- **Nach Haiku** (`checkpoint_after_haiku.json`): kein technischer Defekt. Die Sonnet-Hälfte lief
  daher unverändert.
- **Nach Sonnet:** Die leeren `from_attributes` werte ich als Modellfehler gegen die genannte Regel
  C25. Diese gilt für jede Transformation.
  - Sonnet setzte sie nur in 3 von 8 Extraktionen korrekt (5 leer), Haiku in 9 von 9.
  - Sonnet war selbst innerhalb derselben Antwort uneinheitlich: In LS-04 ist `t1` korrekt, `t4`
    leer.
  - Eine Mitursache in der Vertragsformulierung ist nicht auszuschließen. C23 nennt für die
    Extraktion `to_attributes`, wiederholt aber `from_attributes` nicht.
  - Nach der Vorab-Festlegung ist das kein fehlerhafter Vertragssatz und kein technischer Defekt,
    daher kein R2. Eine künftige Revision sollte C23 ausdrücklich ergänzen.

### 11.5 Freigabe, Replay und P9

- **Lokaler Freigabeentscheid** (`release_attempts_r1.jsonl`):
  - Haiku LS-01 und Sonnet LS-01 sind testweise `RELEASED`, und `inspect` ist gültig.
  - Prüferkennung: „TEST ONLY - Claude Code smoke harness (no human reviewer; not an approval by
    Lazaros Varvatis)“. Es wurde keine menschliche Adjudikation erfunden.
  - Gegenprobe: Haiku LS-02 wurde korrekt `RELEASE_BLOCKED`.
- **Replay aller 12 R1-Antworten** (`replay_log_r1.jsonl`; Hash-Nachweis in einem zweiten
  Replay-Lauf, `replay_check_r1.json`):
  - 12/12 mit gleichem Status und gültigen Bundles;
  - 0 Netzzugriffe, kein Schlüssel in der Umgebung;
  - der Ledger blieb byte-gleich (SHA-256 vorher gleich nachher).
- **Bundles:** byte-genau archiviert mit Index:
  - `live_bundles_r1.tar.gz` (12/12 gültig nach dem Entpacken);
  - `replay_bundles_r1.tar.gz` (12/12 gültig);
  - `released_bundles_r1.tar.gz` (2/2 `RELEASED`).
- **P9 live: weiterhin `not_exercised`.**
  - LS-01 ist `AUTO_RESOLVABLE`, braucht also keine Prüfung.
  - Alle anderen Fälle sind `HUMAN_REVIEW_REQUIRED`.
  - Ein natürlicher `REVIEW_RECOMMENDED`-Trigger trat auch in R1 nicht auf.

### 11.6 Fachliche Beobachtungen R1 (KI-Prüfung, nicht validiert)

- **Formattreue:** Beide Modelle halten den nun ausgesprochenen Vertrag weitgehend ein; Haiku sogar
  fehlerfrei bis auf C25.
- **Modellurteile:** Sie liegen fast immer im Rahmen der vorab eingefrorenen Erwartungen.
  - LS-01: supported.
  - LS-02: unsupported; Zellbefund nicht als klinisch gewertet.
  - LS-03: UND mit gestütztem LDL- und ungestütztem Herzinfarkt-Teil.
  - LS-05: Kein Modell wertet die unzureichende Evidenz als Widerlegung (Haiku unsupported, Sonnet
    unknown).
  - LS-06: beide contradicted.
- **Host-Ableitung:** Sie ist in 9 der 10 unvollständigen Fälle strenger als das Modellurteil und
  ergibt meist `unknown`. Mechanismen in den 12 abweichenden Propositionen (Mehrfachnennung möglich):
  - 8× die Urteilsregel C29: Ein gemeldetes unsupported/contradicted, das von der Evidenzableitung
    abweicht, wird unknown;
  - 6× Beobachtung `inconclusive`;
  - 5× `no_evidence_found`;
  - 3× offene Attribute, etwa `certainty` oder `endpoint_type`;
  - 2× unbekannte Evidenzfähigkeit (LS-03 p1, beide Modelle);
  - 2× Review ohne zugrunde liegende Studien (LS-06, beide Modelle);
  - je 1× ungelöste Produktübertragung (Haiku LS-04 p1) und fehlendes `comparison` (Sonnet LS-04 p1:
    „within-arm change cannot establish a between-arm causal effect“).
- **LS-04 und seine Erwartung:** Die Erwartung „supported“ (ODER mit gestützter Alternative) trifft
  die Host-Ableitung nicht.
  - p1, Haiku: unknown, weil `certainty` offen blieb, eine Abweichung im Interventionstext nicht
    durch die erklärte Übertragung aufgelöst wurde und eine zweite Bindung inconclusive war.
  - p1, Sonnet: unsupported, weil die Evidenzbeschreibung `comparison` leer ließ.
  - p2, beide Modelle: unknown, wegen `no_evidence_found` zusammen mit der Urteilsregel.
  - Der Host bewertet hier also Darstellungsdetails, keine Completer-Frage.
  - Die Erwartung bleibt eingefroren; ob „supported“ fachlich zutrifft, bleibt strittig.
- **Grenzen:** kein Haiku-vs-Sonnet-Sieger; keine Erfolgsquote über die Revisionen hinweg; die sechs
  Fälle bleiben Entwicklungsfälle.

### 11.7 Kosten und Budget (gesamter Auftrag)

| Abschnitt | Versuche | Bestätigte Kosten USD |
|---|---|---|
| Revision 1 (Autorisierung `-002`, jetzt `REVOKED`) | 12 | 0,487679 |
| R1 Haiku `@2` (Autorisierung `-003`) | 6 | 0,075565 |
| R1 Sonnet `@2` (Autorisierung `-003`) | 6 | 0,673692 |
| **Gesamt** | **24 von 40** | **1,236936 von 2,00** |

- **Technische Wiederholungen:** 0 von 4. Ungeklärte Abrechnung: keine.
- **Nicht ausgegebener Rest:** 0,763064 USD in `-003`.
  - Nach Abschluss des Live-Teils habe ich `-003` am 11.10.2026 um 15:43 UTC über die
    Ledger-Sperre geschlossen (`REVOKED`, ausführbarer Rest 0, `repair_r1/evidence/closure_r1.json`).
  - Damit ist keine Autorisierung dieses Auftrags mehr ausführbar. Replay bleibt möglich.
- **R1-Tokens:**
  - Haiku: 88.821 Eingabe- und 133.360 Ausgabetokens.
  - Sonnet: 88.821 Eingabe- und 49.605 Ausgabetokens.
- **Größte Einzelreservierung in R1:** etwa 0,24 USD (Sonnet), unter der Obergrenze von 0,30 USD.
- **Nicht-generativ:** 12 weitere kostenlose `count_tokens`-Aufrufe.
- **Schlüsselmaterial:** keines in Logs, Captures, Bundles oder Commits.

### 11.8 Status nach R1

- **LIVE_INTEGRATION_PASS:** R1-Code getestet (Commit `f885aae`). Den letzten Befund vor dem
  Live-Lauf habe ich nach Kritikervorgabe eingearbeitet, ohne dritte Runde. Er wurde in der
  Berichtskritik nachträglich bestätigt.
- **LIVE_SMOKE_PARTIAL:** Alle Primärplätze laufen technisch. Ein echter Durchlauf bis `RELEASED` ist
  belegt, ohne P9-Aufruf (Routing `AUTO_RESOLVABLE`). P9-Gegenprüfung und -Stabilität sind live noch
  nicht ausgeübt.
- **Reparaturzyklen:** 1 von 2 genutzt; R2 nicht ausgelöst.
- **Saubere Reproduktion R1** (`scripts/phase10_clean_reproduce.py --full-suite`, Commit `6142dcd` mit
  demselben Code wie `f885aae`, Evidenz in `repair_r1/evidence/clean_reproduction/`):
  - Wheel normal installiert; die installierten Bytes entsprechen der Quelle.
  - Offline-Abnahme 21/21, volle Suite **2386 passed**. Die eine Warnung ist eine bekannte
    pytest-Deprecation in einem Alttest und trat schon bei Revision 1 auf.
  - Checkout am Ende sauber, 0 Live-Aufrufe.
  - Mit diesem Wheel ließ sich eine echte R1-Antwort ohne Schlüssel erneut abspielen: Sonnet LS-01
    bleibt `READY_FOR_RELEASE`, die Live-Herkunft bleibt erhalten
    (`repair_r1/evidence/clean_wheel_replay_r1.json`).
