import argparse
import json
import os
from datetime import UTC, date, datetime
from pathlib import Path

import requests

from wiki_market_radar.analytics import calculate_metrics
from wiki_market_radar.comparison import compare_markets
from wiki_market_radar.confidence import assess_trend
from wiki_market_radar.data_processing import (
    aggregate_monthly,
    prepare_pageviews,
)
from wiki_market_radar.reporting import create_comparison_pdf_report
from wiki_market_radar.visualization import create_comparison_chart
from wiki_market_radar.wikimedia_client import fetch_pageviews

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"

WIKIPEDIA_HEADERS = {
    "User-Agent": (
        "wiki-market-radar/0.1 "
        "(https://github.com/wiki-signal/wiki-market-radar)"
    )
}

DEFAULT_USER_REQUEST = (
    "Порівняй динаміку інтересу до штучного інтелекту "
    "в польськомовній, чеськомовній та україномовній Wikipedia "
    "за 2024–2025 роки. Порівняй абсолютний інтерес, динаміку, "
    "стабільність сигналу, trend і confidence та коротко поясни, "
    "що варто перевірити далі."
)

VERIFIED_DEMO_MARKETS = [
    {
        "language": "Polish",
        "project": "pl.wikipedia.org",
        "article": "Sztuczna inteligencja",
    },
    {
        "language": "Czech",
        "project": "cs.wikipedia.org",
        "article": "Umělá inteligence",
    },
    {
        "language": "Ukrainian",
        "project": "uk.wikipedia.org",
        "article": "Штучний інтелект",
    },
]

VERIFIED_DEMO_START = "2024-01-01"
VERIFIED_DEMO_END = "2025-12-31"


def parse_args() -> argparse.Namespace:
    """Parse an optional natural-language request from the CLI."""

    parser = argparse.ArgumentParser(
        description="Run the Wiki Market Radar LLM end-to-end demo."
    )

    parser.add_argument(
        "--request",
        default=None,
        help=(
            "Natural-language research request. If omitted, "
            "the verified Artificial Intelligence reference "
            "scenario is used."
        ),
    )

    return parser.parse_args()


def normalize_timestamp(value: str) -> str:
    """Convert common date formats to Wikimedia timestamp format."""

    value = value.strip()

    if len(value) == 10 and "-" in value:
        parsed_date = date.fromisoformat(value)
        return parsed_date.strftime("%Y%m%d00")

    if len(value) == 8 and value.isdigit():
        return f"{value}00"

    if len(value) == 10 and value.isdigit():
        return value

    raise ValueError(
        f"Unsupported date format: {value}. "
        "Use YYYY-MM-DD, YYYYMMDD, or YYYYMMDDHH."
    )


def resolve_article_title(
    project: str,
    article: str,
) -> str:
    """Resolve a Wikipedia article and follow redirects."""

    url = f"https://{project}/w/api.php"

    response = requests.get(
        url,
        headers=WIKIPEDIA_HEADERS,
        params={
            "action": "query",
            "titles": article,
            "redirects": 1,
            "format": "json",
            "formatversion": 2,
        },
        timeout=30,
    )

    response.raise_for_status()

    pages = response.json()["query"]["pages"]

    if pages and not pages[0].get("missing"):
        return pages[0]["title"]

    response = requests.get(
        url,
        headers=WIKIPEDIA_HEADERS,
        params={
            "action": "query",
            "list": "search",
            "srsearch": article,
            "srlimit": 3,
            "format": "json",
            "formatversion": 2,
        },
        timeout=30,
    )

    response.raise_for_status()

    results = response.json()["query"]["search"]

    if not results:
        raise ValueError(
            f"No Wikipedia article found for '{article}' in {project}."
        )

    return results[0]["title"]


def analyze_market(
    language: str,
    project: str,
    article: str,
    start: str,
    end: str,
) -> dict:
    """Analyze one Wikipedia language edition."""

    resolved_article = resolve_article_title(
        project=project,
        article=article,
    )

    pageviews = fetch_pageviews(
        project=project,
        article=resolved_article,
        start=start,
        end=end,
    )

    daily = prepare_pageviews(pageviews)
    monthly = aggregate_monthly(daily)

    metrics = calculate_metrics(monthly)
    assessment = assess_trend(metrics)

    return {
        "language": language,
        "project": project,
        "article": resolved_article,
        "metrics": metrics,
        "assessment": assessment,
        "monthly": monthly,
    }


