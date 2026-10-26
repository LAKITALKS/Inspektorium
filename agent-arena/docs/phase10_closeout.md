# Phase 10 — lokaler technischer Abschluss

Stand: 10.10.2026. **PHASE_10_PASS** — lokaler technischer Abschluss aller verpflichtenden Kriterien10.1–10.14; Abschlussbericht nach einmaligem unabhaengigem Evidenzabgleich freigegeben. Vertrag **AA-P10/1.0**, ausschließlich aufgezeichnete Offline-Ausführung. Kein Live-Betrieb, Wirksamkeitsnachweis oder öffentliches Software-Release.

## Kriterien und Nutzerablauf

| Kriterien | Implementierung und Nachweis |
|---|---|
| 10.1–10.2 | `audit` integriert echten Runner, Parser, P8, P9, feste Kontrollen und unveränderliche Bundle-Revisionen. |
| 10.3–10.5 | Gemeinsame semantische Projektion für Markdown/HTML; Claim, Urteile, Evidenz, Grenzen, UNKNOWN und Historie bleiben sichtbar. |
| 10.6–10.7 | Druckbares HTML; tatsächliche Datei-, Referenz-, Paritäts-, Browser- und Druckprüfung. Kanonisches PDF ausdrücklich **nicht unterstützt**. |
| 10.8–10.10 | Gebundene Provenienz/Intent, konsistente Zustände, fünf dokumentierte CLI-Operationen und Fehlerpfade. |
| 10.11–10.12 | Frischer Clone, installiertes Wheel, neue Umgebung, README mit ausführbaren Befehlen und bestehenden wissenschaftlichen Verträgen. |
| 10.13–10.14 | Lokaler RC1 eingefroren, saubere Gesamtabnahme bestanden, alle drei Pakete durch separaten KI-Kritiker abgenommen. |

Der unterstützte Ablauf lautet `agent-arena audit validate/run/inspect/review/release`; vollständige Befehle und Exitcodes stehen im [README](../README.md). Beispiel:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install '.[dev,providers]'
.venv/bin/agent-arena audit run --offline \
  --task examples/phase10/positive-task.json \
  --recording examples/phase10/positive-recording.json --output-root reports/local-audit
```

Run liefert einen Kandidaten; `audit release` verlangt Reviewer und Grund und erzeugt eine neue gebundene Revision. Positive und begründet negative wissenschaftliche Ergebnisse wurden lokal freigegeben. Materielles UNKNOWN blieb `REVIEW_REQUIRED`; gültige menschliche Korrektur durch den P9-Pfad ermöglichte eine neue Freigabe. Nichtmaterielles UNKNOWN bleibt sichtbar und kann freigabefähig sein. Fehlende/vakante/veraltete/umgangene Kontrollen, Quellen- oder Fallbindungsfehler und manipulierte Dateien sperren. `inspect` Exit0 bedeutet Integrität, auch bei gesperrtem Status; es erzeugt keine Modellaufrufe.

## Prüfung und Reproduktion

Der Korpus **AA-P10-ACCEPTANCE/1.1** war vor deklarierter Ausführung eingefroren. Die erste Abnahme erreichte20/21 wegen einer falschen Markdown-Zeichendarstellungsprüfung im Harness. Harness1.1 dekodiert Entitäten; Erwartungen und Produkt blieben unverändert. Danach21/21, nach dem echten Referenzfix erneut21/21, ebenso in allen drei sauberen Wheel-Abnahmen. Alle früheren Ergebnisse bleiben erhalten.

49 gezielte Phase10-Tests bestanden auch direkt aus dem sauberen Wheel in15.46s; zusätzlich97 gezielte Offline-Tests für die Reproduktionskorrektur. Die erste Installation deckte neue Ruff-Defaults, fehlendes direktes httpx, Anthropic1.x/httpx2-Inkompatibilität und zwei implizite Testmanifestpfade auf. Eng korrigiert: bisherige Ruff-Policy explizit, Abhängigkeiten deklariert, Anthropic<1, bestehender expliziter Checkout-Parameter. Keine wissenschaftlichen Erwartungen abgeschwächt.

Sechs tatsächliche Chrome154-Ausgaben bei1280/390px sowie A4-Druck mit14/14/14/22/63/30Seiten geprüft. Alle sichtbaren Textwerte erhalten; elf neue Browser-/Druckbilder repräsentativ angesehen, ohne materiellen Layoutverlust. Kritiker sah zusätzlich drei aktuelle Bilder. Nur diese Stichprobe ist visuell abgenommen; PDF-Dateien sind reine Druck-QA-Evidenz. Archive und exakte Hashes: [Rendernachweis](../analysis/phase10_validation/wp2-r1-evidence-index.json).

Ausgeführte saubere Reproduktion:

```sh
python3 scripts/phase10_clean_reproduce.py \
  --scratch /tmp/agent-arena-p10-clean-rc3 \
  --output analysis/phase10_validation/clean-rc3 --full-suite
