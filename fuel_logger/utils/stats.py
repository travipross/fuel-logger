from fuel_logger import KM_PER_MILE


def compute_stats_from_fillup_df(df):
    total_logs = len(df)
    if total_logs > 1:
        last_10 = df.sort_values("timestamp").tail(10)

        days_diff = (last_10.timestamp.max() - last_10.timestamp.min()).days
        odo_diff = last_10.iloc[-1].odometer_km - last_10.iloc[1].odometer_km
        fuel_diff = last_10[1:].fuel_amt_l.sum()

        avg_lp100k = last_10.lp100k.mean()
        avg_mpg = last_10.mpg.mean()
        avg_mpg_imp = last_10.mpg_imp.mean()

        best_lp100k = df.lp100k.min()
        best_mpg = df.mpg.max()
        best_mpg_imp = df.mpg_imp.max()

        worst_lp100k = df.lp100k.max()
        worst_mpg = df.mpg.min()
        worst_mpg_imp = df.mpg_imp.min()

        total_fuel = df.fuel_amt_l.sum()
        total_dist_km = df.dist_km.sum()
        current_odo = df.odometer_km.max()

        fuel_per_month = (fuel_diff / days_diff * 30) if days_diff > 0 else None
        dist_per_month = (odo_diff / days_diff * 30) if days_diff > 0 else None

        stats = {
            "fuel_per_month": float(fuel_per_month) if fuel_per_month else None,
            "dist_per_month": float(dist_per_month) if dist_per_month else None,
            "avg_lp100k": float(avg_lp100k),
            "avg_mpg": float(avg_mpg),
            "avg_mpg_imp": float(avg_mpg_imp),
            "best_lp100k": float(best_lp100k),
            "best_mpg": float(best_mpg),
            "best_mpg_imp": float(best_mpg_imp),
            "worst_lp100k": float(worst_lp100k),
            "worst_mpg": float(worst_mpg),
            "worst_mpg_imp": float(worst_mpg_imp),
            "total_fuel": float(total_fuel),
            "total_dist_km": float(total_dist_km),
            "total_dist_mi": float(total_dist_km / KM_PER_MILE),
            "current_odo": float(current_odo),
            "current_odo_mi": float(current_odo / KM_PER_MILE),
            "total_logs": int(total_logs),
        }
    else:
        stats = None

    return stats
