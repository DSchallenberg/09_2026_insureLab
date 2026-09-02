"""Kicktipp-optimaler Bundesliga-Tipp aus Wettquoten.

Deterministischer Rechenkern: keine Netzwerkzugriffe, nur Standardbibliothek.
Quoten rein, JSON raus.
"""

import argparse
import json
import math
import sys

POINTS_EXACT = 4
POINTS_DIFF = 3
POINTS_TENDENCY = 2
MAX_GOALS = 6
DEFAULT_TOTAL_GOALS = 2.5


def fair_probs_from_odds(odds):
    """Drei 1X2-Dezimalquoten -> faire Wahrscheinlichkeiten [p_a, p_remis, p_b].

    Entfernt die Buchmacher-Marge durch proportionale Normalisierung.
    """
    if len(odds) != 3:
        raise ValueError("Es werden genau drei Quoten benötigt: Sieg A, Remis, Sieg B.")
    if any(not math.isfinite(o) for o in odds):
        raise ValueError(f"Quoten müssen endliche Zahlen sein: {odds}.")
    if any(o <= 1.0 for o in odds):
        raise ValueError(f"Unplausible Quote <= 1.0 in {odds}.")
    implied = [1.0 / o for o in odds]
    total = sum(implied)
    if total < 1.0:
        raise ValueError(
            f"Implizite Wahrscheinlichkeitssumme {total:.3f} < 1.0 – Quoten unplausibel."
        )
    return [p / total for p in implied]


def validate_probs(probs):
    """Direkt übergebene Wahrscheinlichkeiten (z.B. Elo-Fallback) validieren und normalisieren."""
    if len(probs) != 3:
        raise ValueError("Es werden genau drei Wahrscheinlichkeiten benötigt: Sieg A, Remis, Sieg B.")
    if any(not math.isfinite(p) for p in probs):
        raise ValueError(f"Wahrscheinlichkeiten müssen endliche Zahlen sein: {probs}.")
    if any(p <= 0.0 or p >= 1.0 for p in probs):
        raise ValueError(f"Wahrscheinlichkeiten müssen in (0, 1) liegen: {probs}.")
    total = sum(probs)
    if not 0.99 <= total <= 1.01:
        raise ValueError(f"Wahrscheinlichkeitssumme {total:.3f} weicht zu stark von 1.0 ab.")
    return [p / total for p in probs]


def poisson_pmf(lam, k):
    """Poisson probability mass function: P(X = k) für Poisson(λ)."""
    return math.exp(-lam) * lam**k / math.factorial(k)


def score_matrix(lam_a, lam_b):
    """7x7-Ergebnismatrix; Restmasse > MAX_GOALS Tore wird auf MAX_GOALS gekappt."""
    p_a = [poisson_pmf(lam_a, k) for k in range(MAX_GOALS + 1)]
    p_b = [poisson_pmf(lam_b, k) for k in range(MAX_GOALS + 1)]
    p_a[MAX_GOALS] += 1.0 - sum(p_a)
    p_b[MAX_GOALS] += 1.0 - sum(p_b)
    return [[p_a[i] * p_b[j] for j in range(MAX_GOALS + 1)] for i in range(MAX_GOALS + 1)]


def outcome_probs(matrix):
    """(P(Sieg A), P(Remis), P(Sieg B)) einer Ergebnismatrix."""
    n = MAX_GOALS + 1
    p_a = sum(matrix[i][j] for i in range(n) for j in range(n) if i > j)
    p_d = sum(matrix[i][i] for i in range(n))
    p_b = sum(matrix[i][j] for i in range(n) for j in range(n) if i < j)
    return p_a, p_d, p_b


def rescale_to_1x2(matrix, fair):
    """Reskaliert die Regionen Sieg A / Remis / Sieg B auf die fairen 1X2-Wahrscheinlichkeiten."""
    current = outcome_probs(matrix)
    if any(c == 0.0 for c in current):
        raise ValueError("Ergebnismatrix hat eine Region mit Wahrscheinlichkeit 0 – Reskalierung nicht möglich.")
    factors = [fair[k] / current[k] for k in range(3)]

    def region(i, j):
        if i > j:
            return 0
        if i == j:
            return 1
        return 2

    n = MAX_GOALS + 1
    return [
        [matrix[i][j] * factors[region(i, j)] for j in range(n)]
        for i in range(n)
    ]