def run_comparison(
    markets: list[dict],
    start: str,
    end: str,
) -> tuple[list[dict], list[dict]]:
    """Run deterministic analysis for all requested editions."""

    normalized_start = normalize_timestamp(start)
    normalized_end = normalize_timestamp(end)

    detailed_results = []

    for market in markets:
        result = analyze_market(
            language=market["language"],
            project=market["project"],
            article=market["article"],
            start=normalized_start,
            end=normalized_end,
        )

        detailed_results.append(result)

    comparison = compare_markets(detailed_results)

    return comparison, detailed_results


def call_openrouter(
    messages: list[dict],
    tools: list[dict] | None = None,
) -> dict:
    """Send a chat-completion request to OpenRouter."""

    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY environment variable is not set."
        )

    payload = {
        "model": MODEL,
        "messages": messages,
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def build_tools() -> list[dict]:
    """Return the analytical tool exposed to the LLM."""

    return [
        {
            "type": "function",
            "function": {
                "name": "compare_wikipedia_markets",
                "description": (
                    "Analyze and compare Wikipedia pageview trends "
                    "for the same broad encyclopedic concept across "
                    "one or more language editions."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "markets": {
                            "type": "array",
                            "description": (
                                "Wikipedia language editions to analyze. "
                                "Every article must represent the same "
                                "underlying concept."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "language": {
                                        "type": "string",
                                    },
                                    "project": {
                                        "type": "string",
                                        "description": (
                                            "Wikipedia project such as "
                                            "pl.wikipedia.org."
                                        ),
                                    },
                                    "article": {
                                        "type": "string",
                                        "description": (
                                            "Localized canonical Wikipedia "
                                            "article directly representing "
                                            "the requested broad concept. "
                                            "Do not choose a company, brand, "
                                            "product, person, example, or "
                                            "narrower related topic unless "
                                            "explicitly requested."
                                        ),
                                    },
                                },
                                "required": [
                                    "language",
                                    "project",
                                    "article",
                                ],
                            },
                        },
                        "start": {
                            "type": "string",
                            "description": (
                                "Analysis start date. Use January 1 "
                                "when the user requests full years."
                            ),
                        },
                        "end": {
                            "type": "string",
                            "description": (
                                "Analysis end date. Use December 31 "
                                "when the user requests full years."
                            ),
                        },
                    },
                    "required": [
                        "markets",
                        "start",
                        "end",
                    ],
                },
            },
        }
    ]


def validate_tool_arguments(arguments: dict) -> None:
    """Validate LLM-generated tool arguments before execution."""

    if not isinstance(arguments, dict):
        raise TypeError("Tool arguments must be a dictionary.")

    markets = arguments.get("markets")

    if not isinstance(markets, list):
        raise TypeError("Markets must be provided as a list.")

    if not markets:
        raise ValueError("The LLM returned no markets.")

    for market in markets:
        if not isinstance(market, dict):
            raise TypeError("Each market definition must be a dictionary.")

        language = market.get("language")
        project = market.get("project")
        article = market.get("article")

        if not language or not project or not article:
            raise ValueError(
                "Every market requires language, project, and article."
            )

        if not isinstance(language, str):
            raise TypeError("Market language must be a string.")

        if not isinstance(project, str):
            raise TypeError("Wikipedia project must be a string.")

        if not isinstance(article, str):
            raise TypeError("Wikipedia article must be a string.")

        if not project.endswith(".wikipedia.org"):
            raise ValueError(
                f"Invalid Wikipedia project: {project}"
            )

    start = arguments.get("start")
    end = arguments.get("end")

    if not isinstance(start, str) or not isinstance(end, str):
        raise TypeError(
            "Analysis start and end dates must be strings."
        )

    normalize_timestamp(start)
    normalize_timestamp(end)


def get_llm_arguments(
    user_request: str,
    skill_text: str,
) -> tuple[dict, str]:
    """Convert a natural-language request into validated tool arguments."""

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI agent using the following Agent Skill.\n\n"
                f"{skill_text}\n\n"
                "Execution rules:\n"
                "- You MUST call the analytical tool.\n"
                "- Select the broad canonical encyclopedic article "
                "representing the requested concept.\n"
                "- Every language edition must represent the same concept.\n"
                "- Never substitute a company, brand, product, person, "
                "or narrower example for a broad topic unless explicitly "
                "requested.\n"
                "- If complete years are requested, use January 1 through "
                "December 31.\n"
                "- Do not calculate quantitative metrics yourself."
            ),
        },
        {
            "role": "user",
            "content": user_request,
        },
    ]

    response = call_openrouter(
        messages=messages,
        tools=build_tools(),
    )

    model_used = response.get("model", MODEL)

    assistant_message = response["choices"][0]["message"]
    tool_calls = assistant_message.get("tool_calls")

    if not tool_calls:
        raise RuntimeError(
            "The model did not call the analytical tool."
        )

    for tool_call in tool_calls:
        function = tool_call.get("function", {})

        if function.get("name") != "compare_wikipedia_markets":
            continue

        arguments = json.loads(
            function["arguments"]
        )

        validate_tool_arguments(arguments)

        return arguments, model_used

    raise RuntimeError(
        "No supported analytical tool call was returned."
    )


