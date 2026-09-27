import pandas as pd


def calculate_metrics(monthly: pd.DataFrame) -> dict:
    """Calculate quantitative metrics from monthly pageview data."""

    if len(monthly) < 2:
        raise ValueError("At least two months of data are required.")

    views = monthly["views"].astype(float)

    # Compare short averaged windows instead of single edge months
    # to reduce the influence of random spikes.
    window = min(3, len(monthly))

    first_avg = views.head(window).mean()
    last_avg = views.tail(window).mean()

    if first_avg == 0:
        period_growth_pct = 0.0
    else:
        period_growth_pct = ((last_avg / first_avg) - 1) * 100

    monthly_change = views.pct_change().dropna()

    monthly_volatility_pct = monthly_change.std() * 100

    positive_months_pct = (
        (monthly_change > 0).mean() * 100
    )

    # IQR method for detecting unusual monthly spikes or drops.
    q1 = views.quantile(0.25)
    q3 = views.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_mask = (
        (views < lower_bound)
        | (views > upper_bound)
    )

    outlier_months_count = int(outlier_mask.sum())

    # Latest month compared with the same month one year earlier.
    year_over_year_growth_pct = None

    if len(monthly) >= 13:
        previous_year = views.iloc[-13]
        latest = views.iloc[-1]

        if previous_year != 0:
            year_over_year_growth_pct = (
                (latest / previous_year) - 1
            ) * 100

    return {
        "analysis_period_months": len(monthly),
        "avg_monthly_views": round(views.mean(), 2),
        "period_growth_pct": round(period_growth_pct, 2),
        "year_over_year_growth_pct": (
            round(year_over_year_growth_pct, 2)
            if year_over_year_growth_pct is not None
            else None
        ),
        "monthly_volatility_pct": round(
            monthly_volatility_pct,
            2,
        ),
        "positive_months_pct": round(
            positive_months_pct,
            2,
        ),
        "outlier_months_count": outlier_months_count,
    }