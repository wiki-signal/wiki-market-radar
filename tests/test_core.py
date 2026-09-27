import pandas as pd

from wiki_market_radar.analytics import calculate_metrics
from wiki_market_radar.comparison import compare_markets
from wiki_market_radar.confidence import assess_trend
from wiki_market_radar.data_processing import (
    aggregate_monthly,
    prepare_pageviews,
)


def test_prepare_and_aggregate_pageviews():
    items = [
        {
            "timestamp": "2025010100",
            "views": 10,
        },
        {
            "timestamp": "2025010200",
            "views": 20,
        },
        {
            "timestamp": "2025020100",
            "views": 30,
        },
    ]

    daily = prepare_pageviews(items)
    monthly = aggregate_monthly(daily)

    assert len(daily) == 3
    assert len(monthly) == 2
    assert monthly.iloc[0]["views"] == 30
    assert monthly.iloc[1]["views"] == 30


def test_calculate_metrics():
    monthly = pd.DataFrame(
        {
            "date": pd.date_range(
                "2025-01-01",
                periods=6,
                freq="MS",
            ),
            "views": [
                100,
                100,
                100,
                200,
                200,
                200,
            ],
        }
    )

    metrics = calculate_metrics(monthly)

    assert metrics["analysis_period_months"] == 6
    assert metrics["avg_monthly_views"] == 150.0
    assert metrics["period_growth_pct"] == 100.0
    assert metrics["outlier_months_count"] == 0


def test_assess_trend():
    metrics = {
        "analysis_period_months": 24,
        "avg_monthly_views": 1000,
        "period_growth_pct": 25.0,
        "year_over_year_growth_pct": 20.0,
        "monthly_volatility_pct": 15.0,
        "positive_months_pct": 70.0,
        "outlier_months_count": 1,
    }

    assessment = assess_trend(metrics)

    assert assessment["trend"] == "Growing"
    assert assessment["confidence"] == "High"


def test_compare_markets():
    results = [
        {
            "language": "Market A",
            "article": "Topic A",
            "metrics": {
                "avg_monthly_views": 1000,
                "period_growth_pct": 20.0,
                "year_over_year_growth_pct": 10.0,
                "monthly_volatility_pct": 15.0,
            },
            "assessment": {
                "trend": "Growing",
                "confidence": "High",
            },
        },
        {
            "language": "Market B",
            "article": "Topic B",
            "metrics": {
                "avg_monthly_views": 2000,
                "period_growth_pct": -10.0,
                "year_over_year_growth_pct": -5.0,
                "monthly_volatility_pct": 20.0,
            },
            "assessment": {
                "trend": "Stable",
                "confidence": "Medium",
            },
        },
    ]

    comparison = compare_markets(results)

    assert comparison[0]["language"] == "Market A"
    assert comparison[1]["language"] == "Market B"