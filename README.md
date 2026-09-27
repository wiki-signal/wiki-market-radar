# Wiki Market Radar

[![CI](https://github.com/wiki-signal/wiki-market-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/wiki-signal/wiki-market-radar/actions/workflows/ci.yml)

**Wiki Market Radar** is an Agent Skill for analyzing Wikipedia pageview history as an early signal of topic interest across language editions.

It is designed for B2C product exploration: comparing topics or language audiences, identifying whether interest is growing or declining, estimating how reliable the observed trend is, and producing a concise shareable report.

The core principle is simple:

> **The LLM understands the request and explains the result. Python retrieves the data, calculates the metrics, classifies the trend, and generates the artifacts.**

Wikipedia pageviews are used as an **information-interest signal**, not as proof of purchase intent, market size, revenue potential, or willingness to pay.

---

## At a Glance

| Capability | Implementation |
| --- | --- |
| Natural-language research request | LLM tool calling |
| Wikipedia data retrieval | Wikimedia Pageviews API |
| Localized article resolution | MediaWiki API |
| Monthly aggregation | Python / pandas |
| Growth and YoY analysis | Deterministic Python |
| Volatility and outliers | Deterministic Python |
| Trend classification | Deterministic rules |
| Confidence assessment | Deterministic rules |
| Cross-language comparison | Shared analytical pipeline |
| Visualization | matplotlib |
| Shareable output | One-page PDF |
| Cheap-model validation | OpenRouter free model routing |
| Automated verification | Ruff + pytest + Agent Skills validator + GitHub Actions |

---

## What the User Gets

A natural-language request can produce three artifacts:

```text
outputs/
└── llm_e2e/
    └── <run_id>/
        ├── comparison_trend.png
        ├── comparison_report.pdf
        └── final_answer.md
```

The one-page comparison report combines:

- a compact table with the calculated metrics;
- a shared trend chart for the selected Wikipedia editions;
- a short analytical summary;
- a clear limitation statement.

The table is the detailed quantitative layer, the chart shows the observed trajectory, and the analytical summary explains the most important differences without repeating the full table.

---

## How the Result Is Produced

The final result is based on real Wikimedia data and a deterministic analytical pipeline.

```text
Natural-language request
        ↓
LLM interprets topic, languages, period and criteria
        ↓
LLM calls the analytical tool
        ↓
Localized Wikipedia articles are resolved and verified
        ↓
Wikimedia Pageviews API returns raw pageview history
        ↓
Python aggregates observations by month
        ↓
Python calculates metrics
        ↓
Python determines Trend and Confidence
        ↓
Markets / language editions are compared
        ↓
Python generates the comparison chart
        ↓
LLM explains the deterministic result
        ↓
One-page PDF + PNG + Markdown summary
```

The LLM is **not** responsible for calculating growth, volatility, confidence, or other numerical metrics.

This boundary is intentional: it reduces arithmetic hallucinations and makes the Skill suitable for fast, inexpensive tool-capable models.

---

# Quick Start

## 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2. Install the project

```powershell
python -m pip install -e ".[dev]"
```

## 3. Run the deterministic tests

```powershell
ruff check .
pytest -v
agentskills validate .
```

---

# Natural-Language End-to-End Demo

The full E2E workflow uses OpenRouter to test how a low-cost model follows the Agent Skill and calls the deterministic analytical code.

Set the API key:

```powershell
$env:OPENROUTER_API_KEY="your-key"
```

Run the built-in demonstration:

```powershell
python scripts/llm_e2e_test.py
```

Or provide your own natural-language request:

```powershell
python scripts/llm_e2e_test.py --request "Compare interest in cybersecurity in Polish, German and English Wikipedia for 2024–2025. I care most about stability of the signal."
```

The request may change:

- topic;
- language editions;
- analysis period;
- comparison set;
- evaluation criterion.

The E2E runner converts the natural-language request into structured tool arguments and then executes the same deterministic Python pipeline used by the project.

Each run creates a separate output directory:

```text
outputs/llm_e2e/<run_id>/
```

This prevents one report from overwriting another and makes runs easier to inspect.

---

# Example Questions

The Skill is not limited to a predefined topic.

Examples:

> Compare the growth of interest in intermittent fasting in Polish and Czech Wikipedia over the last two years.

> We are considering an astronomy course. Is interest in astronomy growing in Ukrainian Wikipedia, and how reliable is the trend?

> Compare interest in cybersecurity in Polish, German and English Wikipedia for 2024–2025. Prioritize stability.

> Compare electric-vehicle interest across German, French and Spanish Wikipedia and identify which signals deserve further validation.

The topic itself is not hardcoded into the analytical core.

---

# User-Defined Evaluation Criteria

Users may define what matters most for their decision.

For example:

| User criterion | Primary analytical signal |
| --- | --- |
| Highest absolute attention | Average monthly views |
| Strongest growth | Period change |
| Strongest recent movement | YoY change |
| Most stable signal | Monthly volatility + Confidence |
| Most reliable trend | Confidence |
| Consistent direction | Trend + positive-month share |

The Skill does not silently replace the user's criterion with another one.

If a requested criterion cannot be evaluated from Wikipedia pageviews, the Skill should say so and identify what additional evidence would be required.

---

# Architecture

```text
                    USER / HOST AGENT
                           │
                           ▼
                       SKILL.md
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       Natural-language            Direct CLI
        E2E workflow                 workflows
              │                         │
              ▼                         │
   scripts/llm_e2e_test.py              │
              │                         │
              └────────────┬────────────┘
                           ▼
              src/wiki_market_radar/
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
       Wikimedia       Analytics      Confidence
         APIs             │              │
                           └──────┬───────┘
                                  ▼
                              Comparison
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                    Visualization       Reporting
                         │                 │
                         ▼                 ▼
                        PNG              PDF
```

---

# Why This Design

The project separates probabilistic language reasoning from deterministic data processing.

| LLM / Agent | Python |
| --- | --- |
| Understand the request | Retrieve Wikimedia data |
| Identify topic and languages | Aggregate monthly data |
| Propose localized article titles | Calculate metrics |
| Detect user criteria | Classify Trend |
| Call the analytical workflow | Calculate Confidence |
| Explain the result | Compare markets |
| Suggest the next validation step | Generate charts and reports |

This makes the system easier to test and reduces dependence on model quality.

A cheaper model does not need to perform statistical calculations correctly. It only needs to understand the request, construct the tool call, and explain already-calculated results.

---

# Article Resolution

The same concept may have different article titles in different Wikipedia editions.

The E2E workflow therefore:

1. asks the LLM for a localized candidate article;
2. verifies that the article exists through the MediaWiki API;
3. follows redirects when applicable;
4. falls back to Wikipedia search if the proposed title does not exist;
5. analyzes the resolved real article.

The prompt instructs the model to select the **general encyclopedic article that directly represents the requested concept**, rather than an unrelated company, brand, product, person, or narrow example.

The direct CLI workflows expect an explicit article title.

---

# Deterministic CLI Workflows

## Single-market analysis

```powershell
python scripts/analyze.py `
  --project uk.wikipedia.org `
  --article "Штучний інтелект" `
  --language "Ukrainian" `
  --start 2024010100 `
  --end 2025123100 `
  --output-dir outputs/ai_uk
```

The single-market workflow can generate:

- calculated metrics;
- Trend;
- Confidence;
- monthly chart;
- one-page PDF.

## Multi-market comparison

```powershell
python scripts/compare.py `
  --market "Polish|pl.wikipedia.org|Sztuczna inteligencja" `
  --market "Czech|cs.wikipedia.org|Umělá inteligence" `
  --market "Ukrainian|uk.wikipedia.org|Штучний інтелект" `
  --start 2024010100 `
  --end 2025123100
```

These workflows are useful for validating the analytical core without involving an external LLM.

---

# Metrics

## Average Monthly Views

`avg_monthly_views`

Average number of pageviews per month during the selected period.

This represents absolute information attention inside the selected Wikipedia edition.

It is **not** interpreted as market size.

---

## Period Change

Internal field:

```text
period_growth_pct
```

The metric compares the average level near the beginning of the selected period with the average level near the end.

The implementation uses up to the first three and final three months to reduce sensitivity to a single month.

Interpretation:

- positive → interest increased across the period;
- negative → interest decreased;
- near zero → broadly stable.

The report uses the neutral user-facing label **Period change** because the result may be either positive or negative.

---

## Year-over-Year Change

Internal field:

```text
year_over_year_growth_pct
```

Compares the most recent month with the same month one year earlier.

If insufficient history is available, YoY is reported as unavailable.

Period change and YoY are separate metrics and must not be mixed.

---

## Monthly Volatility

`monthly_volatility_pct`

Calculated from month-to-month percentage changes.

Higher volatility means the observed signal changes more sharply between months.

Lower volatility indicates a more consistent signal.

---

## Positive Months

`positive_months_pct`

Percentage of month-to-month changes that were positive.

This supports the Trend classification by showing how consistently the series moved in the same direction.

---

## Outlier Months

`outlier_months_count`

Outliers are detected using the interquartile-range rule.

They help identify whether a trend may be distorted by unusual spikes or drops.

---

# Trend Classification

Trend is deterministic:

```text
Growing
Stable
Declining
```

Current thresholds:

```text
Period change > +10%  → Growing
Period change < -10%  → Declining
otherwise             → Stable
```

A language edition can have high absolute attention while still having a declining trend.

Absolute level and direction are intentionally treated as separate concepts.

---

# Confidence

Confidence describes **signal quality**, not commercial attractiveness and not the LLM's subjective confidence.

Supported values:

```text
High
Medium
Low
```

The deterministic score considers:

- length of historical data;
- monthly volatility;
- number of outlier months;
- consistency between monthly direction and the classified Trend.

This allows the report to distinguish between a strong trend signal and a noisy or weakly supported one.

---

# One-Page Report

The comparison PDF is intentionally compact.

It contains:

```text
Title
  ↓
Comparison table
  ↓
Trend chart + Analytical summary
  ↓
Limitation
```

The table provides the detailed metrics.

The chart shows the time-series behavior.

The summary is kept to one short paragraph and focuses on the main analytical differences and the user's evaluation criterion.

The report avoids repeating the full table in prose.

---

# Follow-Up Requests

The Python analytical layer is stateless.

Conversation state belongs to the host agent.

For example, after an initial request the user may say:

```text
Now use Germany instead of Poland.
```

or:

```text
Use only the last 12 months.
```

or:

```text
Prioritize stability instead of growth.
```

The agent should preserve unchanged assumptions and rerun the affected analysis with the updated parameters.

Previously calculated numerical values should not be manually edited.

---

# Project Structure

```text
wiki-market-radar/
│
├── SKILL.md
├── README.md
├── pyproject.toml
│
├── src/
│   └── wiki_market_radar/
│       ├── __init__.py
│       ├── wikimedia_client.py
│       ├── data_processing.py
│       ├── analytics.py
│       ├── confidence.py
│       ├── comparison.py
│       ├── visualization.py
│       └── reporting.py
│
├── scripts/
│   ├── analyze.py
│   ├── compare.py
│   └── llm_e2e_test.py
│
├── tests/
│   └── test_core.py
│
├── examples/
│   └── sample_case/
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

# Component Responsibilities

| Component | Responsibility |
| --- | --- |
| `SKILL.md` | Agent behavior, workflow, interpretation rules and limitations |
| `wikimedia_client.py` | Wikimedia Pageviews API |
| `data_processing.py` | Prepare and aggregate pageview observations |
| `analytics.py` | Deterministic metric calculations |
| `confidence.py` | Trend and Confidence rules |
| `comparison.py` | Cross-language comparison |
| `visualization.py` | Single-market and comparison charts |
| `reporting.py` | One-page PDF generation |
| `analyze.py` | Single-market deterministic CLI |
| `compare.py` | Multi-market deterministic CLI |
| `llm_e2e_test.py` | Full natural-language / tool-calling validation |
| `test_core.py` | Core deterministic tests |
| `ci.yml` | Automated repository verification |

---

# Requirement Coverage

| Task requirement | Implementation |
| --- | --- |
| Agent Skill format | `SKILL.md` |
| Own meaningful data-processing code | `src/wiki_market_radar/` |
| Wikipedia pageview analysis | `wikimedia_client.py` + analytics pipeline |
| Arbitrary topics and languages | Natural-language tool workflow + parameterized CLI |
| Charts | `visualization.py` |
| Short shareable report | `reporting.py` |
| One-page PDF | Comparison and single-market reporting |
| Explicit assumptions and limitations | `SKILL.md` + PDF limitation |
| User-defined prospectiveness criteria | Skill criteria mapping |
| Follow-up requests | Re-run affected analysis with updated inputs |
| Fast / inexpensive LLM validation | OpenRouter E2E workflow |
| Reproducible dependencies | `pyproject.toml` |
| Automated checks | Ruff + pytest + Agent Skills validator + GitHub Actions |

---

# Verification

Local verification:

```powershell
ruff check .
pytest -v
agentskills validate .
```

The test suite covers the deterministic core, including:

```text
prepare + aggregate pageviews
metric calculation
trend / confidence assessment
market comparison
```

GitHub Actions repeats the repository checks on pushes.

The LLM E2E workflow is intentionally manual because it depends on an external OpenRouter API key and free-model availability.

---

# LLM End-to-End Validation

The E2E scenario validates the full chain:

```text
User request
→ Skill instructions
→ LLM tool call
→ article resolution
→ Wikimedia data
→ deterministic analytics
→ comparison
→ LLM interpretation
→ chart
→ one-page PDF
```

The model is configured as:

```text
openrouter/free
```

OpenRouter may route the request to different available free models.

The script prints the actual model used during each run.

The API key is read from:

```text
OPENROUTER_API_KEY
```

and is not stored in source code.

---

# AI-Assisted Development

AI tools were used during implementation for tasks such as:

- discussing architecture;
- drafting code;
- identifying edge cases;
- improving prompts and documentation;
- reviewing implementation decisions.

AI-generated work was not accepted purely on model output.

It was checked through:

- deterministic unit tests;
- Ruff static checks;
- Agent Skills validation;
- real Wikimedia API runs;
- manual inspection of calculated metrics;
- manual inspection of generated charts and PDFs;
- end-to-end testing with an inexpensive tool-capable model;
- GitHub Actions.

The goal was to use AI as an implementation assistant while keeping verification deterministic wherever possible.

---

# Limitations

The current version intentionally has several limitations:

- Wikipedia pageviews measure information interest rather than commercial demand.
- Different language editions have different total audience sizes, so raw pageview levels are not directly normalized by Wikipedia-edition size.
- One article may not fully represent a broad commercial topic.
- External events may create temporary spikes or drops.
- Article resolution still depends partly on LLM interpretation in the E2E workflow.
- Confidence measures the quality of the observed trend signal, not the probability of commercial success.
- A promising Wikipedia signal should be validated with additional demand or commercial-intent evidence.

---

# Possible Next Iterations

The Skill can be extended incrementally with:

- multiple related articles per concept;
- better semantic entity resolution;
- normalization across Wikipedia edition sizes;
- event-spike detection;
- caching of Wikimedia responses;
- larger batch comparisons;
- configurable user-defined scoring;
- complementary search-demand signals;
- competitor and app-store data;
- commercial-intent or conversion data.

The deterministic analytical core should remain separate from the LLM orchestration layer as the system grows.

---

# Summary

Wiki Market Radar is designed to answer a practical question:

> **Where does Wikipedia data show meaningful and sufficiently reliable information interest that deserves deeper product validation?**

The Skill does not attempt to prove product demand from Wikipedia alone.

Instead, it turns a natural-language research question into a reproducible data workflow, calculates the relevant metrics deterministically, communicates the main differences clearly, and produces a compact report that can be used as the starting point for the next research decision.