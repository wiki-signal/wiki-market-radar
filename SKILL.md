---
name: wiki-market-radar
description: Analyze Wikipedia pageview data to evaluate topic-interest trends across one or more language editions. Use when a user wants to measure whether interest in a topic is growing, stable, or declining, compare interest between language markets, assess confidence in the observed trend, generate a chart, or create a short PDF report.
compatibility: Requires Python 3.12+, internet access to Wikimedia APIs, and the Python dependencies declared in pyproject.toml.
---

# Wiki Market Radar

Use this skill to analyze Wikipedia pageview trends as a signal of information interest.

The skill can:

- analyze one Wikipedia article in one language edition;
- compare the same concept across multiple language editions;
- calculate growth, year-over-year change, volatility, positive-month share, and outliers;
- classify the trend as Growing, Stable, or Declining;
- estimate confidence as High, Medium, or Low;
- generate a monthly trend chart;
- generate a one-page PDF report for a single-market analysis.

Wikipedia pageviews are an information-interest signal. Do not treat them as direct evidence of purchase intent, revenue potential, total addressable market, or willingness to pay.

## Workflow

Follow this sequence:

1. Identify the topic or concept the user wants to analyze.
2. Identify the requested Wikipedia language edition or editions.
3. Determine the analysis period.
4. Resolve the correct article title for each Wikipedia edition.
5. Use `scripts/analyze.py` for one market or `scripts/compare.py` for multiple markets.
6. Read the calculated metrics and assessment.
7. Interpret the results in the context of the user's question.
8. Clearly state limitations and uncertainty.
9. If assumptions change in a follow-up request, rerun only the affected analysis.

Do not invent pageview values or calculate trend metrics manually when the scripts can calculate them.

## Single-market analysis

Use:

```bash
python scripts/analyze.py \
  --project <project> \
  --article "<article>" \
  --language "<language>" \
  --start <YYYYMMDDHH> \
  --end <YYYYMMDDHH> \
  --output-dir <directory>