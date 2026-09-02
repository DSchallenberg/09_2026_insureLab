# End-to-End-Probelauf: Bundesliga-Tipp

## Zweck

Dieses Dokument beschreibt den erwarteten Ablauf für ein einzelnes Spiel der
jeweils aktuellen Bundesliga-Saison. Es enthält bewusst keine als aktuell
dargestellten Quoten, Tabellenstände oder Aufstellungen; diese müssen beim
realen Aufruf recherchiert und mit Quelle sowie Abrufzeitpunkt belegt werden.

## Beispielablauf

**Eingabe:** `/tipp <Heimteam> - <Auswärtsteam>`

1. Der aufrufende Agent bestimmt Saison, Spieltag, Anstoßzeit und
   Heim-/Auswärtsrolle.
2. `aufstellung` liefert den Status der Startelf aus DFL-, Vereins- oder
   seriösen Medienquellen. Liegt die offizielle Startelf noch nicht vor, ist
   die Antwort eindeutig als **voraussichtlich** markiert.
3. `quoten` liefert dezimale 1X2-Quoten und, falls verfügbar, die
   Over-2.5-Quote für 90 Minuten inklusive Nachspielzeit.
4. Der Agent ergänzt Tabellenposition, Heim- und Auswärtsform, Ausfälle und
   Belastung mit belegten Quellen.
5. Der Subagent erhält alle Angaben und führt zum Beispiel aus:

```bash
python3 scripts/kicktipp_optimizer.py --odds 2.10 3.40 3.60 --over25 1.85
```

6. Die Ausgabe enthält die punktoptimale Empfehlung, Wahrscheinlichkeiten,
   erwartete Tore, die Top-5 der Tipps, die Top-5 der Einzelergebnisse und
   die vollständige Faktenlage.

## Abnahmekriterien

- Team A wird durchgehend als Heimteam und Team B als Auswärtsteam behandelt.
- Ausschließlich 90-Minuten-Quoten gelangen in das Script.
- Das Script liefert valides JSON; alle dargestellten Modellwerte stammen
  daraus.
- Fehlende Daten werden offen benannt und nicht ergänzt.
- Eine Abweichung von der Modellempfehlung ist sichtbar markiert und mit einer
  belegten Aufstellungsinformation begründet.
