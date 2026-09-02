---
name: aufstellung
description: Fetch the official or probable lineup for one match in the current Bundesliga season via web search.
---

# Bundesliga-Aufstellungs-Abfrage

Hole die offizielle oder voraussichtliche Startaufstellung für genau EIN Spiel
der jeweils aktuellen Bundesliga-Saison. Team A ist die Heimmannschaft, Team B
die Auswärtsmannschaft.

## Ablauf

### 1. Spiel identifizieren
- Bestimme Heimteam, Auswärtsteam, Saison, Spieltag und Anstoßzeit.
- Bei mehrdeutigen Teams oder mehreren möglichen Paarungen frage nach, statt
  die Begegnung zu erraten.

### 2. Timing prüfen
Offizielle Aufstellungen erscheinen gewöhnlich etwa 60 bis 75 Minuten vor
Anpfiff.
- **Vor diesem Zeitfenster:** Liefere eine Presseprognose nur als
  **voraussichtlich** und nenne die erwartete Veröffentlichungszeit.
- **Im Zeitfenster, während oder nach dem Spiel:** Suche die offizielle
  Startelf.

### 3. Daten beschaffen
Priorisiere Quellen in dieser Reihenfolge:
1. DFL bzw. offizielles Spielzentrum,
2. offizielle Kanäle der beteiligten Vereine,
3. etablierte Sportmedien wie Kicker, Sportschau, ESPN oder Flashscore.

**Vor der offiziellen Veröffentlichung (voraussichtliche Aufstellung):** Rufe
per WebFetch direkt die vereinsspezifische LigaInsider-Seite ab, z. B.
`https://ligainsider.de/<vereinsslug>/<id>/` (Slug/ID vorher per WebSearch
ermitteln, z. B. `"<Team>" ligainsider voraussichtliche Aufstellung`). Diese
Seiten liefern zuverlässig eine aktuelle Spielerliste inklusive markierter
Ausfälle/Rückkehrer und Stand-Zeitstempel — meist in einem einzigen Abruf pro
Team, ohne weitere Suchrunden. Rufe beide Vereinsseiten (Heim- und
Auswärtsteam) einzeln ab.

Nur falls LigaInsider das Spiel nicht führt, suche allgemein nach:

```text
"<Heimteam>" "<Auswärtsteam>" Bundesliga Aufstellung Startelf
```

Gib eine Quelle nur als offiziell an, wenn sie die Startelf bestätigt.

### 4. Ausgabeformat
```json
{
  "match": "<Heimteam> - <Auswärtsteam>",
  "season": "<aktuelle Saison>",
  "matchday": "<Spieltag>",
  "team_a": {
    "role": "home",
    "formation": "4-2-3-1",
    "players": ["Spieler1", "Spieler2"],
    "status": "offiziell|voraussichtlich"
  },
  "team_b": {
    "role": "away",
    "formation": "3-5-2",
    "players": ["Spieler1", "Spieler2"],
    "status": "offiziell|voraussichtlich"
  },
  "notable_changes": ["Rotation", "Ausfall eines Stammspielers"],
  "source": "<Quelle>",
  "timestamp": "<ISO-8601-Zeitpunkt>"
}
```

## Grenzen
- Genau ein Spiel pro Aufruf.
- Vor der offiziellen Veröffentlichung bleiben Prognosen klar als
  **voraussichtlich** markiert.