```

Für Wiederholung neue Verzeichnisse wählen. Python3.11.7; normale Wheel-Installation fuer kanonischen Betrieb und separate frische Editable-Installation desselben sauberen Commits fuer die sourcegebundene Bestandssuite. Beide Herkunftsorte und alle72 Modulbytes separat verifiziert; identische Dependency-Versionen, kein Entwickler-PYTHONPATH, private Fixture oder Originalcheckout-Fallback. Wheel0.1.0 erfolgreich gebaut. Die erste Vollsuite im Wheel-Layout scheiterte mit68 Fehlern bei2271 bestandenen Tests; der unveraenderte Source-Origin-Guard erkannte das unpassende Testlayout korrekt. Beide Volltests bleiben dokumentiert. Nach dem Nutzungslimit wurde der bereits abgeschlossene Lauf aus seinen bestehenden Logs fortgesetzt, nicht erneut gestartet. Erneute Gesamtsuite: **2339 passed,1 warning in413.28s**, Exit0. Finaler Checkout unveraendert. Die Warnung betrifft eine bestehende Pytest-Parametrisierung, keinen fehlgeschlagenen Test.

Belege: [RC1](../analysis/phase10_validation/RC1.json), [Reproduktion](../analysis/phase10_validation/clean-rc3-reproduction.json), [Gesamtsuite](../analysis/phase10_validation/full-suite-clean-rc3.log), [21 Abnahmen](../analysis/phase10_validation/acceptance-clean-rc3.json). Vollstaendige Laufdaten im bytegeprueften `clean-rc3.tar.gz`; vorherige Fehlversuche ebenfalls archiviert.

## Kritik, Grenzen und Git

Vertragskritik einmal; WP10.1 und WP10.2 jeweils Erstkritik plus eine Korrektur/Nachprüfung, danach abgenommen. WP1 band den vollständigen Release-Intent; WP2 reparierte und prüft reale Historienreferenzen. WP10.3: R1 zum Gesamttestlayout nach Korrektur/Nachpruefung1 geschlossen. Kritiker bestaetigte beide Installationsorte,72 Moduldateien,28 Dependency-Versionen sowie206 Archivmitglieder unabhaengig. Alle drei Pakete ohne materiellen Restbefund abgenommen; jeweils zweite Korrekturrunde unbenutzt. Einmalige Abschlussberichtskritik abgeschlossen und freigegeben; keine materiellen sachlichen Abweichungen.

Koordinator: akzeptierte Astra-Extra-High-Sitzung; genau zwei wiederverwendete Rollen: Implementierer Astra High, Kritiker Astra Extra High. Zuweisung/Wiederverwendung dokumentiert; Backendoptionen nicht unabhängig auslesbar. Keine neuen Agenten oder rekursive Delegation.

Grenzen: Offline-Testfreigaben sind keine Kundenfreigaben. Keine Aussage über Accuracy, umfassende Suche, Reviewerqualität oder wissenschaftliche Wahrheit; Hashes sind keine Identitätsauthentifizierung. Python>=3.11 deklariert, nur die dokumentierte Plattform tatsächlich geprüft. Ausführliche Historien können63 Druckseiten erzeugen. 125 historische Ruff-Befunde bleiben separat dokumentiert; kein globaler Ruff-/Typchecker-PASS.

Branch `codex/phase10-operational-release-20261010`; getesteter Codecommit `5f80c87022e569135d003aebfa9d6edcdb0efa24`. RC-/Evidenzcommit `5a6874a`; nachfolgender separater Dokumentationsabschluss wird im Gitlog und in der Abschlussantwort ausgewiesen. Seit dem Codecheckpoint keine Produkt-, Test- oder Guardaenderung. Author und Committer aller neuen Commits: Lazaros Varvatis <varvatislazaros@gmail.com>. Fremde unversionierte Dateien bleiben erhalten und ungestaged. Kein Push, PR, Merge, Tag, Deployment, Live-Modellaufruf oder Phase11. Nach lokalem Abschluss stoppen.
