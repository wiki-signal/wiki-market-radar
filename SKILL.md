---
name: wiki-market-radar
description: Analyze Wikipedia pageview data to evaluate topic-interest trends across one or more language editions. Use when a user wants to compare topic interest, determine whether interest is growing, stable, or declining, assess signal confidence, apply custom evaluation criteria, generate charts, or create a concise one-page PDF report.
compatibility: Requires Python 3.12+, internet access to Wikimedia APIs, and the Python dependencies declared in pyproject.toml.
---

# Wiki Market Radar

Use this skill to analyze Wikipedia pageview history as an early signal of information interest.

The skill is intended for B2C product exploration, for example when a team wants to decide:

- which topics deserve further research;
- which language audiences should be investigated;
- whether interest is growing, stable, or declining;
- whether an observed trend is stable enough to trust;
- which signals should be validated using additional commercial data.

Wikipedia pageviews are an information-interest proxy.

Never treat them as direct evidence of:

- purchase intent;
- willingness to pay;
- revenue;
- market size;
- product-market fit;
- commercial demand.

The purpose of the skill is to prioritize further research, not to make a final market-entry decision.

---

## Core principle

Separate probabilistic language reasoning from deterministic quantitative analysis.

The LLM should:

- understand the user's request;
- identify the topic;
- identify requested Wikipedia language editions;
- identify the analysis period;
- identify any user-defined evaluation criterion;
- propose the appropriate encyclopedic topic;
- call the analytical workflow;
- explain the calculated result.

Python should:

- resolve and verify Wikipedia articles;
- retrieve Wikimedia pageview data;
- aggregate observations by month;
- calculate metrics;
- determine Trend;
- determine Confidence;
- compare language editions;
- generate charts;
- generate PDF reports.

Never ask the LLM to calculate metrics that Python can calculate deterministically.

Never invent pageview values.

Never modify calculated values during interpretation.

---

## Workflow

Follow this sequence:

1. Identify the user's topic or concept.
2. Identify the requested Wikipedia language edition or editions.
3. Determine the requested analysis period.
4. Identify any explicit evaluation criterion.
5. Select the broad encyclopedic article representing the same concept in every language edition.
6. Verify and resolve each article.
7. Retrieve Wikimedia pageview history.
8. Aggregate observations by month.
9. Calculate the metrics.
10. Determine Trend and Confidence.
11. Compare language editions using the same metric definitions and time period.
12. Generate the chart and report.
13. Explain only the most important analytical differences.
14. State what should be validated next.
15. Preserve the Wikipedia-data limitation.

If the user changes an assumption in a follow-up request, rerun the affected analysis.

Do not manually edit old calculated values.

---

## Article selection

Article selection is critical.

For every language edition, select the broad encyclopedic article that directly represents the user's requested concept.

The compared articles must represent the same underlying concept.

Prefer:

- the canonical topic article;
- the broad encyclopedic concept;
- verified localized equivalents.

Do not substitute:

- a company;
- a brand;
- a commercial product;
- a person;
- an individual example;
- a narrower related topic;

unless the user explicitly asked for that entity.

For example, if the requested concept is cybersecurity, do not replace the general cybersecurity concept with the article for a cybersecurity company or VPN vendor.

Verify article existence before using pageview data.

Follow redirects when applicable.

If an exact proposed article does not exist, search the relevant Wikipedia edition.

If no sufficiently relevant article can be resolved, report the problem instead of silently analyzing an unrelated page.

---

## User-defined evaluation criteria

Users may define what they consider promising or important.

Examples:

- highest absolute attention;
- strongest growth;
- strongest recent movement;
- lowest volatility;
- highest confidence;
- most stable signal.

Map common criteria as follows:

| User criterion | Primary metric |
| --- | --- |
| Absolute attention | `avg_monthly_views` |
| Growth | `period_growth_pct` |
| Recent movement | `year_over_year_growth_pct` |
| Stability | `monthly_volatility_pct` + Confidence |
| Reliability | Confidence |
| Direction consistency | Trend + `positive_months_pct` |

State how the user's criterion is being interpreted.

Do not silently replace the user's criterion with another criterion.

If Wikipedia pageviews cannot measure the requested criterion, say so and identify the additional evidence required.

---

## Metrics

### Average monthly views

`avg_monthly_views`

Average Wikipedia pageviews per month over the selected period.

Use this as an indicator of absolute information attention inside that Wikipedia edition.

Do not call it market size.

### Period change

Internal field:

`period_growth_pct`

Measures the change between the average level near the beginning of the selected period and the average level near the end.

Interpretation:

- positive = interest increased;
- negative = interest decreased;
- near zero = broadly stable.

The user-facing report may call this **Period change**.

Never describe this metric as YoY.

### Year-over-year change

`year_over_year_growth_pct`

Compares the latest month with the same month one year earlier.

If the history is too short, return N/A.

Never substitute Period change for YoY change.

### Monthly volatility

`monthly_volatility_pct`

Measures variation in month-to-month percentage changes.

Lower volatility means a more stable observed signal.

Higher volatility means a noisier signal.

### Positive months

`positive_months_pct`

Percentage of month-to-month changes that were positive.

