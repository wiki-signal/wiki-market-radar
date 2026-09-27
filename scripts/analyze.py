from wiki_market_radar.data_processing import (
    aggregate_monthly,
    prepare_pageviews,
)
from wiki_market_radar.wikimedia_client import fetch_pageviews


def main():
    pageviews = fetch_pageviews(
        project="uk.wikipedia.org",
        article="Астрономія",
        start="2024010100",
        end="2025123100",
    )

    daily = prepare_pageviews(pageviews)
    monthly = aggregate_monthly(daily)

    print("\nDAILY DATA:")
    print(daily.head())

    print("\nMONTHLY DATA:")
    print(monthly.head())


if __name__ == "__main__":
    main()