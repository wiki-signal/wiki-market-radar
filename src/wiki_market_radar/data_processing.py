import pandas as pd


def prepare_pageviews(items: list[dict]) -> pd.DataFrame:
    """Convert raw Wikimedia API data into a clean daily DataFrame."""

    if not items:
        raise ValueError("No pageview data received.")

    df = pd.DataFrame(items)

    required_columns = {"timestamp", "views"}

    if not required_columns.issubset(df.columns):
        raise ValueError("API response does not contain required fields.")

    df = df[["timestamp", "views"]].copy()

    df["date"] = pd.to_datetime(
        df["timestamp"],
        format="%Y%m%d%H",
    )

    df["views"] = pd.to_numeric(
        df["views"],
        errors="coerce",
    )

    df = df.dropna(subset=["date", "views"])

    df = df.sort_values("date")

    return df[["date", "views"]]


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily pageviews into monthly totals."""

    monthly = (
        df.set_index("date")
        .resample("MS")["views"]
        .sum()
        .reset_index()
    )

    return monthly