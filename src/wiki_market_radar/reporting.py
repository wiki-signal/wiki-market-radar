import html
import re
from pathlib import Path

from matplotlib import get_data_path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def register_fonts():
    """Register Unicode fonts bundled with matplotlib."""

    fonts_dir = Path(get_data_path()) / "fonts" / "ttf"

    pdfmetrics.registerFont(
        TTFont(
            "DejaVuSans",
            str(fonts_dir / "DejaVuSans.ttf"),
        )
    )

    pdfmetrics.registerFont(
        TTFont(
            "DejaVuSans-Bold",
            str(fonts_dir / "DejaVuSans-Bold.ttf"),
        )
    )

    pdfmetrics.registerFontFamily(
        "DejaVuSans",
        normal="DejaVuSans",
        bold="DejaVuSans-Bold",
    )


def create_pdf_report(
    metrics: dict,
    assessment: dict,
    chart_path: str,
    article: str,
    language: str,
    output_path: str,
) -> str:
    """Create a one-page PDF summary of a single-market analysis."""

    register_fonts()

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    styles["Title"].fontName = "DejaVuSans-Bold"
    styles["Normal"].fontName = "DejaVuSans"

    story = []

    story.append(
        Paragraph(
            "Wikipedia Market Interest Report",
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Topic:</b> {html.escape(article)}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Language:</b> {html.escape(language)}",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 6 * mm))

    yoy_growth = metrics["year_over_year_growth_pct"]

    data = [
        ["Metric", "Value"],
        [
            "Analysis period",
            f'{metrics["analysis_period_months"]} months',
        ],
        [
            "Average monthly views",
            f'{metrics["avg_monthly_views"]:,.0f}',
        ],
        [
            "Period growth",
            f'{metrics["period_growth_pct"]:+.2f}%',
        ],
        [
            "Year-over-year growth",
            (
                f"{yoy_growth:+.2f}%"
                if yoy_growth is not None
                else "N/A"
            ),
        ],
        [
            "Monthly volatility",
            f'{metrics["monthly_volatility_pct"]:.2f}%',
        ],
        [
            "Positive months",
            f'{metrics["positive_months_pct"]:.2f}%',
        ],
        [
            "Outlier months",
            str(metrics["outlier_months_count"]),
        ],
    ]

    table = Table(
        data,
        colWidths=[70 * mm, 70 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "DejaVuSans-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "DejaVuSans",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CCCCCC"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#EEEEEE"),
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            (
                f'<b>Trend:</b> '
                f'{html.escape(assessment["trend"])}'
            ),
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            (
                f'<b>Confidence:</b> '
                f'{html.escape(assessment["confidence"])}'
            ),
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            (
                f'<b>Reason:</b> '
                f'{html.escape(assessment["reason"])}'
            ),
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 5 * mm))

    story.append(
        Image(
            chart_path,
            width=170 * mm,
            height=92 * mm,
        )
    )

    story.append(Spacer(1, 3 * mm))

    story.append(
        Paragraph(
            (
                "<b>Limitation:</b> Wikipedia pageviews indicate "
                "information interest, not purchase intent or market size."
            ),
            styles["Normal"],
        )
    )

    doc.build(story)

    return str(path)


def _format_percentage(
    value: float | None,
    digits: int = 1,
) -> str:
    """Format an optional percentage value."""

    if value is None:
        return "N/A"

    return f"{value:+.{digits}f}%"


def _clean_summary(summary: str) -> str:
    """Convert Markdown-like LLM output to compact PDF-safe text."""

    cleaned = summary.strip()

    cleaned = re.sub(
        r"^#{1,6}\s*",
        "",
        cleaned,
        flags=re.MULTILINE,
    )

    cleaned = re.sub(
        r"^\s*[-*]\s+",
        "• ",
        cleaned,
        flags=re.MULTILINE,
    )

    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("`", "")

    cleaned = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned,
    )

    # Keep the one-page report compact even if a free model
    # returns a longer answer than requested.
    if len(cleaned) > 1400:
        cleaned = f"{cleaned[:1397].rstrip()}..."

    return html.escape(cleaned).replace("\n", "<br/>")


def create_comparison_pdf_report(
    comparison: list[dict],
    chart_path: str,
    summary: str,
    output_path: str,
) -> str:
    """Create a one-page PDF report for a multi-market comparison."""

    if not comparison:
        raise ValueError(
            "At least one market is required "
            "for a comparison report."
        )

    register_fonts()

    path = Path(output_path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=9 * mm,
        bottomMargin=9 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ComparisonTitle",
        parent=styles["Title"],
        fontName="DejaVuSans-Bold",
        fontSize=17,
        leading=20,
        spaceAfter=3 * mm,
    )

    section_style = ParagraphStyle(
        "ComparisonSection",
        parent=styles["Heading2"],
        fontName="DejaVuSans-Bold",
        fontSize=10,
        leading=12,
        spaceAfter=2 * mm,
    )

    summary_style = ParagraphStyle(
        "ComparisonSummary",
        parent=styles["Normal"],
        fontName="DejaVuSans",
        fontSize=8.2,
        leading=10.4,
    )

    limitation_style = ParagraphStyle(
        "ComparisonLimitation",
        parent=styles["Normal"],
        fontName="DejaVuSans",
        fontSize=7.5,
        leading=9,
    )

    story = []

    story.append(
        Paragraph(
            "Wikipedia Market Interest — Comparison Report",
            title_style,
        )
    )

    table_data = [
        [
            "Market",
            "Article",
            "Avg / month",
            "Period growth",
            "YoY",
            "Volatility",
            "Trend",
            "Confidence",
        ]
    ]

    for item in comparison:
        table_data.append(
            [
                html.escape(str(item["language"])),
                html.escape(str(item["article"])),
                f'{item["avg_monthly_views"]:,.0f}',
                _format_percentage(
                    item["period_growth_pct"]
                ),
                _format_percentage(
                    item["year_over_year_growth_pct"]
                ),
                (
                    f'{item["monthly_volatility_pct"]:.1f}%'
                ),
                html.escape(str(item["trend"])),
                html.escape(str(item["confidence"])),
            ]
        )

    metrics_table = Table(
        table_data,
        colWidths=[
            25 * mm,
            45 * mm,
            28 * mm,
            27 * mm,
            23 * mm,
            24 * mm,
            24 * mm,
            26 * mm,
        ],
        repeatRows=1,
    )

    metrics_table.setStyle(
        TableStyle(
            [
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "DejaVuSans-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "DejaVuSans",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7.2,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E9EEF5"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1F2937"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#C9CED6"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (2, 1),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    story.append(metrics_table)
    story.append(Spacer(1, 4 * mm))

    chart = Image(
        chart_path,
        width=158 * mm,
        height=80 * mm,
    )

    summary_block = [
        Paragraph(
            "Analytical summary",
            section_style,
        ),
        Paragraph(
            _clean_summary(summary),
            summary_style,
        ),
    ]

    content_table = Table(
        [
            [
                chart,
                summary_block,
            ]
        ],
        colWidths=[
            164 * mm,
            97 * mm,
        ],
    )

    content_table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    story.append(content_table)
    story.append(Spacer(1, 3 * mm))

    story.append(
        Paragraph(
            (
                "<b>Limitation:</b> Wikipedia pageviews are a signal "
                "of information interest. They do not directly measure "
                "purchase intent, willingness to pay, revenue, "
                "or market size."
            ),
            limitation_style,
        )
    )

    doc.build(story)

    return str(path)