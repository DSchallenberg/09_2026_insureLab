# Bundesliga-Tipp-Agent: Umsetzungsübersicht

## Ziel

Der Tipp-Agent verarbeitet ein Spiel der jeweils aktuellen Bundesliga-Saison
mit Heimteam, Auswärtsteam, Spieltag und Tabellenkontext. Er liefert einen
Kicktipp-optimierten 90-Minuten-Tipp.

## Bausteine

- `aufstellung`: Ermittelt die offizielle oder voraussichtliche Startelf über
  DFL, Vereinsquellen und etablierte Sportmedien.
- `quoten`: Liefert aktuelle Dezimalquoten für den 90-Minuten-1X2-Markt sowie,
  wenn vorhanden, Over/Under 2.5.
- `tipp`: Recherchiert den Bundesligakontext und delegiert alle strukturierten
  Eingaben an `bundesliga-tipp-agent`.
- `bundesliga-tipp-agent`: Führt den Optimizer aus und formatiert die
  Empfehlung; er recherchiert nicht selbst.
- `kicktipp_optimizer.py`: Rechnet fairen Markt, Ergebnismatrix und erwartete
  Kicktipp-Punkte deterministisch.

## Ablauf

1. Heim- und Auswärtsteam, Saison, Spieltag und Anstoßzeit eindeutig bestimmen.
2. Tabelle, Form, Heim-/Auswärtsbilanz, Belastung, Ausfälle und Aufstellung
   mit Quellen und Zeitpunkten erfassen.
3. Ausschließlich 90-Minuten-1X2-Quoten abrufen; keine Märkte für
   Weiterkommen oder Sonderwetten verwenden.
4. Den Optimizer mit 1X2- und optional Over-2.5-Quote aufrufen.
5. Empfehlung, Modellwerte und nachvollziehbare Faktenlage ausgeben.

## Verifikation

- `python3 -m pytest tests/ -v` muss vollständig bestehen.
- Der CLI-Aufruf mit `--odds` und optional `--over25` muss valides JSON
  ausgeben.
- Alle aktiven Anweisungen müssen Bundesliga, Heim-/Auswärtsrollen und
  DFL-/Vereinsquellen nennen.
