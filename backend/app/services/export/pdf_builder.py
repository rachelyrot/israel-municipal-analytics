import io
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import and_

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.models.municipality import Municipality
from app.models.national_average import NationalAverage

FONT_PATH = Path(__file__).parent / "fonts" / "DavidLibre-Regular.ttf"
BASE_INDICATORS = ["POP_TOTAL", "EMP_RATE", "BUDGET_PER_CAPITA", "EDU_BAGRUT_RATE"]


def _register_font() -> None:
    if "DavidLibre" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DavidLibre", str(FONT_PATH)))


def _heb(text: str) -> str:
    """Reshape + BiDi so ReportLab renders Hebrew correctly."""
    return get_display(arabic_reshaper.reshape(str(text)))


def _trend_chart(years: list[int], values: list[float], title: str) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.plot(years, values, color="#2563eb", linewidth=2, marker="o", markersize=4)
    ax.set_xlabel("שנה", fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf


def _make_table(data: list[list]) -> Table:
    t = Table(data, colWidths=[3.5 * cm, 2.5 * cm, 3.2 * cm, 7 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, -1), "DavidLibre"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
        ("GRID",          (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("ALIGN",         (0, 0), (-1, -1), "RIGHT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build_pdf(db: Session, municipality_id: int, year: int) -> bytes:
    """Returns PDF bytes for the given municipality and year."""
    _register_font()

    muni = db.query(Municipality).filter(Municipality.id == municipality_id).first()
    if not muni:
        raise ValueError(f"Municipality {municipality_id} not found")

    rows = (
        db.query(DataPoint, Indicator, NationalAverage)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .outerjoin(
            NationalAverage,
            and_(NationalAverage.indicator_id == Indicator.id, NationalAverage.year == year),
        )
        .filter(and_(DataPoint.municipality_id == municipality_id, DataPoint.year == year))
        .order_by(Indicator.domain, Indicator.name_he)
        .all()
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    heb = ParagraphStyle("H", parent=styles["Normal"], fontName="DavidLibre",
                         fontSize=10, leading=16, alignment=2)
    title_s = ParagraphStyle("HT", parent=heb, fontSize=16, leading=24, spaceAfter=4)
    sub_s   = ParagraphStyle("HS", parent=heb, fontSize=10, textColor=colors.HexColor("#6b7280"), spaceAfter=8)
    sec_s   = ParagraphStyle("HSec", parent=heb, fontSize=12, leading=18, spaceBefore=10, spaceAfter=4,
                              textColor=colors.HexColor("#2563eb"))

    story: list = []
    story.append(Paragraph(_heb(f"דוח רשות מקומית — {muni.name}"), title_s))
    story.append(Paragraph(
        _heb(f"שנת {year}  |  מחוז: {muni.district or 'לא ידוע'}  |  אשכול: {muni.socioeconomic_cluster or 'לא ידוע'}"),
        sub_s,
    ))
    story.append(Spacer(1, 0.4 * cm))

    # KPI tables grouped by domain
    current_domain: str | None = None
    table_data: list[list] = []

    def flush_table():
        if len(table_data) > 1:
            story.append(Paragraph(_heb(current_domain or "כללי"), sec_s))
            story.append(_make_table(table_data))
            story.append(Spacer(1, 0.25 * cm))

    for dp, ind, na in rows:
        if dp.value is None:
            continue
        if ind.domain != current_domain:
            flush_table()
            current_domain = ind.domain
            table_data = [[_heb("ממוצע ארצי"), _heb("יחידה"), _heb("ערך"), _heb("מדד")]]
        avg_str = f"{na.avg_value:,.1f}" if na and na.avg_value is not None else "—"
        table_data.append([
            _heb(avg_str),
            _heb(ind.unit or ""),
            _heb(f"{dp.value:,.2f}"),
            _heb(ind.name_he),
        ])
    flush_table()

    # Trend charts for base indicators
    story.append(Paragraph(_heb("מגמות רב-שנתיות"), sec_s))
    for code in BASE_INDICATORS:
        ts = (
            db.query(DataPoint, Indicator)
            .join(Indicator, DataPoint.indicator_id == Indicator.id)
            .filter(
                DataPoint.municipality_id == municipality_id,
                Indicator.code == code,
                DataPoint.value.isnot(None),
            )
            .order_by(DataPoint.year)
            .all()
        )
        if len(ts) < 2:
            continue
        years_l = [r.year for r, _ in ts]
        vals_l  = [r.value for r, _ in ts]
        ind_name = ts[0][1].name_he
        chart_buf = _trend_chart(years_l, vals_l, ind_name)
        story.append(Image(chart_buf, width=14 * cm, height=5.5 * cm))
        story.append(Spacer(1, 0.25 * cm))

    doc.build(story)
    return buf.getvalue()
