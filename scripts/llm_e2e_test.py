import json
import os
from datetime import date
from pathlib import Path

import requests

from wiki_market_radar.analytics import calculate_metrics
from wiki_market_radar.comparison import compare_markets
from wiki_market_radar.confidence import assess_trend
from wiki_market_radar.data_processing import (
    aggregate_monthly,
    prepare_pageviews,
)
from wiki_market_radar.wikimedia_client import fetch_pageviews

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"

WIKIPEDIA_HEADERS = {
    "User-Agent": (
        "wiki-market-radar/0.1 "
        "(https://github.com/wiki-signal/wiki-market-radar)"
    )
}


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
    """Resolve a candidate to an existing Wikipedia article title."""

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
            "srlimit": 1,
            "format": "json",
            "formatversion": 2,
        },
        timeout=30,
    )

    response.raise_for_status()

    results = response.json()["query"]["search"]

    if not results:
        raise ValueError(
            f"No Wikipedia article found for '{article}' "
            f"in {project}."
        )

    return results[0]["title"]


def analyze_market(
    language: str,
    project: str,
    article: str,
    start: str,
    end: str,
) -> dict:
    """Analyze one Wikipedia language market."""

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
        "article": resolved_article,
        "metrics": metrics,
        "assessment": assessment,
    }


def run_comparison(
    markets: list[dict],
    start: str,
    end: str,
) -> list[dict]:
    """Run the same deterministic analysis for every market."""

    start = normalize_timestamp(start)
    end = normalize_timestamp(end)

    results = []

    for market in markets:
        result = analyze_market(
            language=market["language"],
            project=market["project"],
            article=market["article"],
            start=start,
            end=end,
        )

        results.append(result)

    return compare_markets(results)


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


def main():
    skill_text = Path("SKILL.md").read_text(
        encoding="utf-8"
    )

    user_request = (
        "Порівняй інтерес до астрономії "
        "в польськомовній та чеськомовній Wikipedia "
        "за 2024–2025 роки. Покажи основні метрики, "
        "тренд і рівень confidence та зроби короткий висновок."
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "compare_wikipedia_markets",
                "description": (
                    "Compare Wikipedia pageview trends "
                    "across multiple language markets."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "markets": {
                            "type": "array",
                            "description": (
                                "Wikipedia language markets to compare."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "language": {
                                        "type": "string",
                                        "description": (
                                            "Human-readable language name."
                                        ),
                                    },
                                    "project": {
                                        "type": "string",
                                        "description": (
                                            "Wikipedia project, for example "
                                            "pl.wikipedia.org."
                                        ),
                                    },
                                    "article": {
                                        "type": "string",
                                        "description": (
                                            "Candidate article title in the "
                                            "requested Wikipedia edition. "
                                            "The tool validates and resolves "
                                            "the title before analysis."
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
                                "Start date. YYYY-MM-DD, YYYYMMDD, "
                                "or YYYYMMDDHH are accepted. "
                                "If the user specifies a whole year "
                                "or year range without exact dates, "
                                "use January 1 of the first requested year."
                            ),
                        },
                        "end": {
                            "type": "string",
                            "description": (
                                "End date. YYYY-MM-DD, YYYYMMDD, "
                                "or YYYYMMDDHH are accepted. "
                                "If the user specifies a whole year "
                                "or year range without exact dates, "
                                "use December 31 of the final requested year."
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

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI agent using the following Agent Skill. "
                "Follow its instructions carefully.\n\n"
                f"{skill_text}\n\n"
                "Important rules:\n"
                "- Use tools for factual calculations.\n"
                "- Do not calculate quantitative metrics yourself.\n"
                "- Do not invent Wikipedia pageview values.\n"
                "- If a user specifies a complete year range, analyze "
                "the complete range from January 1 of the first year "
                "through December 31 of the final year."
            ),
        },
        {
            "role": "user",
            "content": user_request,
        },
    ]

    first_response = call_openrouter(
        messages=messages,
        tools=tools,
    )

    print("\nMODEL USED:")
    print(first_response.get("model", MODEL))

    assistant_message = first_response["choices"][0]["message"]
    tool_calls = assistant_message.get("tool_calls")

    if not tool_calls:
        raise RuntimeError(
            "The model did not call the comparison tool."
        )

    messages.append(assistant_message)

    comparison = None

    for tool_call in tool_calls:
        function = tool_call["function"]

        if function["name"] != "compare_wikipedia_markets":
            continue

        arguments = json.loads(function["arguments"])

        print("\nLLM TOOL ARGUMENTS:")
        print(
            json.dumps(
                arguments,
                ensure_ascii=False,
                indent=2,
            )
        )

        comparison = run_comparison(
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

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(
                    comparison,
                    ensure_ascii=False,
                ),
            }
        )

    if comparison is None:
        raise RuntimeError(
            "Comparison tool did not produce a result."
        )

    messages.append(
        {
            "role": "user",
            "content": (
                "Сформуй фінальний результат українською мовою, "
                "використовуючи тільки дані з TOOL RESULT.\n\n"
                "Формат відповіді має бути таким:\n\n"
                "## Результат аналізу\n\n"
                "Для кожного ринку окремо вкажи:\n"
                "- назву мови та статті;\n"
                "- середню кількість переглядів на місяць;\n"
                "- зміну інтересу за весь період;\n"
                "- YoY-зміну;\n"
                "- місячну волатильність;\n"
                "- тренд;\n"
                "- confidence.\n\n"
                "Після цього додай розділ:\n"
                "## Порівняння\n"
                "У 2–3 реченнях поясни головну різницю "
                "між ринками на основі наведених метрик.\n\n"
                "Потім додай:\n"
                "## Як читати метрики\n"
                "Коротко, одним реченням на показник, поясни:\n"
                "- Period growth — зміна між середнім рівнем "
                "на початку і наприкінці періоду;\n"
                "- YoY — зміна останнього місяця порівняно "
                "з тим самим місяцем попереднього року;\n"
                "- Volatility — наскільки сильно змінювалися "
                "місячні темпи переглядів;\n"
                "- Confidence — наскільки надійним є визначений "
                "тренд з урахуванням обсягу історії, "
                "волатильності, викидів і послідовності руху.\n\n"
                "Наприкінці додай:\n"
                "## Обмеження\n"
                "Одним реченням зазнач, що Wikipedia pageviews "
                "відображають інформаційний інтерес, але не є "
                "прямим доказом попиту, доходу, розміру ринку "
                "або готовності платити.\n\n"
                "Вимоги до стилю:\n"
                "- відповідь тільки українською;\n"
                "- коротко і професійно;\n"
                "- не показуй внутрішні міркування;\n"
                "- не додавай даних, яких немає в TOOL RESULT;\n"
                "- не роби маркетингових рекомендацій;\n"
                "- відсотки округлюй максимум до двох знаків;\n"
                "- явно став знак + для позитивної зміни "
                "та знак - для негативної."
            ),
        }
    )

    final_response = call_openrouter(
        messages=messages,
    )

    answer = final_response["choices"][0]["message"]["content"]

    print("\nLLM FINAL ANSWER:")
    print(answer)


if __name__ == "__main__":
    main()