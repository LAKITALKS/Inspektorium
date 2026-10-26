# Live-Funktionstest Haiku 5.5 / Sonnet 5.5 — Abschlussbericht

Stand: 11.10.2026. **Ergebnis: LIVE_SMOKE_BLOCKED** — gestoppt vor dem ersten Generierungsaufruf.
Kosten: **0,00 USD**. Generierungsversuche: **0 von 40**. Budget-Reservierungen: **0**.

Maschinenlesbare Belege: [`live_smoke_blocker_evidence.json`](live_smoke_blocker_evidence.json),
[`model_availability.json`](model_availability.json).

## Technisches Kriterium und Befund

Vorab festgelegtes technisches Kriterium: Jeder Fall läuft einmal pro Modell über den kanonischen
produktiven Pfad Runner → Parser → P8 → P9 → P10 mit einem tatsächlich unterstützten Live-Einstieg,
ohne neue CLI-Flags, ohne Testabkürzung und ohne abgeschwächte Gates.

Dieser Pfad existiert für Live-Provider nicht. Er ist nicht bloß unvalidiert, sondern im Code aktiv
gesperrt:

| Stelle | Tatsache |
|---|---|
| `src/agent_arena/phase10_cli.py:48` | `audit run` verlangt `--offline` und `--recording`; es gibt keine Live-Option. |
| `src/agent_arena/phase10_bundle.py:178` | `run_audit` gibt `PREFLIGHT_BLOCKED` zurück, wenn der Provider nicht exakt `OfflineReviewProvider` ist. |
| `src/agent_arena/phase10_bundle.py:107` | `_write_revision` sperrt jedes Ergebnis, dessen Modell/Provider nicht `offline-recording-no-live-model` ist („no live execution is authorized"). |
| `src/agent_arena/phase10_pipeline.py:222` | Die Pflichtkontrolle `provenance` scheitert, sobald ein Ergebnis oder eine P9-Position nicht offline aufgezeichnet ist. |
| `src/agent_arena/phase10_pipeline.py:131/153` | Provenienz fest: `config: offline-recording-v1`, „RECORDED OFFLINE / SYNTHETIC; no live model execution". |
| `src/agent_arena/phase9_runtime.py:408` | `execute_review` lehnt jeden Gegenprüfer ab, der nicht `OfflineReviewProvider` ist. |
| `src/agent_arena/phase9_runtime.py:350` | P9-Ledger-Policy: `attempt_microusd: 0`, `total_microusd: 0`. |

Live-fähige Pfade existieren außerhalb des kanonischen Ablaufs, erfüllen das Kriterium aber nicht:

- Legacy-`agent-arena run` und `python -m agent_arena.run_library` (`run_library.py:504–511`, jedes
  Modell) durchlaufen live Runner → Parser → P8 → P9-Erstbewertung, weil `run_agent` beides immer
  berechnet (`runner.py:270–273`). Sie führen aber keine P9-Gegenprüfung (`execute_review`) aus,
  erzeugen kein AA-P10-Bundle und reservieren nichts im `BudgetLedger`.
- `bounded_harness_mission`, `bounded_harness_continuation` und `phase7a_real_run` sind registrierte
  Einzelexperimente auf `claude-haiku-4-5-20251001` bzw. 4.5-Modellen ohne P10.
- `judge.py:102` ist ein optionaler Diagnose-Judge.

Ein Teillauf über diese Pfade hätte die verlangte P9-Gegenprüfung, P10 und die Ledger-Reservierung
vor jedem Aufruf nicht erfüllt. Er wäre zudem ohne Adapterkorrektur an den 5.5-Modellen gescheitert
(siehe unten).

Ein Live-Lauf hätte verlangt, Pflicht-Freigabegates zu ändern und eine neue Live-Betriebsfähigkeit mit
echter USD-Reservierung zu bauen. Beides schließen dieser Auftrag („keine neue Architektur", „Gates
nicht abschwächen") und der eingefrorene Vertrag AA-P10/1.0 („live operations … need separate work
orders") aus. Live erzeugte Antworten nachträglich über `--offline` einzuspielen, hätte im Bundle die
Aussage „SYNTHETIC; no live model execution" und die Modell-ID `offline-recording-no-live-model`
erzeugt. Das wäre eine Provenienzfälschung und wurde nicht gemacht.

## Alle 12 geplanten Fall-Modell-Kombinationen

Fälle wurden nicht ausgewählt und kein Manifest eingefroren, weil auf dem kanonischen Pfad kein
Live-Lauf möglich ist. Damit wurde auch kein Entwicklungsfall verbraucht.

| Fall | Typ | Modell | Technisch | Fachlich | Review/Freigabe | Aufrufe | Tokens | Kosten |
|---|---|---|---|---|---|---|---|---|
| 1 | Positive Kontrolle | Haiku 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 1 | Positive Kontrolle | Sonnet 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 2 | Tier/Zelle → klinischer Nutzen | Haiku 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 2 | Tier/Zelle → klinischer Nutzen | Sonnet 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 3 | UND-Claim, ungestützte Komponente | Haiku 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 3 | UND-Claim, ungestützte Komponente | Sonnet 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 4 | ODER-Aussage, gestützte Alternative | Haiku 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 4 | ODER-Aussage, gestützte Alternative | Sonnet 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 5 | Unzureichende Evidenz/Suche | Haiku 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 5 | Unzureichende Evidenz/Suche | Sonnet 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 6 | Widersprüchliche Evidenz | Haiku 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |
| 6 | Widersprüchliche Evidenz | Sonnet 5.5 | NICHT AUSGEFÜHRT | — | — | 0 | 0 | 0,00 USD |

Ablaufstabilität und inhaltliche Richtigkeit sind damit beide **nicht bewertbar**. Aus diesem Lauf
folgt keine Aussage über Accuracy, Modellvergleich oder Harness-Wirkung.

## Modelle und Konto

Beide angeforderten Modelle sind im Account verfügbar. Geprüft wurde über `models.retrieve`
(nicht-generativ, SDK-Retries 0, Endpunkt `https://api.anthropic.com`):

| Angefordert | Zurückgegeben | HTTP | Request-ID | Thinking `disabled` erlaubt |
|---|---|---|---|---|
| `claude-haiku-5-5` | `claude-haiku-5-5` | 200 | `req_011CfuLCBsw54Es2TVHg1Brz` | ja |
| `claude-sonnet-5-5` | `claude-sonnet-5-5` | 200 | `req_011CfuLCDKVwadpuUDtsYdQ2` | nein |

Beide Modelle lehnen `thinking.type=enabled` ab und unterstützen nur Adaptive Thinking.

Der Schlüssel wurde ausschließlich über `~/.zshrc` in einen Kindprozess geladen und nie ausgegeben.
Diese Claude-Code-Sitzung enthält keinen `ANTHROPIC_API_KEY` und nutzt OAuth. Ob Claude Code selbst
über dasselbe API-Guthaben abgerechnet wird, ist von hier nicht unabhängig prüfbar.

## Adapterkompatibilität (Befunde für den Folgeauftrag)

Laut offizieller Dokumentation (geprüft am 11.10.2026) und Models-API wäre der bestehende
`AnthropicProvider` für beide Modelle ohne Korrektur nicht lauffähig:

1. `providers/anthropic.py:66` sendet immer `temperature` (Standard 0.0). Laut Dokumentation
   beantwortet Sonnet 5.5 nicht-standardmäßige `temperature`/`top_p`/`top_k` mit HTTP 400; für
   Haiku 5.5 sollen sie weggelassen werden. Nicht durch einen eigenen Aufruf getestet.
2. `providers/anthropic.py:74` liest `message.content[0].text`. Adaptive Thinking ist standardmäßig
   an; ein Thinking-Block kann vor dem Textblock stehen.
3. Keine Effort- oder Thinking-Konfiguration. Standard-Effort laut Dokumentation: Haiku 5.5
   `medium`, Sonnet 5.5 `high`. Sonnet 5.5 kann Thinking nicht abschalten (Models-API).
4. `MAX_TRANSPORT_RETRIES = 2`: SDK-Retries werden gezählt, aber nicht einzeln budgetiert.
5. `providers/response.py:20` `DEFAULT_MAX_TOKENS = 4096` muss Thinking und das große Phase-8-JSON
   fassen; Trunkierungsrisiko. Die `bounded_harness_*`-Module setzen `max_tokens=4096` explizit.
6. `runtime_contract.MODELS` kennt nur 4.5-Modelle; es gibt kein 5.5-Laufzeitprofil.

## Kostenkalkulation (Schätzung)

Basis: kanonischer Phase-8-Systemprompt (26.100 Zeichen). Tokenzahlen geschätzt (Zeichen/3), nicht
per `messages.count_tokens` gemessen. Obergrenzen je Versuch: 16.000 Eingabe- und 16.000
Ausgabetokens einschließlich Thinking; Preise laut Dokumentation (Haiku 5.5 bis 100k Prompt:
0,10/0,50 USD je MTok; Sonnet 5.5: 2/10 USD je MTok); Thinking als Ausgabe abgerechnet (Annahme).

| Szenario | Worst Case |
|---|---|
| 1 Versuch Haiku 5.5 / Sonnet 5.5 | 0,0096 / 0,192 USD |
| 12 Primärläufe (6+6) | 1,21 USD |
| 40 Versuche (je 20) | **4,03 USD** — passt nicht in 2,00 USD |

Damit wäre auch bei vorhandenem Live-Pfad der volle 40-Versuche-Plan mit diesen Obergrenzen nicht
sicher im Budget. Für 40 Versuche dürfte ein Sonnet-Versuch höchstens etwa 0,09 USD reservieren, also
rund 5.800 Ausgabetokens einschließlich Thinking bei 16.000 Eingabe. Das kollidiert mit dem
Sonnet-Standard-Effort `high` und dem großen Phase-8-Ausgabeformat. Der Primärplan (12 Läufe) allein
passt.

## Kritik

Einmalige KI-Kritik durch genau einen schreibgeschützten Claude-Code-Prüfagenten (Rolle „Explore",
keine Schreibrechte, keine Netz- oder Modellaufrufe). Die frühere Codex-Kritikerrolle „Astra" war in
dieser Sitzung nicht verfügbar. Bestätigt: alle Blockerzeilen, das Fehlen eines Live-Wegs zum
AA-P10-Bundle ohne Gate-Änderung, die Adapterbefunde und die Kostenarithmetik. Korrigiert wurde in
einer Runde: Legacy-`run`/`run_library` berechnen P8 und die P9-Erstbewertung durchaus live; vorher
stand fälschlich, sie umgingen P8/P9. Ergänzt wurden die Belegzeile zu `DEFAULT_MAX_TOKENS` und die
Kennzeichnung dokumentationsbasierter Aussagen. Das Urteil bleibt unverändert. Keine
Produktänderungen.

## Grenzen

Keine Generierung, keine Fallauswahl, keine fachliche Sichtprüfung. Die Tokenkalkulation ist eine
Schätzung. Die Preisangaben stammen aus der Dokumentation vom 11.10.2026. Die Abrechnung von
Thinking-Tokens als Ausgabe wurde nicht gesondert auf der Preisseite nachgewiesen.

## Nächster sinnvoller Schritt

Ein separater, ausdrücklich genehmigter Arbeitsauftrag „AA-P10 Live-Integration" mit eigenem Vertrag:

- Ein Live-Modus im kanonischen `audit`-Pfad, der Live-Provenienz wahrheitsgemäß ausweist:
  angeforderte und zurückgegebene Modell-ID, Request-IDs, Effort-Profil, `config` ungleich
  `offline-recording-v1`.
- Eine neue, versionierte `provenance`-Kontrolle, die Live statt Offline korrekt bindet. Das
  bestehende Offline-Gate wird dabei nicht abgeschwächt.
- Echte USD-Reservierung pro Aufruf im bestehenden `BudgetLedger`, einschließlich P9, mit
  SDK-Retries 0 oder einzeln budgetiert.
- Ein 5.5-kompatibler Adapter ohne Samplingparameter, mit Content-Block-Auswahl (Text statt Thinking),
  eingefrorenem Effort-Profil und einem `max_tokens`, das Thinking und das Phase-8-JSON trägt.
- Ein Budget, das zum Ausgabeumfang passt: entweder mehr als 2,00 USD für 40 Versuche oder weniger
  P9-Versuche.

Erst danach ist der hier verlangte Sechs-Fall-Smoketest auf dem kanonischen Pfad technisch
durchführbar.
