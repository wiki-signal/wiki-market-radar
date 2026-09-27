from pathlib import Path

from matplotlib import get_data_path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
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
    """Create a one-page PDF summary of the analysis."""

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
            f"<b>Topic:</b> {article}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Language:</b> {language}",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 6 * mm))

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
            f'{metrics["period_growth_pct"]:.2f}%',
        ],
        [
            "Year-over-year growth",
            (
                f'{metrics["year_over_year_growth_pct"]:.2f}%'
                if metrics["year_over_year_growth_pct"] is not None
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
                ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "DejaVuSans"),
                ("GRID", (0, 0), (-1, -1), 0.5, "#CCCCCC"),
                ("BACKGROUND", (0, 0), (-1, 0), "#EEEEEE"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            f'<b>Trend:</b> {assessment["trend"]}',
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f'<b>Confidence:</b> {assessment["confidence"]}',
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f'<b>Reason:</b> {assessment["reason"]}',
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