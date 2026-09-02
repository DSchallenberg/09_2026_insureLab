# Design: Bundesliga-Tipp-Agent

**Datum:** 2026-09-03  
**Status:** Vom Nutzer freigegeben

## Ziel

Der Agent analysiert jeweils ein Spiel der aktuellen deutschen
Bundesliga-Saison und gibt einen auf das Kicktipp-Standardsystem (4/3/2)
optimierten 90-Minuten-Tipp aus.

## Entscheidungen

| Thema | Entscheidung |
|---|---|
| Umfang | Vollständiger Bundesliga-Kontext |
| Saison | Jeweils aktuelle Bundesliga-Saison |
| Agent | `bundesliga-tipp-agent` |
| Einstieg | `/tipp` |
| Teamreihenfolge | Team A ist die Heimmannschaft, Team B die Auswärtsmannschaft |
| Aufstellung | DFL, offizielle Vereinsmeldungen, etablierte Sportmedien |
| Quoten | Aktuelle 90-Minuten-1X2- und Over/Under-2.5-Quoten |
| Berechnung | Deterministischer bestehender Optimizer |

## Architektur und Datenfluss

1. `/tipp` identifiziert Saison, Spieltag, Heimteam und Auswärtsteam.
2. `aufstellung` und `quoten` liefern aktuelle, mit Quelle und Zeitpunkt
   versehene Daten.
3. Der aufrufende Agent ergänzt Tabellenlage, Form, Heim-/Auswärtsbilanz,
   Ausfälle und Belastung.
4. `bundesliga-tipp-agent` führt `scripts/kicktipp_optimizer.py` aus und
   formatiert das Ergebnis.

## Fehlerbehandlung und Grenzen

- Ohne belastbare Quoten oder Aufstellungen werden keine Daten erfunden.
- Der Tipp gilt für 90 Minuten inklusive Nachspielzeit.
- Mehrere Spiele pro Aufruf, Tipp-Historie und automatische Tippabgabe sind
  nicht Teil des Umfangs.

## Qualitätssicherung

- pytest sichert Optimizer, CLI-Benennung und die aktiven Kontextdateien.
- Eine Projektprüfung sucht nach überholten Wettbewerbs- und Quellenbezügen.
