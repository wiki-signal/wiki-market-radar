from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def create_trend_chart(
    monthly: pd.DataFrame,
    article: str,
    language: str,
    output_path: str,
) -> str:
    """Create a monthly pageview trend chart."""

    chart_data = monthly.copy()

    chart_data["rolling_avg"] = (
        chart_data["views"]
        .rolling(window=3, min_periods=1)
        .mean()
    )

    fig, ax = plt.subplots(figsize=(10, 5.5))

    ax.plot(
        chart_data["date"],
        chart_data["views"],
        marker="o",
        alpha=0.55,
        label="Monthly pageviews",
    )

    ax.plot(
        chart_data["date"],
        chart_data["rolling_avg"],
        linewidth=2.5,
        label="3-month moving average",
    )

    ax.set_title(
        f"Wikipedia interest trend — {article} ({language})"
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Pageviews")

    ax.grid(alpha=0.2)
    ax.legend()

    fig.autofmt_xdate()
    fig.tight_layout()

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        path,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(fig)

    return str(path)