def detect_focus(user_request: str) -> str:
    """Detect a simple user-defined comparison focus."""

    text = user_request.casefold()

    if any(
        term in text
        for term in (
            "stability",
            "stable",
            "стабіль",
            "стабиль",
        )
    ):
        return "stability"

    if any(
        term in text
        for term in (
            "growth",
            "growing",
            "зрост",
            "рост",
        )
    ):
        return "growth"

    if any(
        term in text
        for term in (
            "confidence",
            "reliable",
            "надійн",
            "уверенн",
        )
    ):
        return "confidence"

    return "general"


def build_fallback_summary(
    comparison: list[dict],
    user_request: str,
) -> str:
    """Build a deterministic one-paragraph analytical summary."""

    highest_interest = max(
        comparison,
        key=lambda item: item["avg_monthly_views"],
    )

    lowest_volatility = min(
        comparison,
        key=lambda item: item["monthly_volatility_pct"],
    )

    highest_volatility = max(
        comparison,
        key=lambda item: item["monthly_volatility_pct"],
    )

    strongest_growth = max(
        comparison,
        key=lambda item: item["period_growth_pct"],
    )

    strongest_decline = min(
        comparison,
        key=lambda item: item["period_growth_pct"],
    )

    trends = {
        item["trend"]
        for item in comparison
    }

    if len(trends) == 1:
        trend_sentence = (
            f"All analyzed editions have a "
            f"{next(iter(trends))} trend."
        )
    else:
        trend_sentence = (
            "The analyzed editions show different Trend classifications."
        )

    focus = detect_focus(user_request)

    if focus == "stability":
        focus_sentence = (
            f"Under the requested stability criterion, "
            f"{lowest_volatility['language']} provides the most stable "
            f"observed signal, while "
            f"{highest_volatility['language']} is the least stable."
        )
    elif focus == "growth":
        if strongest_growth["period_growth_pct"] > 0:
            focus_sentence = (
                f"Under the growth criterion, "
                f"{strongest_growth['language']} shows the strongest "
                f"period increase."
            )
        else:
            focus_sentence = (
                f"Under the growth criterion, all compared editions "
                f"declined, with {strongest_growth['language']} showing "
                f"the smallest decline."
            )
    elif focus == "confidence":
        high_confidence = [
            item["language"]
            for item in comparison
            if item["confidence"] == "High"
        ]

        if high_confidence:
            joined = ", ".join(high_confidence)

            focus_sentence = (
                f"The highest deterministic Confidence is observed for "
                f"{joined}."
            )
        else:
            focus_sentence = (
                "None of the analyzed editions has High Confidence."
            )
    else:
        focus_sentence = (
            f"{lowest_volatility['language']} has the most stable "
            f"observed signal, while "
            f"{highest_volatility['language']} is the least stable."
        )

    direction_sentence = (
        f"{strongest_decline['language']} shows the strongest period "
        f"decline, while {strongest_growth['language']} has the strongest "
        f"relative period result among the compared editions."
    )

    return (
        f"{highest_interest['language']} Wikipedia shows the highest "
        f"absolute information interest among the analyzed editions. "
        f"{trend_sentence} "
        f"{direction_sentence} "
        f"{focus_sentence} "
        "The next step is to validate the Wikipedia signal against "
        "search-demand or commercial-intent data."
    )


def clean_summary(value: str) -> str:
    """Convert model output into a compact single paragraph."""

    text = " ".join(value.split()).strip()

    prefixes = (
        "analytical summary",
        "summary",
        "conclusion",
        "висновок",
    )

    lowered = text.casefold()

    for prefix in prefixes:
        if lowered.startswith(prefix):
            text = text[len(prefix):].lstrip(" :—-#")
            break

    return text


def summary_is_usable(summary: str) -> bool:
    """Check whether an LLM summary is suitable for the report."""

    if not summary:
        return False

    if len(summary) < 150 or len(summary) > 1200:
        return False

    forbidden = (
        "###",
        "•",
        "\n-",
    )

    return not any(
        marker in summary
        for marker in forbidden
    )


