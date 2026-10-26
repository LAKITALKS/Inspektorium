# AA-P8/1.1–1.3 und AA-P9/1.1–1.3 — Modell-/Host-Trennung und verpflichtende Konfliktprüfung

Stand: 11.10.2026, Paket-B-Ergänzung (§8) 12.10.2026, v1-Abschluss (§9) 13.10.2026. Nachtrag zu `phase8_semantic_contract.md` (AA-P8/1.0), `phase9_review_contract.md`
(AA-P9/1.0) und `phase10_live_addendum.md` §8.

Autorisiert durch den Auftrag „C25 korrigieren, verpflichtende P9-Konfliktprüfung und Gesamtdiagnose
P1–P10“ vom 11.10.2026. Historische Verträge, Prompts, Profile, Rohantworten, Erwartungen und
Bundles bleiben unverändert. Dieses Dokument ändert nur die Semantik **neuer** Auswertungen.

## 1. Korrektur früherer Deutungen (Nachtrag)

- **Alte Aussage:** Addendum §8 und Bericht `analysis/live_smoke_20261011/LIVE_INTEGRATION_AND_SMOKE_REPORT.md`
  §11.3 sagten: „Ein `asserted_state`, der vom Host-Zustand abweicht (C25), ist ein Befund der
  Ausgabeprüfung, also Modellqualität.“
  - Das war eine vorab festgelegte Stopp-Regel gegen nachträgliches Anpassen, **kein empirischer
    Befund**.
  - In der Nachdiagnose der 12 abweichenden R1-Propositionen ist kein Modellfehler belegt.
    Zahlen mit Nennern: `analysis/c25_p9_20261011/` (Prüfjournal).
- **Alte Aussage (Bericht §11.4):** „Leere Extraktions-`from_attributes` sind ein Modellfehler gegen
  C25.“
  - Der Vertragstext war widersprüchlich: C23 nannte `from_attributes` für die Extraktion nicht,
    C25 prüfte sie trotzdem.
  - Die Ursache liegt mindestens teilweise in der Vertragslücke.
- **Alte Regel AA-P9/1.0 Nr. 1** („A Phase8 ceiling within one position is not a disagreement“) wird
  für Modell-/Host-Abweichungen durch §5 ersetzt.

## 2. Zwei getrennte Bewertungen je Proposition und Gesamtaussage (AA-P8/1.1)

| Feld | Bedeutung | Quelle |
|---|---|---|
| `reported_verdict` | Urteil des Modells je Proposition, unverändert | Modellantwort |
| `model_composite_state` | UND/ODER-Verknüpfung der Modellurteile der Pflichtpropositionen | Host-Berechnung aus Modellwerten |
| `host_state` | Reine Evidenzableitung des Hosts **ohne** Rückgriff auf das Modellurteil, mit Gründen | Host, Regelversion `host_rule_version` |
| `host_composite_state` | Verknüpfung der Host-Zustände | Host |
| `derived_state` / `composite_state` | Wirksamer Zustand: gleich `host_state`, wenn Modell und Host übereinstimmen; sonst `unknown` (offener Konflikt) | Host |
| `model_host_conflicts` | Liste der Abweichungen je Proposition und auf Gesamtebene | Host |

- **Keine Überschreibung:** Kein Modellurteil wird mit dem Host-Zustand überschrieben, und
  `asserted_state` wird nie aufgefüllt. Eine Neuberechnung ist eine Host-Ableitung, keine
  Modellantwort.
- **Alte Vermischungsregel entfällt:** Die Regel C29 entfällt („gemeldetes unknown erzwingt unknown;
  abweichendes unsupported/contradicted wird unknown“). Damit ist der `unknown`-Ausweg geschlossen:
  Modell `unknown` gegen klares Host-Urteil ist ein Konflikt.
