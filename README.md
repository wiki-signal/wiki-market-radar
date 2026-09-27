# Wiki Market Radar

[![CI](https://github.com/wiki-signal/wiki-market-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/wiki-signal/wiki-market-radar/actions/workflows/ci.yml)

An Agent Skill for using Wikipedia pageview history as an early signal of topic interest across language markets.

The intended user is a B2C product team asking questions such as:

- Is interest in a topic growing or declining?
- Is the observed trend stable enough to take seriously?
- How does the same topic behave across language editions?
- Which markets are worth researching further?

The project deliberately treats Wikipedia traffic as an **information-interest signal**, not as evidence of purchase intent or market size.

---

## At a Glance

| | |
| --- | --- |
| **Input** | Natural-language research question or explicit CLI parameters |
| **Primary data source** | Wikimedia Pageviews API |
| **Core analysis** | Deterministic Python |
| **Agent interface** | `SKILL.md` |
| **Main metrics** | Growth, YoY growth, volatility, positive months, outliers |
| **Assessment** | Growing / Stable / Declining + High / Medium / Low confidence |
| **Outputs** | Structured result, PNG chart, one-page PDF |
| **Multi-market support** | Yes |
| **LLM E2E test** | OpenRouter free tool-capable model |
| **Verification** | Ruff, pytest, Agent Skill validator, GitHub Actions |

---

## Example Questions

The Skill is designed for questions like:

> Compare interest in astronomy in Polish and Czech Wikipedia during 2024–2025.

> Is interest in astronomy growing in Ukrainian Wikipedia, and how much confidence should we place in that trend?

> Compare interest in learning English across several Wikipedia language editions and identify which audiences may deserve further research.

The topic, language editions, time period, and evaluation criteria are not fixed to these examples.

---

## Why This Design

The main design decision is to keep **language reasoning** separate from **numerical analysis**.

| LLM / AI Agent | Python |
| --- | --- |
| Understands the user's intent | Retrieves real Wikimedia data |
| Selects the required workflow | Validates and normalizes inputs |
| Converts natural language into tool arguments | Aggregates observations |
| Interprets calculated results | Calculates metrics |
| Explains assumptions and limitations | Classifies trend and confidence |

The LLM is therefore not responsible for calculating growth percentages or inventing pageview values.

For the same analytical inputs, the Python layer produces the same calculations.

---

## Requirement Coverage

The implementation maps directly to the main requirements of the task.

| Requirement | Implementation |
| --- | --- |
| Agent Skill | `SKILL.md` |
| Own executable data logic | `src/wiki_market_radar/` |
| Wikipedia pageview analysis | `wikimedia_client.py` + processing pipeline |
| Trend analysis | `analytics.py` |
| Reliability / confidence | `confidence.py` |
| Language-market comparison | `comparison.py` |
| Charts | `visualization.py` |
| Short shareable report | `reporting.py` |
| Single-market workflow | `scripts/analyze.py` |
| Multi-market workflow | `scripts/compare.py` |
| Full LLM tool-calling scenario | `scripts/llm_e2e_test.py` |
| Automated verification | pytest + Ruff + GitHub Actions |
| Agent Skills validation | reference validator |

---

## Quick Start

Python 3.12+ is recommended.

### Install

```bash
python -m pip install -e .
```

For development dependencies:

```bash
python -m pip install -e ".[dev]"
```

### Run a single-market analysis

```bash
python scripts/analyze.py --project uk.wikipedia.org --article "Астрономія" --language "Ukrainian" --start 2024010100 --end 2025123100 --output-dir output/astronomy
```

The workflow produces:

- calculated metrics;
- trend classification;
- confidence assessment;
- a PNG trend chart;
- a one-page PDF report.

### Compare language markets

```bash
python scripts/compare.py --market "Polish|pl.wikipedia.org|Astronomia" --market "Czech|cs.wikipedia.org|Astronomie" --start 2024010100 --end 2025123100
```

Both markets pass through the same analytical pipeline, so their metrics are calculated consistently.

---

## How It Works

```text
User question
      ↓
AI Agent / LLM
      ↓
SKILL.md
      ↓
structured tool arguments
      ↓
Python workflow
      ↓
Wikimedia API
      ↓
daily pageviews
      ↓
monthly aggregation
      ↓
metrics
      ↓
trend + confidence
      ↓
chart / report / structured result
      ↓
LLM interpretation
      ↓
user-facing answer
```

`SKILL.md` defines when the Skill should be used and how the agent should approach the task.

The Python package handles the part that should be reproducible: fetching data, processing it, calculating metrics, and assessing signal quality.

---

## Project Structure

```text
wiki-market-radar/
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── scripts/
│   ├── analyze.py
│   ├── compare.py
│   └── llm_e2e_test.py
│
├── src/
│   └── wiki_market_radar/
│       ├── analytics.py
│       ├── comparison.py
│       ├── confidence.py
│       ├── data_processing.py
│       ├── reporting.py
│       ├── visualization.py
│       └── wikimedia_client.py
│
├── tests/
│   └── test_core.py
│
├── .gitignore
├── pyproject.toml
├── README.md
└── SKILL.md
```

### Component Responsibilities

| Component | Responsibility |
| --- | --- |
| `SKILL.md` | Instructions and usage contract for the agent |
| `wikimedia_client.py` | Wikimedia Pageviews API communication |
| `data_processing.py` | Pageview preparation and monthly aggregation |
| `analytics.py` | Quantitative metric calculation |
| `confidence.py` | Trend classification and confidence assessment |
| `comparison.py` | Comparable multi-market results |
| `visualization.py` | Trend-chart generation |
| `reporting.py` | One-page PDF generation |
| `analyze.py` | Direct single-market workflow |
| `compare.py` | Direct multi-market workflow |
| `llm_e2e_test.py` | LLM → tool → Python → LLM integration test |
| `test_core.py` | Deterministic core tests |
| `ci.yml` | Automated repository checks |

---

## Metrics

The metrics are intentionally simple enough to explain and audit.

| Metric | What it answers | Calculation |
| --- | --- | --- |
| **Average monthly views** | What is the typical traffic level? | Mean monthly pageviews |
| **Period growth** | Has interest changed over the period? | First analysis window vs final analysis window |
| **YoY growth** | How does the latest month compare with a year earlier? | Latest month vs same month previous year |
| **Monthly volatility** | How unstable is the signal? | Standard deviation of monthly percentage changes |
| **Positive months** | How consistently does traffic move upward? | Share of month-to-month increases |
| **Outlier months** | Are unusual months influencing the series? | IQR-based detection |

### Period Growth

Rather than comparing two individual dates, the implementation compares short averaged windows.

By default, it uses up to the first three and last three months:

```text
(last window average / first window average - 1) × 100
```

This makes the metric less sensitive to a single endpoint spike.

### Year-over-Year Growth

```text
(latest month / same month previous year - 1) × 100
```

YoY is returned only when enough historical data exists.

### Outliers

Unusual months are identified using the interquartile range (IQR).

They are not automatically removed. A spike can contain useful information — for example, a news event or sudden public attention — but it should also reduce confidence in a supposedly stable trend.

---

## Trend Classification

Trend direction is deliberately rule-based:

```text
Period growth > +10%  → Growing
Period growth < -10%  → Declining
Otherwise             → Stable
```

The thresholds are explicit rather than hidden inside an LLM prompt.

That makes the classification easy to inspect, test, and change.

---

## Confidence

`Confidence` is **not the language model saying how confident it feels**.

It is a deterministic assessment of signal quality.

Four checks are used:

| Check | Question |
| --- | --- |
| Historical coverage | Is there enough history? |
| Volatility | Is the month-to-month signal reasonably stable? |
| Outliers | Is the result dominated by unusual months? |
| Directional consistency | Do monthly changes support the overall trend? |

Current scoring:

| Supporting checks | Confidence |
| ---: | --- |
| 4 | High |
| 2–3 | Medium |
| 0–1 | Low |

This keeps two concepts separate:

**Trend** answers:

> In which direction is interest moving?

**Confidence** answers:

> How well does the observed data support that classification?

---

## Charts and Reports

A single-market run can generate a trend chart containing:

- monthly pageviews;
- a three-month moving average.

The moving average is included to make the underlying direction easier to see when individual months are noisy.

The PDF report combines:

- topic and language;
- key metrics;
- trend;
- confidence;
- confidence reason;
- chart;
- the main interpretation limitation.

The goal is a short research artifact that can be shared without requiring access to the code.

---

## Agent and LLM Flow

The intended user interface is natural language.

A user does **not** need to provide Wikimedia API paths or know the internal metric names.

The agent:

1. reads the user request;
2. uses `SKILL.md` to select the workflow;
3. creates structured tool parameters;
4. receives deterministic results from Python;
5. explains those results in the context of the original question.

The analytical code remains independent of the wording used by the user.

---

## LLM End-to-End Test

The project includes a separate end-to-end harness:

```text
scripts/llm_e2e_test.py
```

It tests the full agent loop rather than only isolated Python functions:

```text
Natural-language request
        ↓
LLM
        ↓
tool call
        ↓
validated parameters
        ↓
real Wikimedia request
        ↓
Python analysis
        ↓
tool result
        ↓
LLM
        ↓
final explanation
```

The test uses:

```text
openrouter/free
```

through OpenRouter.

The free router can select an available free model that supports the features required by the request, including tool calling. The exact underlying model may therefore vary between runs.

### Run

Set the API key through the environment:

```powershell
$env:OPENROUTER_API_KEY="your-key"
```

Then:

```bash
python scripts/llm_e2e_test.py
```

A successful run shows:

```text
MODEL USED
LLM TOOL ARGUMENTS
TOOL RESULT
LLM FINAL ANSWER
```

No OpenRouter credential is stored in the repository.

### Article Resolution in the E2E Scenario

The model proposes an article title for each requested Wikipedia edition.

Before pageview analysis, the E2E workflow checks the candidate against the MediaWiki API and can resolve a valid article title.

The direct CLI workflows remain intentionally simpler: they expect an explicit Wikipedia article title.

This distinction keeps the analytical core deterministic while allowing the agent-facing scenario to work with natural-language topics.

---

## Follow-up Requests

The analytical functions are stateless.

A user can change:

- topic;
- language editions;
- date range;
- comparison set;
- assumptions.

The agent can then call the same workflow again with the updated parameters.

Conversation history itself belongs to the host AI agent rather than to the Python package. The package focuses on producing reproducible analysis for each requested set of inputs.

---

## Verification

The implementation is checked at several levels.

### Code quality

```bash
ruff check .
```

### Deterministic tests

```bash
pytest -v
```

The current tests cover:

- data preparation and monthly aggregation;
- metric calculation;
- trend and confidence assessment;
- market comparison.

### Agent Skill format

The Skill can be checked with the Agent Skills reference validator:

```bash
agentskills validate /absolute/path/to/wiki-market-radar
```

### Real integrations

Development also included:

- real Wikimedia API requests;
- generated chart inspection;
- generated PDF inspection;
- a live LLM tool-calling run through OpenRouter.

### Continuous Integration

GitHub Actions repeats the deterministic checks after pushes to the repository.

The LLM E2E test is kept outside CI because it depends on an external model provider, credentials, and current free-model availability.

---

## Engineering Decisions

A few choices were deliberately kept simple for this version.

| Decision | Reason |
| --- | --- |
| Monthly rather than daily trend analysis | Reduces day-to-day noise |
| Short averaged growth windows | Less sensitive to a single endpoint |
| Explicit trend thresholds | Easy to audit and change |
| Separate trend and confidence | Direction and signal quality are different questions |
| Python for calculations | Reproducible results instead of LLM arithmetic |
| LLM for orchestration and interpretation | Natural-language flexibility where it is useful |
| No database in the MVP | Current workflows do not require persistent state |
| No asynchronous pipeline yet | Current comparison scale does not justify the added complexity |

The intent was to solve the analytical problem first and avoid infrastructure that did not improve the requested workflow.

---

## AI-Assisted Development

AI tools were used during development for:

- discussing architecture;
- explaining unfamiliar concepts;
- implementation suggestions;
- debugging;
- reviewing code;
- identifying edge cases;
- improving documentation.

AI suggestions were not treated as authoritative output.

They were checked through a combination of:

```text
code inspection
+ Ruff
+ deterministic tests
+ Agent Skill validation
+ real Wikimedia requests
+ manual artifact inspection
+ LLM end-to-end testing
```

One practical example was Wikimedia API request handling: HTTP failures observed during real execution were investigated and the client behavior was corrected before the integration was considered complete.

---

## Limitations

Wikipedia pageviews measure attention to information, not commercial demand.

The main limitations are:

- pageviews do not measure willingness to pay;
- Wikipedia language editions have different audience sizes;
- article coverage can differ between languages;
- semantically similar concepts may not map perfectly to equivalent articles;
- news and viral events can create temporary spikes;
- seasonality can influence the observed trend;
- traffic alone is not sufficient for market-sizing or investment decisions.

For that reason, the output should be used as **one research signal** for deciding what to investigate next, not as a standalone go/no-go decision.

---

## Next Iterations

The next improvements I would prioritize are:

1. move topic/article resolution from the E2E harness into a reusable core component;
2. improve cross-language concept matching;
3. add caching for repeated Wikimedia requests;
4. add stronger seasonality-aware trend estimation;
5. add comparative charts and multi-market PDF reports;
6. introduce asynchronous fetching only when the number of markets makes it useful;
7. combine Wikipedia interest with additional demand signals.

For larger research workflows, persistent storage and richer conversational state could be introduced later without changing the current boundary between LLM orchestration and deterministic analysis.