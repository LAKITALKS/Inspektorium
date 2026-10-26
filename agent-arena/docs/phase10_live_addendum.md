# AA-P10-LIVE/1.0 — Addendum zur Live-Ausführung im kanonischen Audit-Pfad

Stand: 11.10.2026. Ergänzt AA-P10/1.0; historische Verträge und Befunde bleiben unverändert gültig.
Autorisiert durch den Folgeauftrag „Live-Anbindung und Live-Funktionstest vollständig abschließen“.
Kein Phase-11-Umfang, kein öffentlicher Release, kein Wirksamkeitsbenchmark.

## 1. Ausführungsmodi und Herkunft

Ein Bundle trägt genau einen Modus. Er wird aus allen Ergebnisträgern abgeleitet, nicht vom Aufrufer
behauptet:

| Modus | Herkunft der Modellantwort | Aktuelle Ausführung | Config | Register `provenance` |
|---|---|---|---|---|
| `recorded_offline` | Fixture/synthetisch | Replay einer Aufzeichnung | `offline-recording-v1` (unverändert) | `1.0` (unverändert) |
| `live_generation` | Echte Anthropic-Generierung | Live-Aufruf in diesem Lauf | `live-anthropic-v1` | `live-1.0` |
| `offline_replay_of_live` | Frühere echte Generierung | Replay ohne neue Modellantwort | `live-replay-v1` | `live-1.0` |

- Ein gemischter, widersprüchlicher oder unbelegter Träger macht den Modus ungültig. Er führt zu
  `PREFLIGHT_BLOCKED` beim Schreiben und zur Fehlschlag-Kontrolle `provenance` bei der Prüfung.
- Menschliche Korrekturpositionen sind in jedem Modus zulässig und bleiben als solche markiert.
- Offline-Bundles behalten Notice, Config, Register und Kontrolltexte byte-identisch.
- Live- und Replay-Bundles tragen eine eigene, im Bericht sichtbare Notice. Live-Antworten können nie
  als „SYNTHETIC; no live model execution“ erscheinen.

## 2. Live-Herkunftsbeleg

Jeder Live- oder Replay-Träger (`AgentResult.execution_evidence`, Schema `aa-p10-live-evidence/1.0`)
bindet folgende Felder:

- angeforderte und zurückgegebene Modell-ID, Request-ID und Message-ID;
- Profil-ID und Profil-Fingerprint, Systemprompt-Version und -SHA-256;
- Nutzernachricht-Version und -SHA-256, SHA-256 der gesendeten Task;
- Slot, Versuchs-ID und Autorisierungs-ID;
- Stop-Grund, Content-Block-Typen, Usage, reservierte und bestätigte Kosten;
- Latenz und SHA-256 der finalen Antwort sowie der gesicherten Rohantwort.

Pflichtprüfung `provenance/live-1.0`:

- Zurückgegebenes Modell gleich angefordertem Modell gleich registriertem Profilmodell.
- Profil-Fingerprint registriert; Request-ID und ganzzahlige Usage vorhanden, sofern ein Request
  gesendet wurde.
- Antwort-Hash gleich dem Hash der gespeicherten Rohausgabe; primäre Träger an den Fall gebunden.
- P9-Träger an ihre Positionsart gebunden; eine einzige Autorisierungs-ID im Bundle; eindeutige
  Versuchs-IDs.
- Fehlende Belege werden markiert und sperren.

Ein Hash authentifiziert weder Person noch Provider.

## 3. Profile und Nutzernachricht

Profil-Registry in `providers/anthropic_live.py`, eingefroren vor dem ersten Live-Ergebnis:

| Profil | Modell | Thinking | Effort | `max_tokens` | Sampling | SDK-Retries | Endpunkt |
|---|---|---|---|---|---|---|---|
| `claude-haiku-5-5@1` | `claude-haiku-5-5` | adaptive (Default) | `medium` (Default) | 16000 | weggelassen | 0 | `https://api.anthropic.com` fest |
| `claude-sonnet-5-5@1` | `claude-sonnet-5-5` | adaptive (nicht abschaltbar) | `medium` | 16000 | weggelassen | 0 | `https://api.anthropic.com` fest |

- **Sonnet `medium` statt Default `high`:** begrenzte Kosten und Latenz für eine strukturierte
  Extraktion; vor Ergebnissen festgelegt, keine nachträgliche Optimierung.
