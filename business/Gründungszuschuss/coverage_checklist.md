# coverage_checklist.md — Template Coverage Checklist (Agent-owned)

Purpose: Ensure **every question/prompt in** `business_plan_template with requirements.md` is either **answered** in `business_plan.md` with authoritative sources, or explicitly tracked as **missing** in `open_questions.md`.

Important: This file is intended to be **re-generated on every run** to avoid redundant state. Do not commit long-lived “pre-filled” prompt rows here.

## How it is used (run-time behavior)

- At the start of a run, populate this file with one row per template prompt from `business_plan_template with requirements.md`.
- During drafting, update rows with:
  - `Status`: `answered | information_missing | not_started`
  - `Answer location in business_plan.md`: section/heading
  - `Source(s)`: authoritative sources used (e.g. `business_plan_input.md`, `business_model_canvas.md`, `llm_exports/...`)
  - `Open question link`: if `information_missing`, add a concrete bullet to `open_questions.md` and link it here
- At the end of a run, this file may be overwritten again on the next run.

## Checklist table (populate per run)

| ID | Template prompt (verbatim) | Status | Answer location in `business_plan.md` | Source(s) | Open question link (if information_missing) | Notes / consistency hooks |
| --- | --- | --- | --- | --- | --- | --- |
| ES-01 | - Was ist der Kern deiner Idee? | not_started |  |  |  |  |
| ES-02 | - Was bietest du an? | not_started |  |  |  |  |
| ES-03 | - Wer sind deine Kunden? | not_started |  |  |  |  |
| ES-04 | - Warum wird dein Angebot für deine Kunden nützlich sein? | not_started |  |  |  |  |
| ES-05 | - Wer ist im Gründungsteam und welche relevanten Qualifikationen habt ihr? | not_started |  |  |  |  |
| ES-06 | - Ab wann wird dein Unternehmen Gewinn machen? | not_started |  |  |  |  |
| ES-07 | - Wofür benötigst du fremdes Kapital und wie viel? | not_started |  |  |  |  |
| 2-A-01 | - Was ist dein Angebot? | not_started |  |  |  |  |
| 2-A-02 | - Was genau verkaufst du damit an deine Kunden? | not_started |  |  |  |  |
| 2-N-01 | - Welche Aufgabe nimmst du deinen Kunden ab bzw. womit machst du ihnen das Leben einfacher oder schöner? | not_started |  |  |  |  |
| 2-N-02 | - Warum wird dein Angebot für deine Kunden nützlich sein? | not_started |  |  |  |  |
| 2-K-01 | - Was kannst du/kann dein Team besonders gut, das einen Wert für deine Kunden hat? | not_started |  |  |  |  |
| 2-K-02 | - Welche Fähigkeiten musst du/müsst ihr aufbauen? | not_started |  |  |  |  |
| 3-K-01 | - Was zeichnet deine Kunden aus? | not_started |  |  |  |  |
| 3-K-02 | * **Segmentierung:** Demografie, Psychografie, B2B/B2C-Spezifika. | not_started |  |  |  |  |
| 3-V-01 | - Wie erreicht das Angebot deine Kunden? | not_started |  |  |  |  |
| 3-V-02 | - Wie kommunizierst du mit deinen Kunden? | not_started |  |  |  |  |
| 3-V-03 | - Was hast du konkret geplant, um Kunden zu gewinnen und zu behalten? | not_started |  |  |  |  |
| 3-M-01 | - Wer sind deine Wettbewerber bzw. welche Konkurrenzprodukte gibt es? | not_started |  |  |  |  |
| 3-M-02 | - Wie unterscheidet sich dein Unternehmen / dein Angebot von deinen Wettbewerbern? | not_started |  |  |  |  |
| 3-M-03 | - Wie groß ist der Markt? | not_started |  |  |  |  |
| 3-M-04 | - Wie wird sich die Branche voraussichtlich entwickeln? | not_started |  |  |  |  |
| 4-T-01 | - Welche Kompetenzen, auch soziale, sind in deinem Team vereint? | not_started |  |  |  |  |
| 4-T-02 | - Aus welcher Situation und Motivation heraus gründest du/gründet ihr? | not_started |  |  |  |  |
| 4-T-03 | - Welche Aufgaben und Funktionen sollen Mitarbeiter\*innen übernehmen? | not_started |  |  |  |  |
| 4-T-04 | - Wie viele Mitarbeiter\*innen benötigst du dafür? | not_started |  |  |  |  |
| 4-T-05 | - Welche Qualifikation sollten die Mitarbeiter\*innen haben? | not_started |  |  |  |  |
| 4-W-01 | - Was ist dir wichtig, was unwichtig? | not_started |  |  |  |  |
| 4-W-02 | - Wofür soll dein Unternehmen stehen? | not_started |  |  |  |  |
| 4-P-01 | - Was können andere besser und wer ist das? | not_started |  |  |  |  |
| 4-P-02 | - Welchen Nutzen haben deine Partner davon, mit dir zu arbeiten? | not_started |  |  |  |  |
| 4-P-03 | - Welche Teilleistungen willst du an die Schlüsselpartner auslagern? | not_started |  |  |  |  |
| 4-P-04 | - Welche Kontakte hast du, die für dein Vorhaben nützlich sind? | not_started |  |  |  |  |
| 5-P-01 | - Welche Leistungen und Schritte sind erforderlich? | not_started |  |  |  |  |
| 5-P-02 | - Was davon machst du selbst, was deine Kunden, was deine Partner? | not_started |  |  |  |  |
| 5-P-03 | - Wie unterscheidet sich dein Prozess von dem deiner Wettbewerber? | not_started |  |  |  |  |
| 5-S-01 | - An welchem Standort willst du dein Vorhaben realisieren? | not_started |  |  |  |  |
| 5-S-02 | - Was zeichnet den Standort deines Unternehmens aus? | not_started |  |  |  |  |
| 5-S-03 | - Welche Räumlichkeiten stehen dir zur Verfügung? | not_started |  |  |  |  |
| 5-S-04 | - Welche Anpassungen musst du noch vornehmen? | not_started |  |  |  |  |
| 5-R-01 | - In welcher Rechtsform wirst du das Unternehmen gründen? | not_started |  |  |  |  |
| 5-R-02 | - Welche besonderen Vorschriften (z.B. Zulassungen und gewerbliche Vorschriften) musst du beachten? | not_started |  |  |  |  |
| 5-X-01 | - Welche schwerwiegenden Probleme könnten auftreten (z.B. aufwendige/ungewisse Kundenakquise; Zielkunden haben nicht den erwarteten Bedarf oder wollen kein Geld für das Angebot ausgeben; stärkerer Wettbewerb als erwartet; Schwierigkeiten, passende Mitarbeiter\*innen zu finden; Ausfall von Lieferanten; Forderungsausfälle usw.)? | not_started |  |  |  |  |
| 5-X-02 | - Für überregional tätige oder sehr innovative Unternehmen: Welche Risiken entstehen möglicherweise aus Veränderungen bei Rahmenbedingungen wie Technologie, Trends o.ä.? | not_started |  |  |  |  |
| 5-X-03 | - Mit welchen Maßnahmen planst du den Problemen und Risiken zu begegnen? | not_started |  |  |  |  |
| 6-U-01 | - Womit nimmst du Geld ein? | not_started |  |  |  |  |
| 6-U-02 | - Zu welchen Zeitpunkten fließt das Geld? | not_started |  |  |  |  |
| 6-U-03 | - Wie kalkulierst du deine Preise und wie verhalten sich diese zu den derzeitigen Marktpreisen? | not_started |  |  |  |  |
| 6-KO-01 | - Wofür gibst du im Unternehmen wie viel Geld aus? | not_started |  |  |  |  |
| 6-KO-02 | - Wie flexibel sind diese Kosten? | not_started |  |  |  |  |
| 6-KO-03 | - Welche Kosten (z.B. Waren- oder Materialeinsatz) steigen oder fallen direkt mit dem Umsatz? | not_started |  |  |  |  |
| 6-KO-04 | - Wie hoch sind die Personalausgaben für deine Mitarbeiter\*innen? | not_started |  |  |  |  |
| 6-KO-05 | - Wie hoch sind die Betriebsausgaben (z.B. Miete, Energiekosten, Versicherungen)? | not_started |  |  |  |  |
| 6-PE-01 | - Welche Lebenshaltungskosten fallen an (z.B. private Miete, Krankenversicherung, Verpflegung)? | not_started |  |  |  |  |
| 6-PE-02 | - Wie viel Einkommenssteuer musst du zahlen? | not_started |  |  |  |  |
| 6-PE-03 | - Privater Finanzbedarf (private monatliche Kosten als Tabelle), typisch für einen Monat im ersten Jahr (nach der Gründung). Bitte beachten Sie die Kranken- und Pflegepflichtversicherungen ab der Gründung, sowie die Einkommenssteuer und die Altersvorsorge | not_started |  |  |  |  |
| 6-KF-01 | - Welche Investitionen sind für dein Unternehmen notwendig (z.B. Büroausstattung, Maschinen, Gebäude, Fahrzeuge)? | not_started |  |  |  |  |
| 6-KF-02 | - Gibt es Sachen, die für dein Unternehmen notwendig sind, die du selbst beisteuerst? Wie viel sind sie noch wert (Sacheinlage, z.B. dein PC, dein Auto)? | not_started |  |  |  |  |
| 6-KF-03 | - Welche Kosten fallen einmalig bei der Gründung deines Unternehmens an (z.B. Warenerstausstattung, Gebühren für die Gewerbeanmeldung)? | not_started |  |  |  |  |
| 6-KF-04 | - Wie viel Mittel benötigst du zur Gewährleistung des laufenden Betriebes in der Anlaufphase? | not_started |  |  |  |  |
| 6-KF-05 | - Wie viel Liquiditätsreserve benötigst du als allgemeines Sicherheitspolster und um die Zeit zwischen Aus- und Einzahlungen innerhalb eines Monats überbrücken zu können? | not_started |  |  |  |  |
| 6-KF-06 | - Wie viel Geld steuerst du selber bei (Geldeinlage)? | not_started |  |  |  |  |
| 6-KF-07 | - Woher kommen die zusätzlichen Mittel, um deinen Kapitalbedarf decken zu können? | not_started |  |  |  |  |
| 6-KF-08 | * Kapitalbedarfsplan als Tabelle (Aufstellung über die erforderlichen Anschaffungen für die Gründung) | not_started |  |  |  |  |
| 6-KF-09 | * Finanzierungsplan als Tabelle (Aufstellung über die vorgesehene Finanzierung ohne Gründungszuschuss) | not_started |  |  |  |  |
| 6-KF-10 | * Detaillierter Umsatzplan auf Monatsbasis mit Erläuterung als Tabelle für 3 Jahre (Rumpfjahr + 2 Jahre auf Monatsbasis) | not_started |  |  |  |  |
| 6-R-01 | - Wie stehen die Kosten im Verhältnis zu den Erlösen? | not_started |  |  |  |  |
| 6-R-02 | - Ab wann erzielst du einen Gewinn und wie entwickelt sich dieser? | not_started |  |  |  |  |
| 6-R-03 | * Rentabilitätsvorschau/Ertragsvorschau als Tabelle für 3 Jahre (Prognose der zu erwartenden Umsätze und der betrieblichen Kosten als Gegenüberstellung) | not_started |  |  |  |  |
| 6-L-01 | - Wie entwickelt sich die Liquidität deines Unternehmens? | not_started |  |  |  |  |
| 6-L-02 | - Hast du eine Liquiditätsreserve für unvorhergesehene Kosten und verzögerte Einzahlungen eingeplant? | not_started |  |  |  |  |
| 6-L-03 | * Monatlicher Liquiditätsplan mit detaillierter Kostenaufstellung als Tabelle für 3 Jahre (Rumpfjahr + 2 Jahre auf Monatsbasis) ohne Gründungszuschuss | not_started |  |  |  |  |
| A-01 | * Tabellarischer Lebenslauf | not_started |  |  |  |  |