- **Getrennte Eigenschaften:** Technische Vollständigkeit, wissenschaftlicher Zustand, Konflikt,
  Reviewpflicht und Freigabefähigkeit bleiben getrennt.
  - Eine Abweichung allein macht eine Analyse **nicht** technisch unvollständig.
  - Schema-, Referenz-, Quellen- und Transformationsfehler sperren weiter.
- **Der Host ist kein Goldstandard.** Sein Zustand ist eine deterministische Ableitung aus den vom
  Modell dargestellten Feldern, mit dokumentierten Grenzen.

## 3. Ausgabeprüfung (C25 neu) und Extraktion (C23 neu)

- **Innere Konsistenz der Modellausgabe** (bleibt harte Prüfung):
  - Ein gesetzter `asserted_state` muss dem **eigenen** Modellurteil entsprechen: bei einer Proposition
    deren `reported_verdict`, bei `asserts_whole_claim` dem `model_composite_state`.
  - Eine Abweichung ist der Befund „output state changes the model's own judgment“. Er macht die
    Analyse technisch unvollständig.
- **Summary-Ausgaben** brauchen weiterhin einen `asserted_state`.
- **Unzulässige Transformationen sperren weiter:** Attributänderung, Hedge-Verlust und
  Teil-zu-Ganz-Erhöhung, gemessen am eigenen Modell-Gesamturteil.
- **Extraktion:**
  - `from_text` = Spantext, `to_text` = Propositionstext, `to_attributes` = Propositionsattribute
    (unverändert geprüft).
  - `from_attributes` ist entweder gleich den Propositionsattributen oder vollständig leer.
  - Ist es leer, nutzt der Host für die Bedeutungsprüfung die bereits validierten
    Propositionsattribute. Er vermerkt das sichtbar (`host_derived_copies`) und schreibt dem Modell
    keinen Inhalt zu.
  - Teilweise gefüllte, abweichende `from_attributes` bleiben eine Attributänderung.
- **Alte Antworten** müssen nicht jede neue Prüfung bestehen. Fehlende Pflichtinhalte werden nicht
  nachträglich dem Modell zugeschrieben.

## 4. `comparison` (Evidenzfähigkeit kontrollierter Interventionen)

| Situation | Darstellung | Host-Zustand und Begründung |
|---|---|---|
| 1. Quelle nennt einen Vergleich, Extraktion lässt ihn weg | `comparison` leer/unknown | `unknown`: „comparison not represented“; keine Designaussage |
| 2. Quelle beschreibt ein Design ohne Vergleichsgruppe | `comparison` = `within` | `unsupported`: Veränderung innerhalb eines Arms belegt keinen Gruppeneffekt |
| 3. Ausschnitt lässt das Design offen | `comparison` leer/unknown | `unknown` wie 1. Der Host kann 1 und 3 ohne Textverständnis nicht unterscheiden und sagt das auch nicht |
| 4. Vergleich für die Proposition nicht anwendbar (deskriptive Relation, Assoziation) | an der Proposition leer | Die Fähigkeitsregel zieht `comparison` nicht heran; keine Vergleichsbegründung |

Unbekannte Werte außer `between`/`within` ergeben `unknown` mit dem Grund „unrecognized comparison
value“. Fehlende Information und belegte fehlende Vergleichsgruppe werden nie verwechselt.

Präzisierung nach der Erstkritik (A-C11): Die Tabelle betrifft die Fähigkeitsregel. Unabhängig davon
vergleicht die unveränderte Rohattributprüfung C14 jede Dimension, die die Proposition selbst setzt
oder als materiell nennt, also auch `comparison`, bei jeder Relation.
- Fehlt der Wert an der Evidenz, bleibt die Bindung unaufgelöst (`unknown`).
- Weicht er ab, ist sie `unsupported`.
- Bleibt `comparison` an der Proposition leer, wird es nicht verglichen.

Die Wirkung ist konservativ und unverändert gegenüber AA-P8/1.0.

## 5. Verpflichtende Konfliktbehandlung und Routing-Priorität (AA-P9/1.1)