- **Bestehende 4.5-Profile:** `providers/anthropic.py` bleibt byte-identisch, weil historische
  Laufzeitverträge daran gebunden sind.
- **Nutzernachricht `aa-p10-live-user-message/1.0`:** `task.prompt` in
  `<task_prompt source_id="input">`, `task.context` in `<task_context source_id="context">`.
  - Systemprompt-Bytes bleiben unverändert.
  - Gold-, Rubrik- und Referenzfelder werden nie gesendet.
  - Eingaben mit den Begrenzungstags werden vor dem Versand blockiert.
- **Antwortauswertung:**
  - Nur `text`-Blöcke bilden die Fachantwort; `thinking`/`redacted_thinking` sind kein Ersatz.
  - `max_tokens` bedeutet trunkiert: die Rohausgabe bleibt erhalten, die Analyse unvollständig.
  - `refusal`, fehlender Text oder ein unbekannter Stop-Grund ergeben einen expliziten Fehler.

## 4. Autorisierung, Budget und Wiederaufnahme

- **Auftragsgebundene Autorisierung** `aa-p10-live-authorization/1.0` im Autorisierungsverzeichnis.
  Die Grenzen gelten über alle Modelle, Pakete, Korrekturen und Neustarts zusammen:
  - harte Grenze 2.000.000 Mikro-USD gesamt;
  - höchstens 40 Generierungsversuche;
  - höchstens 4 technische Wiederholungen, höchstens 1 je fehlgeschlagener Anfrage;
  - Obergrenze je Aufruf;
  - erlaubte Profile, Fall-IDs und Slots.
- **Frühere Smoke-Autorisierung** (Commit `0fd4745`): ausdrücklich `CLOSED_NOT_EXECUTABLE`, ohne
  Restbudget.
- **Ledger** `LiveBudgetLedger`, eine rückwärtskompatible Erweiterung des bestehenden `BudgetLedger`:
  - an den Autorisierungs-Fingerprint gebunden;
  - Reservierung der konservativen Maximalexposition vor JEDEM Provideraufruf, einschließlich P9,
    Stabilität und Wiederholung.
- **Maximalexposition:**
  - Eingabe ≤ UTF-8-Bytes plus Rahmenpauschale. Das ist eine gekennzeichnete konservative Annahme,
    nachträglich gegen die Usage geprüft.
  - Ausgabe ≤ `max_tokens`, einschließlich Thinking.
  - Höhere Preisstufe ab 100k Prompt-Tokens; keine Cache-Rabatte vorausgesetzt.
- **Abrechnung:**
  - Bekannte Usage verringert die Reservierung auf bestätigte Kosten.
  - Unbekannte Abrechnung (Timeout, Abbruch) bleibt voll gebunden.
- **Kein Versand**, wenn die zusätzliche Maximalexposition das Restbudget überschreiten könnte.
- **Exklusive Prozess-Lease** pro Autorisierung: keine Parallelität, die das Limit vervielfacht.
- **Wiederaufnahme:**
  - Ledger, gesicherte Rohantworten und Konfigurationsrevision werden abgeglichen.
  - Beantwortete Slots werden nie erneut gesendet.
  - Ein reservierter Slot ohne gesicherte Antwort gilt als unklar versandt: Reservierung bleibt
    gebunden, keine Wiederholung.

## 5. P9 im Live-Pfad

- **Gegenprüfung:** genau dann, wenn die P9-Route nach dem Primärlauf `REVIEW_RECOMMENDED` ist
  (AA-P9 Regel 3).
- **`HUMAN_REVIEW_REQUIRED`:** führt zu menschlicher Prüfung, ohne Modell-Gegenprüfung.
  - *Nachtrag v1-Abschluss (13.10.2026):* Im Betrieb ohne menschlichen Prüfer bedeutet die Kennung „automatisch
    nicht abschließend klärbar“. Die Bearbeitung ist beendet; der Bericht nennt die offene Ursache. Eine
    Warteschlange oder ein Prüfer wird nicht vorausgesetzt (V1_SCOPE.md).
- **Stabilität:** höchstens eine Auswertung je Fall und Modell. Bedingung: Gegenprüfung abgeschlossen,
  Fall weiter `mandatory` und technisch vollständig (Regel 7, nur Umkehr der Evidenzreihenfolge).
- **Bestehende Mechanik bleibt:** P9-Fall-Ledger, Leases, Variantensperren, Historienprüfung und
  Adjudikationsträger.
