def assess_trend(metrics: dict) -> dict:
    """Classify trend and estimate confidence from calculated metrics."""

    growth = metrics["period_growth_pct"]
    volatility = metrics["monthly_volatility_pct"]
    positive_months = metrics["positive_months_pct"]
    outliers = metrics["outlier_months_count"]
    months = metrics["analysis_period_months"]

    # Trend classification
    if growth > 10:
        trend = "Growing"
    elif growth < -10:
        trend = "Declining"
    else:
        trend = "Stable"

    score = 0
    reasons = []

    # Enough historical data
    if months >= 12:
        score += 1
    else:
        reasons.append("limited historical data")

    # Signal stability
    if volatility <= 30:
        score += 1
    else:
        reasons.append("high volatility")

    # Outlier control
    if outliers <= max(1, round(months * 0.1)):
        score += 1
    else:
        reasons.append("multiple outlier months")

    # Does month-to-month behavior support the overall trend?
    if trend == "Growing" and positive_months >= 55:
        score += 1
    elif trend == "Declining" and positive_months <= 45:
        score += 1
    elif trend == "Stable" and 40 <= positive_months <= 60:
        score += 1
    else:
        reasons.append("monthly direction does not strongly support the trend")

    if score >= 4:
        confidence = "High"
    elif score >= 2:
        confidence = "Medium"
    else:
        confidence = "Low"

    if not reasons:
        reasons.append("signal is consistent and relatively stable")

    return {
        "trend": trend,
        "confidence": confidence,
        "reason": "; ".join(reasons),
    }