- **Konflikt:** `reported_verdict ≠ host_state` bei einer Proposition, oder
  `model_composite_state ≠ host_composite_state`. Das gilt in beiden Richtungen und auch bei klarem
  Host-Urteil; es gibt keine Rangordnung der Zustände.
- **Materiell** ist ein Konflikt:
  - immer auf Gesamtebene;
  - bei einer Proposition, wenn ihr Zustand die Gesamtaussage oder eine entscheidende Ausgabe ändern
    kann. Prämissen erben die Materialität (bestehende P9-Logik).
- **Verpflichtender Auslöser:** Jeder materielle Konflikt erzeugt `model_host_conflict` mit
  `mandatory=true`.
- **Nichtmaterielle Konflikte** bleiben sichtbar (`bounded_model_host_conflict`). Sie sperren die
  Freigabe nicht, weil der Auftrag die Pflichtprüfung für jede **materielle** Abweichung verlangt.
  - Ihr Ort bleibt wirksam `unknown`.
  - Bericht und Projektion weisen sie als „offen, nicht materiell, nicht geprüft“ aus.
- **Host-Gründe** (`host_reasons`) enthalten nur vom Host formulierte Sätze (Erstkritik A-C7 und
  Nachprüfung N-R2).
  - Die Bindungsbegründung des Modells steht nur in den allgemeinen Gründen der Proposition, nie unter
    der Host-Position.
  - Vom Modell vergebene Bindungs- und Brücken-IDs werden durch Ordnungsnummern ersetzt
    („binding 1“, „required bridge 1“).
  - Zitiert wird nur ein unbekannter `comparison`-Wert, gekürzt auf 40 Zeichen und als Wert erkennbar.
  - Alle übrigen Werte sind validierte Literale oder Feldnamen.

| Lage | Verbindliches Verhalten |
|---|---|
| Beschädigte Herkunft, falsche Fallbindung, strukturell unbrauchbare Analyse | Bestehende harte Sperre (PREFLIGHT_BLOCKED, ANALYSIS_INCOMPLETE, Herkunftskontrolle); ein Konfliktflag umgeht sie nicht |
| Bestehende zwingende menschliche Prüfung (technischer Fehler, materieller Positionskonflikt) | HUMAN_REVIEW_REQUIRED bleibt vorrangig |
| Technisch auswertbare Analyse mit materiellem Modell-/Host-Konflikt | REVIEW_RECOMMENDED mit `mandatory=true`; Gegenprüfung über den kanonischen Reviewpfad |
| Materielles UNKNOWN ohne Konflikt | Bestehende Regeln (necessary_unknown, keine Freigabe eines materiellen UNKNOWN); Gleichheit unknown/unknown ist kein Freigabebeweis |
| Vollständig, konsistent, ohne Konflikt oder andere Pflicht | Regulärer Entscheidungsweg |

- **Gegenprüfung bei Konflikt:**
  - Das Prüfpaket enthält die Evidenz wie bisher und zusätzlich beide Positionen je Konflikt:
    Modellurteil mit Begründung und Host-Zustand mit Gründen und Regelversion. Beide sind als
    ungeprüfte Behauptungen markiert.
  - Ohne Modell-/Host-Konflikt bleibt das Paket blind wie in AA-P9/1.0.
  - Die Stabilitätsvariante kehrt nur die Evidenzreihenfolge um; die Konfliktangaben bleiben gleich.
  - **Reviewprompt:**
    - Live nutzt jedes Profil seinen gebundenen Reviewprompt (@3: `…-r2-review-p9-2`).
    - Offline erhält ein Paket mit Konflikten ebenfalls den AA-P9/1.1-Reviewprompt. Der blinde
      AA-P9/1.0-Prompt bleibt für Pakete ohne Konflikt.
    - Der Unabhängigkeitsvermerk des Versuchs nennt die mitgelieferten Positionen statt „First verdict
      withheld“.