def generate_summary(
    user_request: str,
    comparison: list[dict],
    skill_text: str,
) -> str:
    """Generate a concise LLM summary with deterministic fallback."""

    fallback = build_fallback_summary(
        comparison=comparison,
        user_request=user_request,
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are producing the analytical-summary paragraph "
                "for a one-page Wikipedia topic-interest report.\n\n"
                f"{skill_text}\n\n"
                "The numerical data supplied by Python is the source "
                "of truth."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Original request:\n{user_request}\n\n"
                "Deterministic Python result:\n"
                f"{json.dumps(comparison, ensure_ascii=False, indent=2)}"
                "\n\n"
                "Write the report summary in English.\n"
                "Return exactly ONE plain-text paragraph of 4–6 short "
                "sentences.\n"
                "Do not use headings, bullets, numbered lists, or Markdown.\n"
                "Do not repeat the entire table.\n"
                "Explain the highest absolute information interest, "
                "the overall Trend pattern, the most important difference "
                "in direction, stability and Confidence, and the user's "
                "criterion when present.\n"
                "Finish with exactly one relevant next validation step.\n"
                "Do not repeat the Wikipedia limitation because the PDF "
                "already contains it.\n"
                "Never recalculate or invent numerical values."
            ),
        },
    ]

    try:
        response = call_openrouter(
            messages=messages,
        )

        content = response["choices"][0]["message"]["content"]

        if not isinstance(content, str):
            return fallback

        summary = clean_summary(content)

        if summary_is_usable(summary):
            return summary

    except (
        requests.RequestException,
        RuntimeError,
        ValueError,
        KeyError,
        IndexError,
        TypeError,
    ):
        pass

    return fallback


def create_run_output_dir() -> Path:
    """Create a unique output directory for the current E2E run."""

    run_id = datetime.now(UTC).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    output_dir = (
        Path("outputs")
        / "llm_e2e"
        / run_id
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_dir


def main() -> None:
    args = parse_args()

    use_verified_demo = args.request is None

    if use_verified_demo:
        user_request = DEFAULT_USER_REQUEST
    else:
        user_request = args.request.strip()

        if not user_request:
            raise ValueError(
                "--request cannot be empty."
            )

    skill_text = Path("SKILL.md").read_text(
        encoding="utf-8"
    )

    print("\nUSER REQUEST:")
    print(user_request)

    if use_verified_demo:
        print("\nMODE:")
        print("Verified Artificial Intelligence reference scenario")

        arguments = {
            "markets": VERIFIED_DEMO_MARKETS,
            "start": VERIFIED_DEMO_START,
            "end": VERIFIED_DEMO_END,
        }

        model_used = "verified deterministic demo inputs"

        if os.environ.get("OPENROUTER_API_KEY"):
            try:
                llm_arguments, model_used = get_llm_arguments(
                    user_request=user_request,
                    skill_text=skill_text,
                )

                print("\nLLM PROPOSED TOOL ARGUMENTS:")
                print(
                    json.dumps(
                        llm_arguments,
                        ensure_ascii=False,
                        indent=2,
                    )
                )

                print(
                    "\nVerified reference inputs are used for execution."
                )

            except (
                requests.RequestException,
                RuntimeError,
                ValueError,
                KeyError,
                IndexError,
                TypeError,
                json.JSONDecodeError,
            ) as exc:
                print(
                    "\nWARNING: "
                    f"LLM tool-call validation was unavailable: {exc}"
                )
                print(
                    "Continuing with verified reference inputs."
                )

    else:
        arguments, model_used = get_llm_arguments(
            user_request=user_request,
            skill_text=skill_text,
        )

    print("\nMODEL USED:")
    print(model_used)

    print("\nEXECUTION ARGUMENTS:")
    print(
        json.dumps(
            arguments,
            ensure_ascii=False,
            indent=2,
        )
    )

    comparison, detailed_results = run_comparison(
        markets=arguments["markets"],
        start=arguments["start"],
        end=arguments["end"],
    )

    print("\nTOOL RESULT:")
    print(
        json.dumps(
            comparison,
            ensure_ascii=False,
            indent=2,
        )
    )

    answer = generate_summary(
        user_request=user_request,
        comparison=comparison,
        skill_text=skill_text,
    )

    print("\nANALYTICAL SUMMARY:")
    print(answer)

    output_dir = create_run_output_dir()

    chart_path = create_comparison_chart(
        results=detailed_results,
        output_path=str(
            output_dir / "comparison_trend.png"
        ),
    )

    report_path = create_comparison_pdf_report(
        comparison=comparison,
        chart_path=chart_path,
        summary=answer,
        output_path=str(
            output_dir / "comparison_report.pdf"
        ),
    )

    answer_path = output_dir / "final_answer.md"

    answer_path.write_text(
        answer,
        encoding="utf-8",
    )

    print("\nGENERATED ARTIFACTS:")
    print(f"Chart: {chart_path}")
    print(f"Report: {report_path}")
    print(f"Summary: {answer_path}")


if __name__ == "__main__":
    main()