- **USD-Reservierung** erfolgt zusätzlich im globalen Live-Ledger.
- **Nicht ausgelöste Pfade** bleiben `not_exercised`.
- **Replay, `validate` und `inspect`** erzeugen keine Generierung.

## 6. Acceptance-Matrix (vor der ersten Generierung festgelegt)

| ID | Prüfpunkt | Erwartung |
|---|---|---|
| L1 | Offline-Ablauf und Replay | Kein Netzwerk-/Generierungsaufruf; Offline-Bundle-Notice/Config/Register unverändert |
| L2 | Autorisierter Live-Pfad (Transport-Double) | Parser, P8, P9 und P10 erreicht; READY bzw. begründeter Zustand |
| L3 | Fehlende/ungültige Autorisierung, fremder Provider/Profil, unzureichendes Budget | Stopp vor Versand, 0 Transportaufrufe |
| L4 | Text nach Thinking, mehrere Blöcke, Ablehnung, Trunkierung, kein Text | Korrekte Extraktion bzw. expliziter Fehlerzustand |
| L5 | Herkunftsmanipulation, gemischte Träger, Umdeklarierung live→offline, veraltete Artefakte | Erkannt und gesperrt |
| L6 | Pflichtkontrollen | Live-Register vollständig; Fehlen/Nichtausführung blockiert |
| L7 | P9 Historie und Grenzen | Gegenprüfung nur bei Trigger; Aufruf-/Variantengrenzen gelten nach Neustart |
| L8 | Fehler, Retry, Parallelität, Crash | Retry einzeln reserviert; Timeout gebunden; parallele Lease verweigert; Crash-Slot gesperrt |
| L9 | Berichte | Gültig positiv und begründet negativ READY; offene materielle Reviewpflicht sperrt |

Offline-Doubles ersetzen keinen Live-Nachweis eines P9-Pfads.

## 7. Abschlusskriterien

- **LIVE_INTEGRATION_PASS:** L1–L9 grün; bestehende Offline-Abnahme 21/21; Kritik ohne offenen
  materiellen Befund; Gesamtsuite grün.
- **LIVE_SMOKE_PASS:** Alle 12 Primärdurchläufe technisch ausgeführt und bis zu einem gültigen,
  geprüften Bundle mit Markdown/HTML verarbeitet. Dazu kommen Ledger-Abgleich und Budgeteinhaltung.
  Getriggerte P9-Pfade wurden live ausgeführt, nicht getriggerte bleiben als `not_exercised` sichtbar.
- **LIVE_SMOKE_PARTIAL:** einzelne Primärplätze fehlen oder scheitern technisch, oder ein vorgesehener
  P9-Pfad wurde live nicht ausgeübt.
- **LIVE_SMOKE_BLOCKED:** externer Zugang, Budgetdurchsetzung oder materieller Pflichtfehler.

Fachliche Richtigkeit wird getrennt berichtet; technisches PASS ist kein fachliches PASS.

## 8. Reparaturrevision R1 (nach den ersten Live-Ergebnissen)

Festgelegt nach den 12 Primärläufen der Profile `@1` und vor jedem R1-Ergebnis. Grundlage ist die
Reparaturregel des Auftrags: höchstens zwei Live-Reparaturzyklen innerhalb derselben 2-USD-/40-Versuche-Grenze.
R1 ist Zyklus 1.

- **Ursache (offline an den 12 gesicherten Antworten):** Keine P8-Analyse war vollständig. Von 86 einzelnen
  Fehlergründen betrafen 65 Prüferregeln, die `study_forensics_prompt/v3-phase8` nicht nennt. 5 betrafen abweichend
  formulierte, 9 nur angedeutete und 7 ausdrücklich genannte Regeln (Modellfehler).
  Beleg: `analysis/live_smoke_20261011/repair_r1/diagnosis_rev1.json`.
- **Korrektur:** neue Promptversion `study_forensics_prompt/v3-phase8-contract-r1`. Sie besteht aus den
  unveränderten `v3-phase8`-Bytes plus den ausdrücklich formulierten bestehenden Prüferregeln C1–C29.
  - Vokabulare werden aus den Prüfer-Konstanten erzeugt; die Prompt-Bytes sind per Test eingefroren.
  - Keine neue Prüfregel, kein Fallinhalt, keine erwartete Antwort; der P8-Prüfer bleibt unverändert.
  - Review-Version `…-contract-r1-review-p9-1` mit identischem P9-Zusatz.
