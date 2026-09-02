---
name: quoten
description: Fetch current 90-minute 1X2 and Over/Under 2.5 betting odds for one match in the current Bundesliga season via web search.
---

# Bundesliga-Wettquoten-Abfrage

Hole aktuelle Dezimalquoten für genau EIN Spiel der jeweils aktuellen
Bundesliga-Saison. Team A ist die Heimmannschaft, Team B die Auswärtsmannschaft.

## Ablauf

### 1. Spiel identifizieren
- Bestimme Heimteam, Auswärtsteam, Saison, Spieltag und Anstoßzeit.
- Bei mehrdeutigen Paarungen frage nach, statt zu raten.

### 2. Daten beschaffen
**Primärquelle (zuerst versuchen):** Rufe per WebFetch direkt
`https://www.wettfreunde.net/bundesliga-quoten/` ab. Diese Seite liefert für
den aktuellen Spieltag eine strukturierte Vergleichstabelle mehrerer
Buchmacher (u. a. Betano, Winamax, Interwetten, bet365, Oddset, LeoVegas) mit
sauber zugeordneten 1-X-2-Spalten und Zeitstempel — das ist in der Praxis die
zuverlässigste Einzelquelle und macht in den meisten Fällen weitere Suchen
überflüssig. Bilde den Durchschnitt über die gelisteten Buchmacher als
`odds_1x2`-Wert, sofern keine einzelne Quote ausdrücklich verlangt ist.

**Nicht direkt per WebFetch ansteuern:** Einzelne Buchmacher-Landingpages
(tipico.de, bet365.de, bwin.de) sowie oddschecker.com, oddspedia.com und
forebet.com liefern beim direkten Abruf regelmäßig HTTP 403. Flashscore-
Quotenseiten liefern beim Abruf oft nur eine leere clientseitig gerenderte
Seite ohne Werte. Vermeide außerdem KI-generierte Wett-Tipp-Artikel
(z. B. sportwetten24.com, wette.de) als alleinige Quelle: Sie nennen Quoten
oft nur im Fließtext ohne eindeutige 1-X-2-Zuordnung oder beziehen sich auf
ein anderes Datum derselben Paarung.

**Falls die Primärquelle das gesuchte Spiel nicht listet:** Nutze WebSearch,
zum Beispiel:

```text
"<Heimteam>" "<Auswärtsteam>" Bundesliga Wettquoten 1X2 Dezimalquoten
```

und bevorzuge dabei weitere Quotenvergleichsportale (z. B. Oddspedia via
WebSearch-Snippet statt direktem WebFetch) gegenüber einzelnen
Buchmacherseiten.

Ermittle:
- **Pflicht:** 1X2-Dezimalquoten für die reguläre Spielzeit: Sieg Heim,
  Remis, Sieg Auswärts;
- **Optional:** Over-2.5- und Under-2.5-Dezimalquote.

Achte ausdrücklich darauf, dass die Quoten für 90 Minuten inklusive
Nachspielzeit gelten. Märkte für Weiterkommen, Sonderwetten oder Ergebnisse
inklusive Verlängerung beziehungsweise Elfmeterschießen dürfen nicht verwendet
werden.

### 3. Ausgabeformat
```json
{
  "match": "<Heimteam> - <Auswärtsteam>",
  "season": "<aktuelle Saison>",
  "matchday": "<Spieltag>",
  "odds_1x2": {
    "win_a": 2.10,
    "draw": 3.40,
    "win_b": 3.50
  },
  "odds_ou25": {
    "over": 1.92,
    "under": 1.87
  },
  "market": "90 Minuten inklusive Nachspielzeit",
  "source": "<Quelle>",
  "timestamp": "<ISO-8601-Zeitpunkt>"
}
```

## Grenzen
- Genau ein Spiel pro Aufruf.
- Fehlen belastbare 90-Minuten-Quoten, melde dies klar statt Ersatzwerte zu
  erfinden.
