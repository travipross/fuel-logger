from fuel_logger import KM_PER_MILE

def compute_stats_from_fillup_df(df):
    if len(df) > 0:
        last_10 = df.sort_values('timestamp').tail(10)

        days_diff = (last_10.timestamp.max() - last_10.timestamp.min()).days
        odo_diff = last_10.odometer_km.max() - last_10.odometer_km.min()
        fuel_diff = last_10.fuel_amt_l.max() - last_10.fuel_amt_l.min()
        
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

        total_logs = len(df)

        stats = {
            'fuel_per_month': fuel_diff/days_diff*30 if days_diff > 0 else None,
            'dist_per_month': odo_diff/days_diff*30 if days_diff > 0 else None,
            'avg_lp100k': avg_lp100k,
            'avg_mpg': avg_mpg,
            'avg_mpg_imp': avg_mpg_imp,
            'best_lp100k': best_lp100k,
            'best_mpg': best_mpg,
            'best_mpg_imp': best_mpg_imp,
            'worst_lp100k': worst_lp100k,
            'worst_mpg': worst_mpg,
            'worst_mpg_imp': worst_mpg_imp,
            'total_fuel': total_fuel,
            'total_dist_km': total_dist_km,
            'total_dist_mi': total_dist_km/KM_PER_MILE,
            'current_odo': current_odo,
            'current_odo_mi': current_odo/KM_PER_MILE,
            'total_logs': total_logs
        }
    else:
        stats = None

    return stats