- **Zulässige Auflösung:** **nur** eine echte menschliche Adjudikation über die bestehende API.
  - Sie wählt eine revalidierte Position ohne offenen materiellen Konflikt und mit nicht-unknown
    Gesamtzustand, oder sie reicht eine revalidierte Korrektur ein.
  - Modell-Gegenprüfung und Stabilität liefern nur zusätzliche Positionen. Sie schließen keinen
    Konflikt, auch nicht durch Wiederholung desselben Urteils.
  - Nach abgeschlossener Gegenprüfung bleibt der Fall HUMAN_REVIEW_REQUIRED.
- **Offen und sperrend** sind fehlender, verweigerter, budgetbedingt nicht ausgeführter,
  fehlgeschlagener oder unklarer Pflichtreview (UNRESOLVED). Keine automatische Freigabe.

## 6. Versionen

- **Bewertung:** AA-P8/1.1, seit Paket B AA-P8/1.2 (§8) (`host_rule_version` = `AA-P8-HOST/1.1`). Das Ausgabeformat der
  Modellantwort (Ledger `contract_version` = `AA-P8/1.0`) bleibt unverändert.
- **Reviewvertrag:** AA-P9/1.1, seit Paket B AA-P9/1.2 (§8). Gespeicherte AA-P9/1.0-Fallzustände werden nicht stillschweigend
  übernommen; sie scheitern geschlossen.
- **P10-Kontrollregister:** `phase8_semantics_taxonomy` und `phase9_history_review` erhalten Version
  1.1, seit Paket B 1.2 (§8).
- **Prompts:** `study_forensics_prompt/v3-phase8-contract-r2` und `…-r2-review-p9-2`.
  - Sie erklären Zuständigkeiten und Ausgabevertrag neu: eigenes Urteil, kein Erraten des
    Host-Zustands, C23/C25 neu, `comparison`.
  - Keine Erwartungslabels, Goldfelder oder fallspezifischen Lösungen.
- **Profile:** `claude-haiku-5-5@3` und `claude-sonnet-5-5@3`.
- Der r2-Text erklärt, dass er die AA-P8/1.0-Verweise des unveränderten v3-Präfixes ersetzt. Er
  unterscheidet materielle Abweichungen (Pflichtreview) von nichtmateriellen (sichtbar offen); das ist
  die Präzisierung nach Erstkritik A-C8.

## 6a. Live-Nachfolgeautorisierung (Schema `aa-p10-live-authorization/1.1`)

Nachgeschärft nach der Erstkritik (A-C1 bis A-C5, A-C9) und ihrer Nachprüfung (A-R1 bis A-R3):
- **Festgeschriebene geschlossene Historie:** `KNOWN_CLOSED_AUTHORIZATIONS` hält `-002` und `-003`
  mit dem SHA-256 ihres geschlossenen Ledgers und ihrer Autorisierungsdatei. Die Autorisierungsdatei
  legt das kanonische Verzeichnis fest.
  - Ein neues Live-Budget muss ein Nachfolger nach Schema 1.1 sein und jeden Eintrag mit genau diesen
    Bytes aufführen.
  - Schema 1.0 bleibt für Replay gültig.
  - Live öffnet eine festgeschriebene ID nur als sie selbst: unveränderte Datei und vorhandener,
    geschlossener Ledger. Sie erhält nie einen frischen Ledger (A-R1).
  - Jede andere Autorisierung nach Schema 1.0 wird live abgewiesen.
- **Vollständige, echte Kette:**
  - Jeder Vorgänger wird aus seinem eigenen `canonical_directory` gelesen.
  - Sein Ledger ist an genau diese Autorisierungsdatei gebunden (`binding.authorization_fingerprint`).
  - Die Liste ist abgeschlossen unter den `supersedes`- und `predecessors`-Einträgen der Vorgänger,
    einschließlich der dort festgehaltenen Ledger-Hashes.
  - Genau ein Vorgänger ist der jüngste.
  - Ein nicht festgeschriebener Vorgänger zählt nur, wenn er ein Nachfolger nach Schema 1.1 ist und sein
    eigener jüngster Vorgänger ihn im Nachfolgeanspruch mit ID, Verzeichnis und Autorisierungs-Hash
    ausweist (A-R2). Kopien, umgeschriebene Autorisierungen und handgeschriebene „Vorgänger“ binden
    daher nichts.
