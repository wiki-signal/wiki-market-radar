def compare_markets(results: list[dict]) -> list[dict]:
    """Rank analyzed markets using their calculated signals."""

    comparison = []

    for result in results:
        metrics = result["metrics"]
        assessment = result["assessment"]

        comparison.append(
            {
                "language": result["language"],
                "article": result["article"],
                "avg_monthly_views": metrics["avg_monthly_views"],
                "period_growth_pct": metrics["period_growth_pct"],
                "year_over_year_growth_pct": metrics[
                    "year_over_year_growth_pct"
                ],
                "monthly_volatility_pct": metrics[
                    "monthly_volatility_pct"
                ],
                "trend": assessment["trend"],
                "confidence": assessment["confidence"],
            }
        )

    return sorted(
        comparison,
        key=lambda item: item["period_growth_pct"],
        reverse=True,
    )