import argparse
from pathlib import Path

from wiki_market_radar.analytics import calculate_metrics
from wiki_market_radar.confidence import assess_trend
from wiki_market_radar.data_processing import (
    aggregate_monthly,
    prepare_pageviews,
)
from wiki_market_radar.reporting import create_pdf_report
from wiki_market_radar.visualization import create_trend_chart
from wiki_market_radar.wikimedia_client import fetch_pageviews


def make_safe_name(value: str) -> str:
    """Create a filesystem-friendly name from an article title."""

    name = "".join(
        char.lower() if char.isalnum() else "_"
        for char in value
    )

    while "__" in name:
        name = name.replace("__", "_")

    return name.strip("_") or "analysis"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze Wikipedia pageview trends."
    )

    parser.add_argument(
        "--project",
        required=True,
        help="Wikipedia project, e.g. uk.wikipedia.org",
    )

    parser.add_argument(
        "--article",
        required=True,
        help="Wikipedia article title",
    )

    parser.add_argument(
        "--language",
        required=True,
        help="Human-readable language name",
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

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory for generated files",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    topic_name = make_safe_name(args.article)

    pageviews = fetch_pageviews(
        project=args.project,
        article=args.article,
        start=args.start,
        end=args.end,
    )

    daily = prepare_pageviews(pageviews)
    monthly = aggregate_monthly(daily)

    metrics = calculate_metrics(monthly)
    assessment = assess_trend(metrics)

    chart_path = create_trend_chart(
        monthly=monthly,
        article=args.article,
        language=args.language,
        output_path=str(
            output_dir / f"{topic_name}_trend.png"
        ),
    )

    report_path = create_pdf_report(
        metrics=metrics,
        assessment=assessment,
        chart_path=chart_path,
        article=args.article,
        language=args.language,
        output_path=str(
            output_dir / f"{topic_name}_report.pdf"
        ),
    )

    print("\nMETRICS:")
    for name, value in metrics.items():
        print(f"{name}: {value}")

    print("\nASSESSMENT:")
    for name, value in assessment.items():
        print(f"{name}: {value}")

    print("\nCHART:")
    print(chart_path)

    print("\nREPORT:")
    print(report_path)


if __name__ == "__main__":
    main()