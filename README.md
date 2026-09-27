# Wiki Market Radar

An Agent Skill for analyzing Wikipedia pageview trends as a signal of topic interest across different language markets.

The project uses Wikimedia pageview data to help answer questions such as:

- Is interest in a topic growing or declining?
- How stable is the observed trend?
- How does interest differ between Wikipedia language editions?
- Which markets may be worth investigating further?

Wikipedia pageviews are treated as an information-interest signal, not as direct evidence of purchase intent or market size.

## Features

- Fetch Wikipedia pageview data through the Wikimedia API
- Normalize daily pageview observations
- Aggregate daily data into monthly totals
- Calculate trend metrics
- Detect unusual months using IQR-based outlier detection
- Classify trends as `Growing`, `Stable`, or `Declining`
- Estimate signal confidence as `High`, `Medium`, or `Low`
- Compare multiple Wikipedia language editions
- Generate PNG trend charts
- Generate one-page PDF reports
- Expose the workflow through CLI tools
- Package the workflow as an Agent Skill

## Architecture

```text
User request
    ↓
LLM / AI Agent
    ↓
SKILL.md
    ↓
CLI workflow
    ↓
Wikimedia API
    ↓
Data processing
    ↓
Monthly aggregation
    ↓
Analytics
    ↓
Trend + confidence
    ↓
Visualization / PDF
    ↓
LLM interpretation
    ↓
User-facing answer
```

The main design principle is to separate probabilistic language reasoning from deterministic data analysis.

The LLM is responsible for understanding user intent, selecting the correct workflow, resolving parameters, and explaining the result.

Python performs the numerical calculations so the same inputs produce reproducible analytical outputs.

## Project Structure

```text
wiki-market-radar/
├── SKILL.md
├── README.md
├── pyproject.toml
├── scripts/
│   ├── analyze.py
│   └── compare.py
├── src/
│   └── wiki_market_radar/
│       ├── analytics.py
│       ├── comparison.py
│       ├── confidence.py
│       ├── data_processing.py
│       ├── reporting.py
│       ├── visualization.py
│       └── wikimedia_client.py
├── tests/
│   └── test_core.py
└── examples/
```

## Installation

Python 3.12 or newer is recommended.

Create and activate a virtual environment, then install the project:

```bash
python -m pip install -e .
```

Development dependencies can be installed with:

```bash
python -m pip install -e ".[dev]"
```

## Single-Market Analysis

Example:

```bash
python scripts/analyze.py \
  --project uk.wikipedia.org \
  --article "Астрономія" \
  --language "Ukrainian" \
  --start 2024010100 \
  --end 2025123100 \
  --output-dir output/astronomy
```

The workflow produces:

- calculated metrics;
- trend classification;
- confidence assessment;
- PNG trend chart;
- one-page PDF report.

Generated filenames are based on the analyzed article.

## Multi-Market Comparison

Multiple Wikipedia editions can be analyzed over the same period.

Example:

```bash
python scripts/compare.py \
  --market "Polish|pl.wikipedia.org|Astronomia" \
  --market "Czech|cs.wikipedia.org|Astronomie" \
  --start 2024010100 \
  --end 2025123100
```

Each market is processed through the same analytical pipeline so that results remain comparable.

## Metrics

### Average monthly views

Mean monthly pageview volume over the analyzed period.

### Period growth

Compares the average of the first three months with the average of the final three months:

```text
(last window average / first window average - 1) × 100
```

Averaged windows are used instead of individual endpoints to reduce sensitivity to random spikes.

### Year-over-year growth

Compares the latest month with the same month one year earlier.

This metric is available when enough historical data exists.

### Monthly volatility

Standard deviation of month-to-month percentage changes.

Higher values indicate a less stable signal.

### Positive months

Percentage of month-to-month transitions where pageviews increased.

This helps distinguish persistent movement from changes driven by only a small number of months.

### Outlier months

Detected using the interquartile range (IQR) method.

Outliers can indicate news events, seasonality, viral attention, or other temporary effects.

## Trend Classification

The current deterministic rules are:

```text
Period growth > +10%  → Growing
Period growth < -10%  → Declining
Otherwise             → Stable
```

These thresholds are intentionally explicit so that the classification is auditable and easy to modify.

## Confidence

Confidence is not an LLM-generated confidence score.

It is calculated using explicit rules based on:

- analysis-period length;
- monthly volatility;
- outlier count;
- whether month-to-month behavior supports the overall trend.

Possible results:

```text
High
Medium
Low
```

## Visualization

The generated chart contains:

- monthly pageview observations;
- a three-month moving average.

The moving average helps distinguish the underlying direction from short-term spikes.

## Agent Skill

`SKILL.md` describes when and how an AI agent should use the project.

The Skill separates two responsibilities:

```text
LLM
→ understand the request
→ select the workflow
→ interpret the result

Python
→ retrieve data
→ process data
→ calculate metrics
→ evaluate trend quality
→ create artifacts
```

This design reduces the amount of reasoning required from the language model and makes the Skill suitable for smaller and less expensive tool-capable models.

## Validation

The Agent Skill format can be validated with:

```bash
agentskills validate <path-to-skill>
```

The current Skill passes Agent Skills validation.

## Tests

Run:

```bash
pytest -v
```

The test suite covers:

- pageview preparation and aggregation;
- metric calculation;
- trend and confidence classification;
- market comparison.

## Linting

Run:

```bash
ruff check .
```

Ruff is used to detect Python style and code-quality issues.

## Development Verification

The implementation was checked at several levels:

```text
Agent Skill specification → agentskills validator
Python code quality       → Ruff
Core analytical logic     → Pytest
End-to-end behavior       → Wikimedia API test runs
Generated artifacts       → manual chart and PDF inspection
```

## AI-Assisted Development

AI tools were used as an engineering assistant during development for:

- architecture discussion;
- code explanation;
- debugging;
- code review;
- identifying edge cases;
- improving documentation.

AI-generated suggestions were not treated as ground truth.

The implementation was verified through deterministic test cases, linting, Agent Skill validation, real Wikimedia API requests, and manual inspection of generated outputs.

For example, an initial Wikimedia API request returned an HTTP error. The request behavior was investigated and corrected by adding an appropriate client `User-Agent`, after which the API workflow was verified with real pageview data.

## Limitations

Wikipedia pageviews measure information attention, not commercial demand.

Important limitations include:

- pageviews do not measure willingness to pay;
- Wikipedia editions differ in audience size;
- article coverage may differ across languages;
- news events can create temporary spikes;
- pageview trends alone are insufficient for market-sizing decisions.

The output should therefore be treated as an input to further market research rather than a final investment decision.

## Future Improvements

Possible next iterations include:

- automatic article resolution across languages;
- caching repeated Wikimedia requests;
- asynchronous fetching for larger market sets;
- stronger statistical trend estimation;
- improved seasonality handling;
- more robust anomaly detection;
- comparative charts and PDF reports;
- additional demand signals such as search or product-market data;
- persistent storage for larger research workflows.

The current implementation intentionally keeps the architecture lightweight and focused on the core analytical problem.