- **Kein paralleles Budget:** Beim ersten Öffnen seines frischen Ledgers schreibt der Nachfolger
  einmalig (`O_EXCL`) `successor_claim.json` in das Verzeichnis des jüngsten Vorgängers.
  - Ein zweiter Nachfolger desselben Vorgängers wird abgewiesen.
  - Ledger und Autorisierung des Vorgängers bleiben bytegleich; der Anspruch ist eine neue Datei.
  - Er wird mit den Belegen des Nachfolgers versioniert, damit ein Löschen sichtbar wird.
- **Lebenszyklus des Anspruchs (N-R1):** Alle Fälle schließen geschlossen.
  - Ein Anspruch bleibt bestehen, auch wenn die Ledger-Erzeugung danach scheitert.
  - Wird die Autorisierung des Nachfolgers später geändert, sperrt das diesen Nachfolger.
  - Behebung nur durch Wiederherstellen der Originalbytes oder durch eine dokumentierte menschliche
    Entscheidung.
- **Grenzen:**
  - Wer lokale Dateien von Hand ändert oder löscht, kann jede dateibasierte Sperre umgehen.
    Festgeschriebene Hashes und versionierte Ansprüche machen solche Eingriffe sichtbar; verhindern
    können sie sie nicht.
  - Live-Ausgaben sind nur aus diesem Checkout möglich (absolute kanonische Pfade). Replay liest keine
    Vorgänger.
- **Reviewgrenzen:** je Profil und Art 0 oder 1.
  - Die Live-Entscheidung wird vor dem Request im Ledger festgehalten (`review_cap_claims`).
  - Replay reproduziert genau diese Entscheidung.
  - Eine Ablehnung trägt ihren Grund im P9-Versuch.
  - Ist der Ledger zur Reviewzeit nicht ACTIVE (etwa nach einer Kostenüberschreitung), wird der Review
    mit diesem Grund abgelehnt, statt den Lauf abzubrechen (A-R3).
  - Replay unterscheidet „Grenze erreicht“ von „keine Live-Freigabe festgehalten“.
  - Ein live freigegebener, aber nie gesendeter Review wird als nicht gesendet nachgespielt, mit einem
    allgemeinen Grund. Status und Positionen stimmen überein (N-R3).
- **Nur r2-Profile:** Ein Nachfolger darf nur Profile freigeben, die die AA-P8/1.1-Prompts binden.
- **Replay** prüft die Struktur. Es liest keine Vorgänger-Ledger, denn Replay gibt nie Geld aus.

## 7. Vorab festgelegte Prüfkriterien (vor der Implementierung)

