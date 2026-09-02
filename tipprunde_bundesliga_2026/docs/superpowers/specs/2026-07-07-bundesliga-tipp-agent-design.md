# Design: Bundesliga-Tipp-Agent

**Status:** Fachlich auf die jeweils aktuelle Bundesliga-Saison ausgerichtet.

## Ziel

`/tipp <Heimteam> - <Auswärtsteam>` analysiert genau ein Bundesligaspiel und
empfiehlt ein Ergebnis nach 90 Minuten, das die erwarteten Punkte im
Kicktipp-Standardsystem maximiert: exakt 4, richtige Tordifferenz 3,
richtige Tendenz 2 Punkte.

## Fachliche Entscheidungen

| Thema | Entscheidung |
|---|---|
| Saison | Jeweils aktuelle Bundesliga-Saison |
| Reihenfolge | Team A = Heimteam, Team B = Auswärtsteam |
| Umfang | Genau ein Spiel pro Aufruf |
| Daten | Aktuelle Aufstellung, 90-Minuten-Quoten und belegter Spielkontext |
| Aufstellungsquellen | DFL, Vereine, Kicker, Sportschau, ESPN oder Flashscore |
| Quoten | Dezimale 1X2- und optional Over-2.5-Quote für 90 Minuten |
| Wertung | Kicktipp 4/3/2 |

## Architektur

```text
/tipp
 ├── Bundesliga-Kontext: Spieltag, Tabelle, Heim-/Auswärtsform, Ausfälle
 ├── /aufstellung: bestätigte oder voraussichtliche Startelf
 ├── /quoten: 90-Minuten-Marktquoten
 └── bundesliga-tipp-agent
       └── scripts/kicktipp_optimizer.py
```

Der aufrufende Agent recherchiert Daten und übergibt sie strukturiert an den
Subagent. Dieser besitzt keine Recherchewerkzeuge, erfindet keine Werte und
berechnet jede Empfehlung mit dem Python-Script.

## Rechenkern

Das Script entfernt die Buchmacher-Marge aus 1X2-Quoten, leitet aus der
Over-2.5-Quote erwartete Gesamttore ab und verteilt diese auf Heim- und
Auswärtsteam. Eine Poisson-Ergebnismatrix für 0:0 bis 6:6 wird auf die fairen
1X2-Wahrscheinlichkeiten reskaliert. Für jeden möglichen Tipp wird die
Punkterwartung berechnet; der Tipp mit dem höchsten Wert wird empfohlen.

Fehlt die Over/Under-Quote, setzt das Modell transparent 2,5 erwartete Tore
an. Ohne belastbare 1X2-Quoten wird keine Markt-basierte Empfehlung erfunden.

## Ausgabe

1. Empfehlung mit erwarteten Punkten
2. Sieg-/Remis-/Niederlagenwahrscheinlichkeiten und erwartete Tore
3. Top-5 der punktoptimalen Tipps und Top-5 wahrscheinlichsten Ergebnisse
4. Quellen, Abrufzeitpunkte, Aufstellungsstatus und Modellannahmen
5. Bundesliga-Kontext: Spieltag, Tabelle, Heim-/Auswärtsform, Belastung und
   Ausfälle

## Grenzen

- Der Tipp gilt ausschließlich für 90 Minuten inklusive Nachspielzeit.
- Mehrere Spiele, Tipp-Historie, automatische Tippabgabe und andere
  Punktesysteme sind nicht enthalten.
- Qualitative Abweichungen von der Modellempfehlung sind nur bei belegten,
  noch nicht im Markt abgebildeten Aufstellungsinformationen zulässig.
