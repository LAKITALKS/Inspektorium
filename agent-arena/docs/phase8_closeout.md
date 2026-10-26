# Phase 8 — lokaler Abschluss

Status: **PHASE_8_PASS** für die lokale Implementierung im beschriebenen Prüfungsumfang.
Maßstab ist der vorab
eingefrorene Vertrag **AA-P8/1.0**, abgeleitet aus dem bereitgestellten Blueprint.

## Implementierung und Kriterien

| Arbeitspaket | Implementiertes Verhalten | Kanonische Kriterien |
|---|---|---|
| WP1 | Striktes Proposition-Ledger, Originalspannen, gebundene IDs, Pflicht-/Kontextkomponenten, AND/OR, getrennte Zustände | 8.2, 8.9, struktureller Anteil 8.12 |
| WP2 | Population/Endpunkt/Comparator/Produkt, Evidenzfähigkeit und Directness, Inferenzbrücken, Negativbefunde, Abhängigkeit, Transformationsaudit, vollständige Quellen-/Urteilskette | 8.3–8.8, 8.10–8.12 |
| WP3 | Spezifischer Trigger plus Kernfehler, gebundene Taxonomiebegründung, Compositegrenzen, Originalklassifikation getrennt | zusätzliche CvC-Aufgabe |
| Vertrag und Abnahme | Vorab-Vertrag, generische Fehler-/Gegenfälle, 18 separat eingefrorene Offline-Abnahmefälle, vollständige Suite und Berichtskritik | 8.1, 8.13, 8.14 |

Die Umsetzung liegt in `phase8_models.py`, `phase8_semantics.py`,
`phase8_pipeline.py` und `phase8_taxonomy.py`. Sie ist im bestehenden Runner,
Parser, Evaluator, Library-Datensatz und den bestehenden Renderern verdrahtet.
Neue Analysen verwenden den registrierten v3-Prompt. Explizite historische
Bedingungen und ihre Promptbytes bleiben erhalten; fehlende Phase8-Analyse wird
als `not_executed` sichtbar. Alle fünf bestehenden Phase7-Kontrollen werden
wiederverwendet. Die offizielle Release-Coverage wird nicht abgeschwächt.

Beispiel: Ein hochkonfidentes `solid` mit Mausbefund für behaupteten menschlichen
klinischen Nutzen bleibt als Originalantwort erhalten; fehlende Passung begrenzt
die abgeleitete Bewertung. Eine unzulässig stärkere Zusammenfassung wird
`incomplete/UNKNOWN`. Ein korrekt begrenzter Mausmechanismus kann dagegen
weiterhin `completed/supported` erreichen. Generische ungestützte Wirksamkeit
wird bei entsprechender gebundener Annotation zu `overclaim`, ohne das rohe
Modelllabel CvC umzuschreiben. Gestützte ODER-Aussagen werden nicht wegen einer
ungestützten Alternative pauschal abgewertet.

## Tatsächliche Prüfung

- Ausgangsprüfung: 380 Tests bestanden. WP1: 54 bestanden.
- Eingefrorener Abnahmekorpus: 18/18 bestanden beim ersten Lauf; Erwartungen
  unverändert. Hash und Fälle stehen im Prüfjournal.
- Erster vollständiger Lauf: 2126 bestanden, 2 fehlgeschlagen (344,71 s).
  Beide veralteten Testannahmen wurden korrigiert: neuer Standardprompt plus
  expliziter historischer Prompt; verbrauchter Experiment-Freeze muss heutigen
  Quelldrift ablehnen. Historische Artefakte und Produktionsgates blieben erhalten.
- Letzte gezielte Prüfung: 188 bestanden (3,79 s).
- Finale vollständige Suite auf Codecommit `d17bb58`: **2129 passed in 360.11s**, Exit 0.
- Ruff auf allen neuen Phase8-Modulen/Testdateien, `compileall -q src/agent_arena`
  und `git diff --check`: bestanden. In drei bestehenden Produktionsdateien bleiben elf vorher
  vorhandene Ruff-Befunde, im nun ebenfalls angepassten historischen Fortsetzungstest
  weitere 25. Keine neuen Fehlersignaturen; kein globaler Ruff-PASS. Kein Typchecker konfiguriert.

Befehle und Zwischenresultate: `docs/phase8_review_journal.md`. Vollständiger
Testbefehl: `.venv/bin/python -m pytest -q`.

## Kritik und Grenzen

Vertrag: eine Kritik vor Freeze, drei Präzisierungen übernommen. WP1: Erstreview,
keine Korrekturrunde. WP2: Erstreview plus zwei Korrekturrunden; Report-Umgehung,
Review-Gegenrichtung/Directness und Suchscope-Bindung geschlossen. WP3: Erstreview
plus zwei Korrekturrunden zu Gesamtlogik und korrekter Triggerbindung;
alle materiellen Befunde geschlossen. Abschlussbericht durch denselben Kritiker kurz gegen Diff und tatsächliche
Prüfergebnisse geprüft: keine materiellen Korrekturen.

Implementierer: GPT-6 Astra High; Kritiker: GPT-6 Astra Extra High. Koordinator
blieb Astra Extra High; diese offengelegte Abweichung wurde nach dem
Konfigurationscheckpoint mit „ok mach weiter“ zur Fortsetzung akzeptiert.
Frühere Sol-High-/Astra-High-Rollen lieferten nur Leseübergaben und blieben inaktiv.

Dies belegt lokale Implementierung, Offline-Vertragsprüfungen und KI-Codekritik.
Es belegt keine korrekte Modell-Extraktion, vollständige Literatursuche,
universelle Semantik, wissenschaftliche Replikation oder verbesserte Live-Accuracy.
Quellenzitatbindung beweist keine inhaltliche Ableitung; Trigger und Attribute
bleiben extraktionsabhängig. Live-Modellausgabe und Tokenbudget-Tauglichkeit
wurden nicht empirisch geprüft. Semantischer Status und Taxonomiestatus werden
getrennt angezeigt; unbekannte Klassifikation bleibt unbekannt.

Phase9/10, breitere Ontologien, statistische Evidenzbewertung und der später
separat autorisierte Wirksamkeitsvergleich bleiben nachgelagert. Kein neuer
Projektmodell-/Providerlauf, Push, Release oder Tag ausgeführt.

## Lokaler Stand

Branch: `codex/phase8-deep-forensics-20260930`, Ausgang `6d0d5cc`.
Checkpoints: `550f1d7`, `c3bae56`, Vertrag `d1b140f`, WP1 `35e34e2`,
WP2 `9545915`; WP3 `d17bb58`. Jeder neue Commit verwendet als Author
und Committer **Lazaros Varvatis <varvatislazaros@gmail.com>**, ohne Coauthor.
Code und Tests sind vollständig committed; die zwei Abschlussdokumente bilden
einen separaten abschließenden Commit. Versionierter Arbeitsbaum nach Abschluss
sauber; vorhandene fremde unversionierte Dateien bleiben separat.
Vorhandene fremde unversionierte Dateien werden nicht gestaged. Kein Remote
konfiguriert. Es wurden ausschließlich lokale Phase8-Arbeiten beauftragt.