| ID | Kriterium |
|---|---|
| K1 | Alle 16 Kombinationen Modell × Host (4 × 4 Zustände): Konflikt genau bei Ungleichheit; Route und Freigabe getrennt geprüft |
| K2 | Materieller Konflikt trotz klarem Host-Urteil, in beiden Richtungen, und Modell-`unknown` gegen klares Host-Urteil ergeben einen verpflichtenden Auslöser und REVIEW_RECOMMENDED; keine Freigabe |
| K3 | unknown/unknown mit materiell fehlender Evidenz bleibt ungeklärt und nicht freigabefähig |
| K4 | Struktur-, Quellen- und Herkunftsfehler bleiben harte Sperren, auch mit Konflikt |
| K5 | Ein vollständiger positiver und ein vollständig begründeter negativer Fall bleiben regulär (AUTO_RESOLVABLE, READY_FOR_RELEASE) |
| K6 | Der Pflichtreview wird ausgelöst und erhält beide Bewertungen samt Evidenz. Bei Fehler, Verweigerung, Budgetstopp oder Unterbrechung bleibt er offen; abschließbar nur durch menschliche Adjudikation |
| K7 | Konflikt und Historie überstehen Speichern, Laden, Replay und unterbrochene Fortsetzung |
| K8 | Die vier `comparison`-Situationen ergeben passende Zustände und zutreffende Begründungen |
| K9 | Der Extraktionsvertrag hat keine gegensätzlichen Kopierregeln. Host-Kopien sind eindeutig und sichtbar gekennzeichnet; einer Altantwort wird kein Inhalt zugeschrieben |
| K10 | Berichte zeigen Modell- und Host-Urteil, Konflikt, Gründe und tatsächlichen Reviewstatus; bei offener Pflicht kein Freigabestatus |
| K11 | Ein echter P9-Ablauf durch den kanonischen Einstieg mit Transport-Double ist offline nachgewiesen |
| K12 | Alle 24 vorhandenen Captures sind unter dem neuen Vertrag neu ausgewertet und den Originalergebnissen gegenübergestellt; jede Abweichung ist begründet. Die vier Herkunftsarten bleiben getrennt: Originalprüfung, Neuauswertung, Synthese, neue Generierung |
| K13 | Bisherige Offline-Abnahme 21/21; eine technische Erwartungsänderung wird getrennt von wissenschaftlichen Sollantworten ausgewiesen |

## 8. Korrekturen aus der Gesamtdiagnose (Paket B) — AA-P8/1.2 und AA-P9/1.2

Belegt in `analysis/c25_p9_20261011/PACKAGE_B_DIAGNOSIS.md`. Sie ändern Routing und Vollständigkeit.

- **Versionen:**
  - Bewertung **AA-P8/1.2**, Reviewvertrag **AA-P9/1.2**.
  - P10-Kontrollregister, gilt für offline wie live:
    - `phase8_semantics_taxonomy` und `phase9_history_review` **1.2**;
    - `input_preflight` **1.1**: Kuratierte Fälle werden abgewiesen;
    - `evidence_symmetry` **1.1.0**: `material=false` nimmt vom Elternbefund gebundene Evidenz nicht
      mehr aus der Richtungsprüfung (P7-F1).
    - Die Registry-Fingerprints ändern sich entsprechend.
  - Unverändert bleiben `host_rule_version` (`AA-P8-HOST/1.1`, die Host-Ableitung selbst ist gleich),
    das Ausgabeformat der Modellantwort sowie die gepinnten r2-Prompts und @3-Profile. Die
    Versionsangaben „AA-P8/1.1“ und „AA-P9/1.1“ im r2-Text bezeichnen dort das Ausgabe- und
    Review-Format, das gleich bleibt.
  - Gespeicherte AA-P9/1.1-Fallzustände werden wie 1.0-Zustände nicht stillschweigend übernommen; sie
    scheitern geschlossen.
- **Materialität (AA-P9/1.2):** Eine Proposition ist auch dann materiell, wenn ein anderer Zustand von
  ihr das abgeleitete Taxonomie-Label ändern würde.
  - Das Label ist eine freigegebene, entscheidende Ausgabe (`phase10_operational_contract.md`).
  - Ein Konflikt oder ein einiges UNKNOWN auf der CvC- oder ME-Auslöseproposition wird damit
    verpflichtend geprüft (P8-F1/AF1).
- **C15 für jede Proposition (AA-P8/1.2):** Die Prüfung von Beobachtung gegen Evidenzrolle gilt auch für
  optionale Propositionen, wie im r2-Text ohne Einschränkung angegeben (P8-F2).
  - C16–C18 bleiben ausdrücklich auf Pflichtpropositionen beschränkt.
- **Kein vollständiges Ergebnis ohne Rohtext (AA-P8/1.2):**
  - Eine gecachte Analyse ohne Rohtext ist nie vollständig, weil Abschneiden, Reparatur und eine zweite
    Analyse nicht nachprüfbar sind (P1-F2).
  - Eine Antwort mit einer weiteren JSON-Analyse (`multiple_objects`) ist nie vollständig (P1-F1).