def total_goals_from_over25(over25_odd):
    """Erwartete Gesamttore aus der Over-2.5-Dezimalquote (Bisektion über Poisson-Gesamttore)."""
    if not math.isfinite(over25_odd) or over25_odd <= 1.0:
        raise ValueError(f"Unplausible Over-2.5-Quote <= 1.0: {over25_odd}.")
    p_over = min(max(1.0 / over25_odd, 0.02), 0.98)
    lo, hi = 0.1, 8.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        p = 1.0 - sum(poisson_pmf(mid, k) for k in range(3))
        if p < p_over:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def split_total_goals(total, fair):
    """Teilt die Gesamttore so auf (lam_a, lam_b) auf, dass die Poisson-Matrix
    die Differenz der fairen Siegwahrscheinlichkeiten trifft (Bisektion über d = lam_a - lam_b)."""
    target = fair[0] - fair[2]
    lo, hi = -total * 0.999, total * 0.999
    for _ in range(60):
        d = (lo + hi) / 2.0
        p_a, _, p_b = outcome_probs(score_matrix((total + d) / 2.0, (total - d) / 2.0))
        if p_a - p_b < target:
            lo = d
        else:
            hi = d
    d = (lo + hi) / 2.0
    return (total + d) / 2.0, (total - d) / 2.0


def expected_points_table(matrix):
    """Erwartete Kicktipp-Punkte für jeden möglichen Tipp, absteigend sortiert.

    Regeln: exakt = 4; richtige Tendenz + richtige Tordifferenz = 3 (nur bei
    Sieg-Tipps, bei Remis gibt es diese Stufe nicht); richtige Tendenz = 2.
    """
    n = MAX_GOALS + 1
    tips = []
    for tip_a in range(n):
        for tip_b in range(n):
            expected = 0.0
            for i in range(n):
                for j in range(n):
                    p = matrix[i][j]
                    if p == 0.0:
                        continue
                    if i == tip_a and j == tip_b:
                        expected += POINTS_EXACT * p
                    elif tip_a == tip_b and i == j:
                        expected += POINTS_TENDENCY * p
                    elif tip_a != tip_b and (i - j) == (tip_a - tip_b):
                        expected += POINTS_DIFF * p
                    elif tip_a != tip_b and i != j and (i > j) == (tip_a > tip_b):
                        expected += POINTS_TENDENCY * p
            tips.append(
                {
                    "tip": f"{tip_a}:{tip_b}",
                    "expected_points": round(expected, 4),
                    "probability": round(matrix[tip_a][tip_b], 4),
                }
            )
    tips.sort(key=lambda t: t["expected_points"], reverse=True)
    return tips


def analyze(fair, total_goals, assumptions):
    """Komplette Analyse: faire W'keiten + Gesamttore -> Empfehlung mit Punkterwartung."""
    lam_a, lam_b = split_total_goals(total_goals, fair)
    matrix = rescale_to_1x2(score_matrix(lam_a, lam_b), fair)
    tips = expected_points_table(matrix)
    n = MAX_GOALS + 1
    results = [
        {"result": f"{i}:{j}", "probability": round(matrix[i][j], 4)}
        for i in range(n)
        for j in range(n)
    ]
    results.sort(key=lambda r: r["probability"], reverse=True)
    return {
        "fair_probabilities": {
            "team_a_win": round(fair[0], 4),
            "draw": round(fair[1], 4),
            "team_b_win": round(fair[2], 4),
        },
        "expected_goals": {
            "team_a": round(lam_a, 2),
            "team_b": round(lam_b, 2),
            "total": round(total_goals, 2),
        },
        "top_results": results[:10],
        "tips_by_expected_points": tips,
        "recommendation": tips[0],
        "assumptions": assumptions,
    }


class _GermanArgumentParser(argparse.ArgumentParser):
    """Gibt Parser-Fehler im projektweiten Format 'Fehler: ...' mit Exit-Code 2 aus."""

    def error(self, message):
        print(f"Fehler: {message}", file=sys.stderr)
        raise SystemExit(2)


def build_parser():
    parser = _GermanArgumentParser(
        description="Kicktipp-optimaler Bundesliga-Tipp aus Wettquoten."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--odds",
        nargs=3,
        type=float,
        metavar=("SIEG_A", "REMIS", "SIEG_B"),
        help="1X2-Dezimalquoten für 90 Minuten",
    )
    source.add_argument(
        "--probs",
        nargs=3,
        type=float,
        metavar=("P_A", "P_REMIS", "P_B"),
        help="Faire Wahrscheinlichkeiten direkt (Fallback ohne Quoten, z.B. Elo-basiert)",
    )
    parser.add_argument(
        "--over25",
        type=float,
        default=None,
        help="Dezimalquote für Over 2.5 Tore (optional)",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    assumptions = []
    try:
        if args.odds:
            fair = fair_probs_from_odds(args.odds)
        else:
            fair = validate_probs(args.probs)
            assumptions.append(
                "Wahrscheinlichkeiten direkt übergeben (z.B. Elo-Fallback), keine Marktquoten."
            )
        if args.over25 is not None:
            total_goals = total_goals_from_over25(args.over25)
        else:
            total_goals = DEFAULT_TOTAL_GOALS
            assumptions.append(
                f"Keine Over/Under-Quote gefunden: Standardwert {DEFAULT_TOTAL_GOALS} erwartete Gesamttore."
            )
    except ValueError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 2
    result = analyze(fair, total_goals, assumptions)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