Use this as supporting evidence for directional consistency.

### Outlier months

`outlier_months_count`

Number of unusual monthly observations detected by the deterministic outlier rule.

Outliers may indicate temporary events or spikes.

---

## Trend

Trend is deterministic.

Supported values:

- `Growing`
- `Stable`
- `Declining`

Always preserve the Trend returned by Python.

Do not let the LLM replace or reinterpret the label.

Absolute attention and direction are different concepts.

A language edition can have the highest pageview volume and still have a Declining trend.

---

## Confidence

Confidence is deterministic signal-quality confidence.

It is not the LLM's subjective confidence.

Supported values:

- `High`
- `Medium`
- `Low`

Confidence considers:

- amount of historical data;
- volatility;
- outliers;
- consistency between monthly movement and the classified Trend.

Always preserve the exact Confidence value returned by Python.

Confidence does not represent probability of commercial success.

---

# Required Output Contract

Keep the final result concise, analytical, and easy to scan.

For a multi-language one-page report, use:

1. a compact metrics table;
2. one shared trend chart;
3. one short analytical-summary paragraph;
4. one limitation statement.

The table contains the detailed numbers.

The chart shows the trajectory.

The analytical summary explains what matters.

Do not repeat the entire table in prose.

---

## Analytical summary

For a comparison report, produce exactly one concise paragraph.

Normally use 4–6 short sentences.

Do not use:

- headings inside the summary;
- bullet lists;
- numbered lists;
- separate sections for every language edition;
- repeated table values.

The summary should explain:

1. which language edition has the highest absolute information interest;
2. the overall Trend pattern;
3. one important Period change or YoY difference when useful;
4. which signal is most stable;
5. which signal is least stable;
6. meaningful Confidence differences;
7. the user's explicit criterion, if one exists;
8. one next validation step.

Use exact numerical values only when they materially help the comparison.

Do not repeat every metric.

When the report layer already displays the heading `Analytical summary`, return only the paragraph body.

Do not add another `Summary`, `Conclusion`, `Висновок`, or equivalent heading.

When the report already contains the Wikipedia limitation in the footer, do not repeat it inside the summary.

---

## Example of a good comparison summary

A good summary has this form:

> English Wikipedia shows the highest absolute information interest, while all analyzed editions have a Declining trend. English and German provide the most stable signals with low volatility and High confidence, while the Polish signal is more volatile and therefore less reliable. Under a stability-focused criterion, the lower-volatility editions deserve further investigation, but the observed decline means the direction of interest should also be considered. The next step is to compare the Wikipedia signal with search-demand or commercial-intent data.

The exact language editions and conclusions must come from the actual calculated data.

Do not copy this example mechanically.

---

## One-page report requirements

A report should contain:

- clear title;
- comparison table;
- one trend chart;
- one short analytical summary;
- limitation statement.

Keep it on one page whenever the amount of requested data makes that practical.

Optimize for clarity and information density rather than decoration.

Do not add redundant charts.

---

## Follow-up requests

Users may refine the first request.

Examples:

- "Now compare Germany instead of Poland."
- "Use only the last 12 months."
- "Add Ukrainian Wikipedia."
- "Compare another topic."
- "Prioritize stability instead of growth."

Preserve unchanged assumptions.

Rerun the affected analysis.

Never manually modify previously calculated metrics.

---

## Reliability rules

Always:

- use Python output as the quantitative source of truth;
- preserve the mapping between language edition and metrics;
- preserve Trend;
- preserve Confidence;
- distinguish absolute attention from direction;
- distinguish Period change from YoY change;
- verify article existence;
- compare the same concept across editions;
- state relevant limitations.

Never:

- invent missing values;
- estimate metrics visually from the chart;
- substitute a company or product for a general concept;
- combine metrics from different language editions;
- claim Wikipedia pageviews prove commercial demand;
- claim the highest pageview edition is automatically the best market;
- interpret Confidence as probability of business success.

---

## Failure handling

If an article cannot be resolved:

- identify the affected language edition;
- do not invent a title;
- do not silently analyze an unrelated article.

If Wikimedia data cannot be retrieved:

- report the failure;
- do not fabricate observations.

If the period is too short for YoY:

- return the available metrics;
- report YoY as N/A.

A transparent partial result is preferable to a fabricated complete result.

---

## Reference scenario

A verified reference scenario is provided for reproducible testing:

- Topic: Artificial Intelligence
- Polish Wikipedia: `Sztuczna inteligencja`
- Czech Wikipedia: `Umělá inteligence`
- Ukrainian Wikipedia: `Штучний інтелект`
- Period: 2024-01-01 through 2025-12-31

This reference scenario is intended to demonstrate the full workflow reliably.

It does not mean the analytical core is hardcoded to Artificial Intelligence.

Users may provide other topics, languages, periods, and criteria through the natural-language E2E interface.

---

## Future iterations

Possible extensions include:

- stronger semantic article resolution;
- multiple related articles per concept;
- normalization for Wikipedia edition size;
- event-spike detection;
- caching;
- larger batch comparisons;
- complementary search-demand data;
- competitor and app-store data;
- configurable multi-signal scoring.

Keep deterministic data processing separate from LLM reasoning as the system grows.