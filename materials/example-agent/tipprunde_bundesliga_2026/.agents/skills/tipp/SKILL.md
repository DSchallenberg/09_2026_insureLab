---
name: tipp
description: Use for a prediction or Kicktipp recommendation for one match in the current Bundesliga season. Researches lineup and odds data, then delegates the 90-minute recommendation to bundesliga-tipp-agent.
---

# Bundesliga-Tipp

Analysiere genau EIN Spiel der jeweils aktuellen Bundesliga-Saison und gib
einen auf das Kicktipp-Standardsystem optimierten 90-Minuten-Tipp aus.
Team A ist die Heimmannschaft, Team B die Auswärtsmannschaft.

## Ablauf

### 1. Begegnung einordnen
- Bestimme Heimteam, Auswärtsteam, Saison, Spieltag und Anstoßzeit.
- Bei mehrdeutigen Teams oder Paarungen stelle eine kurze Rückfrage.
- Bei mehreren Spielen im Auftrag weise auf die Begrenzung hin und analysiere
  nur das zuerst eindeutig genannte Spiel.

### 2. Daten parallel beschaffen (Skill-Delegation)
Rufe diese beiden Skills **gleichzeitig** auf:
- `aufstellung <Heimteam> - <Auswärtsteam>, <Datum>, <Spieltag>`
- `quoten <Heimteam> - <Auswärtsteam>, <Datum>, <Spieltag>`

Beide Skills liefern strukturierte JSON-Responses mit Spielerinformationen und 
Wettquoten für die weitere Verarbeitung.

### 3. Bundesliga-Kontext recherchieren
Beschaffe belegte Informationen zu:
- Tabellenposition und Wettbewerbskontext (Meisterschaft, Europapokal,
  Klassenerhalt),
- aktueller Form sowie Heimform des Heimteams und Auswärtsform des Auswärtsteams,
- Verletzungen, Sperren, Rotation und Belastung durch englische Wochen,
- Historie zwischen den Teams (direkte Duelle).

Nenne Quellen und Abrufzeitpunkte. Erfinde keine Informationen.

### 4. An den Subagent delegieren
Übergebe `bundesliga-tipp-agent` ein vollständiges, strukturiertes Prompt mit:

```text
<Heimteam> - <Auswärtsteam>
Saison: <aktuelle Saison>
Spieltag: <Spieltag>
Bundesliga-Kontext: <Tabelle, Form, Heim-/Auswärtsform, Belastung, Ausfälle>

Aufstellung:
<JSON aus aufstellung-Skill>

Quoten:
<JSON aus quoten-Skill>
```

Der Subagent berechnet die Empfehlung ausschließlich mit
`scripts/kicktipp_optimizer.py` und liefert die formatierte Analyse zurück.

#### Delegationsprotokoll

- Die beiden Recherche-Skills werden vor dieser Delegation vollständig
  abgeschlossen. Starte keine zusätzlichen Recherche-Subagents mit demselben
  Auftrag.
- Delegiere genau **einen** Aufruf an `bundesliga-tipp-agent`; übergib die
  gesammelten JSON-Daten direkt im Prompt.
- Der Subagent recherchiert nicht, wartet nicht auf weitere Agenten und führt
  genau einen lokalen Optimizer-Aufruf aus. Fordere eine kompakte Antwort an.
- Kommt die Antwort nicht zurück, führe den Optimizer im aufrufenden Agenten
  mit denselben 1X2-Daten aus und kennzeichne nur die Agentenantwort als
  unavailable. Gib nicht fälschlich an, die Datenanalyse sei fehlgeschlagen.

## Grenzen
- Die Empfehlung gilt nur für 90 Minuten inklusive Nachspielzeit.
- Keine Verlängerung, kein Elfmeterschießen, keine automatische Tippabgabe.
- Ohne belastbare 1X2-Quoten weist die Ausgabe auf die fehlende Datenbasis hin.