- **Host-Gründe:** Brückengründe werden bei der Erzeugung mit Ordnungsnummer gebildet und nicht
  nachträglich umgeschrieben (P8-F3).
- **Konflikt auf Claim-Ebene im Review-Paket:** Beide Positionen tragen Begründungen (P9-F5).
  - Modellseite: die Begründung der eigenen Gesamtaussage, sonst die eigenen Urteile je Proposition.
  - Hostseite: die Host-Zustände je Proposition, über Positionsnummern referenziert.
- **Modell-Adjudikation:** Herkunft und Unabhängigkeit werden aus der gebundenen Review-Position
  abgeleitet (P9-F2, BF1). Unterschieden wird:
  - offline aufgezeichnet;
  - live;
  - Replay eines Live-Laufs;
  - nie gesendeter Live-Request („Live review request not sent … no review output“, auch im Replay);
  - blind oder mit offengelegten Positionen.

  Der historische Text für blinde Offline-Reviews bleibt unverändert. Das Feld `origin`
  (`offline_comparison`) bezeichnet den deterministischen Vergleich der Positionen durch den Host,
  nicht die Ausführungsart des Reviews; diese steht in `reviewer_provenance`.
- **Replay (AA-P10-LIVE):**
  - **Grundregel:** Ein Review-Slot wird nur aus einer abgeschlossenen Live-Aufnahme nachgespielt, oder
    als nie gesendete, live freigegebene Anfrage. Jeder andere Review-Slot wird vor dem Reviewer
    abgelehnt, und der Review bleibt offen (P10-F1, G1, P9-F1). Das gilt für:
    - einen nie ausgeführten Review alter Historien;
    - einen unterbrochenen oder ungeklärten Request;
    - eine erreichte Grenze oder eine fehlende Freigabe.

    In diesen Fällen entsteht ein Bundle mit offenem Review statt einer falschen Herkunftssperre.
  - **Ausnahme:** Bleibt die Aufnahme eines terminalen Review-Slots aus, oder hat sich der Paketaufbau
    seit dem Live-Review geändert (P10-G2), scheitert das Replay weiterhin geschlossen.
  - **Verzeichnisbindung:** Sie gilt nur für Live-Ausgaben. Replay ist aus jeder Kopie oder jedem Klon
    möglich (K1).
  - **Bytebindung statt Ort:**
    - Eine festgeschriebene geschlossene Autorisierung replayt nur aus ihren unveränderten
      Autorisierungs- und Ledger-Bytes (BF3).
    - Jede Replay-Evidenz trägt den SHA-256 des nachgespielten Ledgers (`replay_ledger_sha256`).
  - **Zustand:** Der CLI-Replay legt seinen Phase-9-Zustand neben der Ausgabe ab, nie im
    Evidenzverzeichnis der Autorisierung.
- **Eingaben des Audit-Pfads (`input_preflight` 1.1):** Ein Task mit Gold-, Rubrik-, Kurator-,
  Bewertungs- oder Bibliotheksfeldern wird abgewiesen, bevor eine Modellnachricht entsteht
  (P2-F1/P3-F1/P6-F1).
  - Sein `context` ist Kuratorkommentar und kein Quellmaterial.
  - **Grenze:** Die Prüfung ist feldbasiert. Kuratortext innerhalb von `context` eines sonst sauberen
    Tasks erkennt sie nicht.

## 9. v1-Abschluss (13.10.2026) — AA-P8/1.3, AA-P9/1.3 und Betriebsdarstellung

Belegt in `analysis/v1_closeout_20261013/CLOSEOUT.md`. Ausgabeformat der Modellantwort (Ledger AA-P8/1.0), Prompts,
Profile und `host_rule_version` (`AA-P8-HOST/1.1`) bleiben unverändert.

