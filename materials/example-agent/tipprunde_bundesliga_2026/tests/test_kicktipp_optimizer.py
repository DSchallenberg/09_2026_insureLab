import math

import pytest

from scripts.kicktipp_optimizer import fair_probs_from_odds, validate_probs, poisson_pmf, score_matrix, outcome_probs, rescale_to_1x2, total_goals_from_over25, split_total_goals, MAX_GOALS, expected_points_table, analyze


class TestFairProbsFromOdds:
    def test_no_margin(self):
        # Quoten ohne Marge: implizite W'keiten sind bereits fair
        assert fair_probs_from_odds([2.0, 4.0, 4.0]) == pytest.approx([0.5, 0.25, 0.25])

    def test_margin_removed_proportionally(self):
        # implizit: 0.5556/0.2778/0.2778, Summe 1.1111 -> proportional normalisiert
        fair = fair_probs_from_odds([1.8, 3.6, 3.6])
        assert sum(fair) == pytest.approx(1.0)
        assert fair == pytest.approx([0.5, 0.25, 0.25])

    def test_odd_below_one_rejected(self):
        with pytest.raises(ValueError):
            fair_probs_from_odds([0.9, 3.4, 3.6])

    def test_implied_sum_below_one_rejected(self):
        # implizit: 0.333+0.25+0.2 = 0.783 < 1.0 -> unplausibel
        with pytest.raises(ValueError):
            fair_probs_from_odds([3.0, 4.0, 5.0])

    def test_nan_odd_rejected(self):
        with pytest.raises(ValueError):
            fair_probs_from_odds([float("nan"), 3.4, 3.6])


class TestValidateProbs:
    def test_valid_probs_pass_through(self):
        assert validate_probs([0.5, 0.25, 0.25]) == pytest.approx([0.5, 0.25, 0.25])

    def test_slight_deviation_normalized(self):
        result = validate_probs([0.5, 0.253, 0.25])
        assert sum(result) == pytest.approx(1.0)

    def test_bad_sum_rejected(self):
        with pytest.raises(ValueError):
            validate_probs([0.5, 0.2, 0.2])

    def test_out_of_range_rejected(self):
        with pytest.raises(ValueError):
            validate_probs([1.2, -0.1, -0.1])

    def test_nan_prob_rejected(self):
        with pytest.raises(ValueError):
            validate_probs([float("nan"), 0.5, 0.5])


class TestScoreMatrix:
    def test_poisson_pmf_known_values(self):
        assert poisson_pmf(1.0, 0) == pytest.approx(math.exp(-1.0))
        assert poisson_pmf(2.0, 2) == pytest.approx(math.exp(-2.0) * 2.0)

    def test_matrix_sums_to_one(self):
        m = score_matrix(1.4, 1.0)
        assert sum(sum(row) for row in m) == pytest.approx(1.0)

    def test_matrix_sums_to_one_with_heavy_tail(self):
        # hohe Lambdas: viel Restmasse > 6 Tore, muss auf 6 gekappt sein
        m = score_matrix(5.0, 5.0)
        assert sum(sum(row) for row in m) == pytest.approx(1.0)

    def test_outcome_probs_symmetric(self):
        p_a, p_d, p_b = outcome_probs(score_matrix(1.2, 1.2))
        assert p_a == pytest.approx(p_b)
        assert p_a + p_d + p_b == pytest.approx(1.0)

    def test_stronger_team_wins_more_often(self):
        p_a, _, p_b = outcome_probs(score_matrix(2.0, 0.8))
        assert p_a > p_b


class TestRescaleTo1x2:
    def test_matches_target_probs_exactly(self):
        fair = [0.5, 0.3, 0.2]
        m = rescale_to_1x2(score_matrix(1.4, 1.0), fair)
        assert outcome_probs(m) == pytest.approx(tuple(fair))

    def test_total_mass_stays_one(self):
        m = rescale_to_1x2(score_matrix(1.4, 1.0), [0.45, 0.28, 0.27])
        assert sum(sum(row) for row in m) == pytest.approx(1.0)

    def test_corrects_draw_underestimation(self):
        # reines Poisson unterschätzt Remis; nach Reskalierung stimmt die Remis-Masse
        raw = score_matrix(1.3, 1.1)
        _, p_d_raw, _ = outcome_probs(raw)
        target_draw = p_d_raw + 0.05
        rescaled = rescale_to_1x2(raw, [0.45 - 0.025, target_draw, 0.55 - p_d_raw - 0.025])
        _, p_d_new, _ = outcome_probs(rescaled)
        assert p_d_new == pytest.approx(target_draw)

    def test_zero_mass_region_rejected(self):
        n = 7
        m = [[0.0] * n for _ in range(n)]
        m[1][0] = 1.0  # nur Sieg-A-Masse, Remis- und Sieg-B-Region leer
        with pytest.raises(ValueError):
            rescale_to_1x2(m, [0.5, 0.3, 0.2])


