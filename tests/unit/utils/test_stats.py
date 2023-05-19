from fuel_logger.utils.stats import compute_stats_from_fillup_df
from pytest import approx


def test_compute_stats_from_fillup_df(corolla_df):
    assert len(corolla_df) == 12
    assert {
        "timestamp",
        "odometer_km",
        "fuel_amt_l",
        "lp100k",
        "mpg",
        "mpg_imp",
        "dist_km",
        "odometer_km",
    }.issubset(corolla_df.keys())

    output_stats = compute_stats_from_fillup_df(corolla_df)

    assert output_stats is not None

    assert output_stats.get("fuel_per_month") == approx(19.3, 0.1)
    assert output_stats.get("dist_per_month") == approx(203.3, 0.1)
    assert output_stats.get("avg_lp100k") == approx(9.35, 0.1)
    assert output_stats.get("avg_mpg") == approx(26.12, 0.1)
    assert output_stats.get("avg_mpg_imp") == approx(31.35, 0.1)
    assert output_stats.get("best_lp100k") == approx(6.56, 0.1)
    assert output_stats.get("best_mpg") == approx(35.8, 0.1)
    assert output_stats.get("best_mpg_imp") == approx(42.99, 0.1)
    assert output_stats.get("worst_lp100k") == approx(12.25, 0.1)
    assert output_stats.get("worst_mpg") == approx(19.2, 0.1)
    assert output_stats.get("worst_mpg_imp") == approx(23.04, 0.1)
    assert output_stats.get("total_fuel") == approx(402.0, 0.1)
    assert output_stats.get("total_dist_km") == approx(4539, 0.1)
    assert output_stats.get("total_dist_mi") == approx(2821, 0.1)
    assert output_stats.get("current_odo") == approx(262684, 0.1)
    assert output_stats.get("current_odo_mi") == approx(163259.2, 0.1)
    assert output_stats.get("total_logs") == 12