- **Zusammenfassung über die ganze Aussage (AA-P9/1.3):**
  - Eine `summary`-Transformation mit `asserts_whole_claim` und einem gesetzten, nicht-`unknown` Zustand ist
    eine entscheidende Ausgabe ihrer Quellpropositionen (`from_proposition_ids`).
  - Ein Modell/Host-Konflikt auf einer solchen Quellproposition ist daher materiell und pflichtgeprüft, auch
    wenn die Proposition optional ist oder eine andere Disjunktion den Gesamtzustand trägt.
  - Bisher war diese Ausgabe von der Regel ausgenommen. Eine Kundenzusammenfassung konnte so den Inhalt einer
    konfliktbehafteten oder nicht gestützten Proposition als „supported“ freigeben (latent, in den echten
    Ledgern nicht aufgetreten).
- **Teil-zu-Ganz-Prüfung (AA-P8/1.3):**
  - Eine Zusammenfassung mit `asserts_whole_claim` und Zustand `supported` braucht neben dem gestützten
    Modell-Gesamtzustand auch Quellpropositionen, die das Modell selbst durchweg als `supported` beurteilt.
  - Andernfalls entsteht der Befund „partial-to-whole promotion“, und die Analyse ist technisch unvollständig.
- **Versionen:**
  - Bewertung **AA-P8/1.3**, Reviewvertrag **AA-P9/1.3**.
  - Registry `phase8_semantics_taxonomy` und `phase9_history_review` **1.3**, `analysis_source` **1.1**,
    `markdown_qa`/`html_qa` **1.1**.
  - Gespeicherte AA-P9/1.0–1.2-Fallzustände werden nicht übernommen; sie scheitern geschlossen.
- **Betriebsdarstellung ohne menschlichen Prüfer (AA-P10, Projektion):**
  - Jede Revision sagt, dass die automatische Bearbeitung beendet ist. Die Zeile `open cause` leitet aus
    vorhandenen Feldern ab, warum der Fall offen ist:
    - Pflichtreview nicht ausgeführt, mit Grund (verweigert, nicht gesendet, abgelehnt, unterbrochen);
    - ausgeführt, Konflikt weiter offen;
    - ausgeführt, aber fehlgeschlagen;
    - technisch unvollständig, mit Grund.
  - Es gibt keinen neuen Zustand. `HUMAN_REVIEW_REQUIRED` bleibt die interne Kennung für „automatisch nicht
    abschließend klärbar“.
  - Fehlgeschlagene Kontrollen `analysis_source`, `phase8_semantics_taxonomy` und `phase9_history_review`
    nennen ihre Ursache statt eines Erfolgstexts (XT-F3 für diese drei Kontrollen geschlossen).
  - Die fünf Phase-7B-Gates bleiben unverändert.
- **Nichtmaterielle Konflikte (§5):**
  - Der Bericht nennt sie offen, nicht materiell, ohne Pflichtreview und nicht geprüft.
  - Nach einer menschlichen Adjudikation heißt es „case adjudicated, conflict not closed by the adjudication“.
  - Der Satz „no recorded conflicts“ erscheint nur, wenn weder Positions- noch Modell/Host-Konflikte vorliegen.
  - Die Phase-8-Begründungstexte („mandatory review decides …“) bleiben unverändert im Record. Sie beschreiben
    die Regel für materielle Konflikte, und die Konfliktzeile des Berichts stellt den nichtmateriellen Fall klar.
    Eine Textänderung der Phase-8-Ausgabe war für den Abschluss nicht nötig und hätte über die minimale Korrektur
    hinausgegriffen.
- **Darstellungssicherheit:**
  - Steuer-, Bidi- und unsichtbare Formatzeichen in angezeigtem Text erscheinen als `⟦U+XXXX⟧`; `record.json`
    behält die exakten Zeichen.
  - Markdown gibt nie rohe Zeilenenden außer LF aus und bestätigt sie nie.
  - Überschriften nutzen Ordnungszahlen statt Modell-IDs.
  - Modell-Schlüssel können Host-Zeilen nicht ersetzen.