class TestExpectedGoals:
    def test_over25_roundtrip(self):
        # aus lam die faire Over-Quote bauen und lam zurückgewinnen
        lam = 2.4
        p_over = 1.0 - sum(poisson_pmf(lam, k) for k in range(3))
        assert total_goals_from_over25(1.0 / p_over) == pytest.approx(lam, abs=1e-3)

    def test_lower_over_odd_means_more_goals(self):
        # niedrigere Over-Quote = torreicheres Spiel erwartet
        assert total_goals_from_over25(1.5) > total_goals_from_over25(2.5)

    def test_invalid_over_odd_rejected(self):
        with pytest.raises(ValueError):
            total_goals_from_over25(0.99)

    def test_nan_over_odd_rejected(self):
        with pytest.raises(ValueError):
            total_goals_from_over25(float("nan"))

    def test_split_symmetric_teams(self):
        lam_a, lam_b = split_total_goals(2.5, [0.35, 0.30, 0.35])
        assert lam_a == pytest.approx(lam_b, abs=1e-3)
        assert lam_a + lam_b == pytest.approx(2.5)

    def test_split_favors_stronger_team(self):
        lam_a, lam_b = split_total_goals(2.5, [0.60, 0.25, 0.15])
        assert lam_a > lam_b
        assert lam_a + lam_b == pytest.approx(2.5)

    def test_split_matches_win_prob_difference(self):
        fair = [0.55, 0.25, 0.20]
        lam_a, lam_b = split_total_goals(2.6, fair)
        p_a, _, p_b = outcome_probs(score_matrix(lam_a, lam_b))
        assert p_a - p_b == pytest.approx(fair[0] - fair[2], abs=1e-3)


def unit_matrix(i, j):
    """Matrix, in der genau ein Ergebnis Wahrscheinlichkeit 1.0 hat."""
    n = MAX_GOALS + 1
    m = [[0.0] * n for _ in range(n)]
    m[i][j] = 1.0
    return m


class TestExpectedPoints:
    def test_scoring_tiers_against_certain_result(self):
        # tatsächliches Ergebnis sicher 1:0 -> Punkte je Tippkategorie prüfen
        pts = {t["tip"]: t["expected_points"] for t in expected_points_table(unit_matrix(1, 0))}
        assert pts["1:0"] == pytest.approx(4.0)  # exakt
        assert pts["2:1"] == pytest.approx(3.0)  # richtige Differenz
        assert pts["2:0"] == pytest.approx(2.0)  # nur Tendenz
        assert pts["0:0"] == pytest.approx(0.0)  # falsch (Remis)
        assert pts["0:1"] == pytest.approx(0.0)  # falsch (Tendenz B)

    def test_draw_tips_have_no_diff_tier(self):
        # Kicktipp-Regel: anderes Remis bringt nur Tendenzpunkte (2), nie 3
        n = MAX_GOALS + 1
        m = [[0.0] * n for _ in range(n)]
        m[0][0] = 0.5
        m[1][1] = 0.5
        pts = {t["tip"]: t["expected_points"] for t in expected_points_table(m)}
        assert pts["0:0"] == pytest.approx(4 * 0.5 + 2 * 0.5)
        assert pts["1:1"] == pytest.approx(4 * 0.5 + 2 * 0.5)

    def test_table_sorted_descending(self):
        table = expected_points_table(score_matrix(1.5, 1.0))
        values = [t["expected_points"] for t in table]
        assert values == sorted(values, reverse=True)


class TestAnalyze:
    def test_result_shape(self):
        fair = fair_probs_from_odds([2.10, 3.40, 3.60])
        result = analyze(fair, 2.5, ["Testannahme"])
        assert set(result) == {
            "fair_probabilities",
            "expected_goals",
            "top_results",
            "tips_by_expected_points",
            "recommendation",
            "assumptions",
        }
        assert len(result["top_results"]) == 10
        assert len(result["tips_by_expected_points"]) == (MAX_GOALS + 1) ** 2
        assert result["recommendation"] == result["tips_by_expected_points"][0]
        assert result["assumptions"] == ["Testannahme"]

    def test_clear_favorite_gets_win_tip(self):
        fair = fair_probs_from_odds([1.50, 4.20, 6.50])
        result = analyze(fair, 2.6, [])
        goals_a, goals_b = map(int, result["recommendation"]["tip"].split(":"))
        assert goals_a > goals_b


import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "kicktipp_optimizer.py"), *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


def test_help_describes_bundesliga_context():
    proc = run_cli("--help")

    assert proc.returncode == 0
    assert "Bundesliga" in proc.stdout
    assert "WM 2026" not in proc.stdout


class TestCli:
    def test_odds_with_over25(self):
        proc = run_cli("--odds", "2.10", "3.40", "3.60", "--over25", "1.85")
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert set(data) == {
            "fair_probabilities",
            "expected_goals",
            "top_results",
            "tips_by_expected_points",
            "recommendation",
            "assumptions",
        }
        assert data["assumptions"] == []

    def test_missing_over25_adds_assumption(self):
        proc = run_cli("--odds", "2.10", "3.40", "3.60")
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert data["expected_goals"]["total"] == pytest.approx(2.5)
        assert any("Standardwert" in a for a in data["assumptions"])

    def test_probs_fallback_adds_assumption(self):
        proc = run_cli("--probs", "0.5", "0.3", "0.2")
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert any("Elo" in a or "direkt" in a for a in data["assumptions"])

    def test_invalid_odds_exit_code_2(self):
        proc = run_cli("--odds", "0.9", "3.4", "3.6")
        assert proc.returncode == 2
        assert proc.stderr.startswith("Fehler:")

    def test_odds_and_probs_mutually_exclusive(self):
        proc = run_cli("--odds", "2.1", "3.4", "3.6", "--probs", "0.5", "0.3", "0.2")
        assert proc.returncode == 2
        assert proc.stderr.startswith("Fehler:")

    def test_nan_odds_exit_code_2(self):
        proc = run_cli("--odds", "nan", "3.4", "3.6")
        assert proc.returncode == 2
        assert proc.stderr.startswith("Fehler:")