- **Bewusst nicht offengelegt:** die wissenschaftliche Zustandsableitung des Hosts, etwa Evidenztyp-Obergrenzen,
  Beobachtung → Zustand oder Designschwächen. Sie würde auf die Erwartungen der Fangfälle steuern.
  - Offengelegt ist nur Buchhaltung (C29): Vorrang des gemeldeten Urteils und UND/ODER-Verknüpfung,
    dazu die Liste der als unbekannt geltenden Werte (C14).
  - Vorab festgelegt: Ein `asserted_state`, der vom Host-Zustand abweicht (C25), ist ein Befund der
    Ausgabeprüfung, also Modellqualität. Er rechtfertigt keinen Zyklus R2.
- **Profilrevisionen** (`@1` bleibt unverändert, auch im Fingerprint):

| Profil | Abweichung von `@1` | Promptbindung |
|---|---|---|
| `claude-haiku-5-5@2` | `max_tokens` 32000 statt 16000 (`@1` nutzte bis 15505) | `v3-phase8-contract-r1` / `…-review-p9-1` |
| `claude-sonnet-5-5@2` | keine Request-Abweichung | `v3-phase8-contract-r1` / `…-review-p9-1` |

- **Bindung:**
  - Eine Profilrevision bindet Primär- und Reviewprompt mit Version und SHA-256 im Fingerprint.
  - Der Provider verweigert vor dem Versand jede andere Version.
  - Die Pflichtkontrolle `provenance/live-1.0` prüft Version und SHA-256 je Träger.
- **Budgetübergang:**
  - Autorisierung `-002` wird über die bestehende Ledger-Sperre geschlossen (`close_for_successor`:
    `REVOKED`, ausführbarer Rest 0). Ihre `authorization.json` bleibt unverändert, Replay bleibt möglich.
  - `-003` hält nur den Auftragsrest: 1.512.321 Mikro-USD, 28 Versuche, 4 technische Wiederholungen.
  - Es gibt nie zwei ausführbare Budgets.
- **Reihenfolge und Stopp-Regel:**
  - Erst Haiku LS-01…LS-06, dann Sonnet LS-01…LS-06.
  - Ein durch Autorisierung, Budget, Obergrenze oder Versuchszahl verweigerter Slot gilt als nicht
    ausgeführt; es gibt keine Umverteilung.
  - Haiku- und Sonnet-Hälfte bilden einen Zyklus. Jede Änderung dazwischen ist Zyklus R2.
- **R2** nur bei einem neu gefundenen technischen Defekt (Transport, Adapter, Parser, Budgetbindung oder
  fehlerhafte Vertragsaussage), nicht wegen Modellqualität.
- **Replay:** Das Ablaufdatum begrenzt nur Ausgaben. Replay prüft es nicht mehr, damit gesicherte
  Live-Antworten dauerhaft nachprüfbar bleiben. Replay erzeugt weiterhin nie eine Generierung und schreibt
  den Ledger nicht.
- **Bundle-Codebindung:** P10-Bundles binden die Bytes aller installierten Module.
  - Ältere Bundles prüfen nur mit ihrem Originalcode gültig: die 12 Bundles der Revision 1 mit `871a66a`.
  - Unter neuem Code werden sie per Replay neu abgeleitet (12/12 gleicher Status, 0 Netzaufrufe).
- **Offline-Test der Korrektur:** `repair_r1/offline_simulation/` enthält die Kritiker-Simulation an den
  gesicherten Antworten. Sie ist keine Modellausgabe.
- **Zusatztests R1:**
  - eingefrorene Prompt-Bytes und Fingerprints, Vokabularabdeckung ohne Fallinhalt;
  - gebundener Prompt für Primär- und Reviewaufruf, keine Profil-/Prompt-Mischung, Herkunftsfälschung erkannt;
  - Replay nach Ablauf ohne Ledger-Schreibzugriff, Schließen ohne Parallelbudget und nicht bei offener
    Reservierung oder nach Ablauf;
  - CLI;
  - Vertragssätze C17/C19/Binding-IDs gegen die unveränderten Prüfer, Unbekannt-Werte und klinische
    Endpunkte gegen die Semantik;
  - Obergrenze je Aufruf für die sechs eingefrorenen Fälle.
