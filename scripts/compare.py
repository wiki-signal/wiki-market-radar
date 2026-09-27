import argparse

from wiki_market_radar.analytics import calculate_metrics
from wiki_market_radar.comparison import compare_markets
from wiki_market_radar.confidence import assess_trend
from wiki_market_radar.data_processing import (
    aggregate_monthly,
    prepare_pageviews,
)
from wiki_market_radar.wikimedia_client import fetch_pageviews


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare Wikipedia interest across multiple markets."
    )

    parser.add_argument(
        "--market",
        action="append",
        required=True,
        help=(
            "Market definition in the format "
            "'Language|project|article'. "
            "Use --market multiple times."
        ),
    )

    parser.add_argument(
        "--start",
        required=True,
        help="Start date in YYYYMMDDHH format",
    )

    parser.add_argument(
        "--end",
        required=True,
        help="End date in YYYYMMDDHH format",
    )

    return parser.parse_args()


def analyze_market(
    language: str,
    project: str,
    article: str,
    start: str,
    end: str,
) -> dict:
    pageviews = fetch_pageviews(
        project=project,
        article=article,
        start=start,
        end=end,
    )

    daily = prepare_pageviews(pageviews)
    monthly = aggregate_monthly(daily)

    metrics = calculate_metrics(monthly)
    assessment = assess_trend(metrics)

    return {
        "language": language,
        "project": project,
        "article": article,
        "metrics": metrics,
        "assessment": assessment,
    }


def main():
    args = parse_args()

    results = []

    for market in args.market:
        parts = market.split("|")

        if len(parts) != 3:
            raise ValueError(
                "Each --market must use "
                "'Language|project|article' format."
            )

        language, project, article = parts

        result = analyze_market(
            language=language,
            project=project,
            article=article,
            start=args.start,
            end=args.end,
        )

        results.append(result)

    comparison = compare_markets(results)

    print("\nMARKET COMPARISON:")

    for index, market in enumerate(comparison, start=1):
        print(f"\n{index}. {market['language']}")
        print(f"Article: {market['article']}")
        print(
            f"Average monthly views: "
            f"{market['avg_monthly_views']}"
        )
        print(
            f"Period growth: "
            f"{market['period_growth_pct']}%"
        )
        print(
            f"YoY growth: "
            f"{market['year_over_year_growth_pct']}%"
        )
        print(
            f"Monthly volatility: "
            f"{market['monthly_volatility_pct']}%"
        )
        print(f"Trend: {market['trend']}")
        print(f"Confidence: {market['confidence']}")


if __name__ == "__main__":
    main()