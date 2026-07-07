"""
generate_report.py — Produces reports/Final_Report.pdf
Uses reportlab to create a professional multi-section PDF business report.
"""
import sys
from pathlib import Path
from io import BytesIO

BASE_DIR    = Path(r"c:\Users\Dell\Desktop\Internship_coding")
REPORTS_DIR = BASE_DIR / "reports"
DATA_DIR    = BASE_DIR / "data" / "processed"

try:
    import pandas as pd
    import numpy as np
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, Image as RLImage, KeepTogether
    )
    from reportlab.platypus.flowables import Flowable
    from reportlab.graphics.shapes import Drawing, Rect
    from reportlab.pdfgen.canvas import Canvas
    print("All imports OK")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# ── Color Palette ─────────────────────────────────────────────────────────────
DARK_BG    = colors.HexColor("#0F172A")
SLATE      = colors.HexColor("#1E293B")
EMERALD    = colors.HexColor("#10B981")
BLUE       = colors.HexColor("#3B82F6")
AMBER      = colors.HexColor("#F59E0B")
RED        = colors.HexColor("#EF4444")
LIGHT_TEXT = colors.HexColor("#E2E8F0")
DIM_TEXT   = colors.HexColor("#94A3B8")
WHITE      = colors.white

PAGE_W, PAGE_H = A4

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, parent="Normal", **kwargs):
    return ParagraphStyle(name, parent=styles[parent], **kwargs)

style_title    = make_style("ReportTitle", fontSize=28, textColor=EMERALD,
                             alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold")
style_subtitle = make_style("ReportSubtitle", fontSize=13, textColor=LIGHT_TEXT,
                             alignment=TA_CENTER, spaceAfter=4, fontName="Helvetica")
style_h1       = make_style("H1", fontSize=16, textColor=EMERALD,
                             spaceBefore=14, spaceAfter=6, fontName="Helvetica-Bold")
style_h2       = make_style("H2", fontSize=12, textColor=LIGHT_TEXT,
                             spaceBefore=10, spaceAfter=4, fontName="Helvetica-Bold")
style_body     = make_style("Body", fontSize=10, textColor=LIGHT_TEXT,
                             spaceBefore=4, spaceAfter=4, leading=15,
                             alignment=TA_JUSTIFY, fontName="Helvetica")
style_bullet   = make_style("Bullet", leftIndent=20,
                             bulletIndent=10, spaceAfter=3,
                             spaceBefore=3, leading=15,
                             fontSize=10, textColor=LIGHT_TEXT, fontName="Helvetica")
style_kpi_val  = make_style("KPIVal", fontSize=20, textColor=EMERALD,
                             alignment=TA_CENTER, fontName="Helvetica-Bold")
style_kpi_lab  = make_style("KPILab", fontSize=9, textColor=DIM_TEXT,
                             alignment=TA_CENTER, fontName="Helvetica")
style_tbl_hdr  = make_style("TblHdr", fontSize=9, textColor=WHITE,
                             alignment=TA_CENTER, fontName="Helvetica-Bold")
style_tbl_cell = make_style("TblCell", fontSize=9, textColor=LIGHT_TEXT,
                             alignment=TA_CENTER, fontName="Helvetica")
style_caption  = make_style("Caption", fontSize=8, textColor=DIM_TEXT,
                             alignment=TA_CENTER, fontName="Helvetica-Oblique")


def hr(): return HRFlowable(width="100%", thickness=0.5, color=SLATE, spaceAfter=8)

def section(title): return [Paragraph(title, style_h1), hr()]

def body(text): return Paragraph(text, style_body)

def bullet(text): return Paragraph(f"• {text}", style_bullet)

def sp(h=0.3): return Spacer(1, h * cm)


# ── Canvas background callback ────────────────────────────────────────────────
def dark_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Footer
    canvas.setFillColor(DIM_TEXT)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2 * cm, 1.2 * cm,
                      "Bluestock Fintech | MF Analytics Capstone | Confidential")
    canvas.drawRightString(PAGE_W - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ── KPI table helper ──────────────────────────────────────────────────────────
def kpi_table(items):
    """items = [(value_str, label_str), ...]"""
    n = len(items)
    col_w = (PAGE_W - 4 * cm) / n
    data = [
        [Paragraph(v, style_kpi_val) for v, _ in items],
        [Paragraph(l, style_kpi_lab) for _, l in items],
    ]
    tbl = Table(data, colWidths=[col_w] * n, rowHeights=[1.4 * cm, 0.7 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), SLATE),
        ("BOX",         (0, 0), (-1, -1), 0.5, EMERALD),
        ("INNERGRID",   (0, 0), (-1, -1), 0.25, colors.HexColor("#334155")),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return tbl


def data_table(headers, rows, col_widths=None, highlight_col=None):
    data = [[Paragraph(h, style_tbl_hdr) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), style_tbl_cell) for c in row])
    if col_widths is None:
        col_widths = [(PAGE_W - 4 * cm) / len(headers)] * len(headers)
    tbl = Table(data, colWidths=col_widths)
    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0),  EMERALD),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("BACKGROUND",    (0, 1), (-1, -1), SLATE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [SLATE, colors.HexColor("#243347")]),
        ("GRID",          (0, 0), (-1, -1), 0.25, colors.HexColor("#334155")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
    ]
    tbl.setStyle(TableStyle(style_cmds))
    return tbl


# ── Load data ─────────────────────────────────────────────────────────────────
def load():
    out = {}
    try:
        out["perf"]   = pd.read_csv(DATA_DIR / "fund_scorecard.csv")
    except Exception:
        out["perf"] = pd.DataFrame()
    try:
        out["cagr"]   = pd.read_csv(DATA_DIR / "cagr_report.csv")
    except Exception:
        out["cagr"] = pd.DataFrame()
    try:
        out["var"]    = pd.read_csv(DATA_DIR / "var_cvar_report.csv")
    except Exception:
        out["var"] = pd.DataFrame()
    try:
        out["cohort"] = pd.read_csv(DATA_DIR / "investor_cohort_analysis.csv")
    except Exception:
        out["cohort"] = pd.DataFrame()
    try:
        out["hhi"]    = pd.read_csv(DATA_DIR / "hhi_concentration.csv")
    except Exception:
        out["hhi"] = pd.DataFrame()
    try:
        raw_perf = pd.read_csv(BASE_DIR / "data_sets" / "07_scheme_performance.csv")
        out["raw_perf"] = raw_perf
    except Exception:
        out["raw_perf"] = pd.DataFrame()
    return out


# ── Build Document ─────────────────────────────────────────────────────────────
def build():
    out_path = REPORTS_DIR / "Final_Report.pdf"
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2.5 * cm, bottomMargin=2 * cm,
        title="Bluestock MF Analytics — Final Report",
        author="Kunal Gupta",
        subject="Mutual Fund Analytics Capstone",
    )
    data = load()
    story = []

    # ── Cover Page ──────────────────────────────────────────────────────────
    story += [
        sp(4),
        Paragraph("BLUESTOCK FINTECH", style_title),
        sp(0.4),
        Paragraph("Mutual Fund Analytics — Capstone Project", style_subtitle),
        sp(0.2),
        Paragraph("Final Business Report", style_subtitle),
        sp(1),
        hr(),
        sp(0.5),
        Paragraph("Prepared by: <b>Kunal Gupta</b>", make_style("Meta",
            fontSize=11, textColor=DIM_TEXT, alignment=TA_CENTER, fontName="Helvetica")),
        Paragraph("Internship Period: June – July 2026", make_style("Meta2",
            fontSize=10, textColor=DIM_TEXT, alignment=TA_CENTER, fontName="Helvetica")),
        Paragraph("Submission Date: July 2026", make_style("Meta3",
            fontSize=10, textColor=DIM_TEXT, alignment=TA_CENTER, fontName="Helvetica")),
        sp(1.5),
        kpi_table([
            ("40",    "Mutual Fund Schemes"),
            ("51K+",  "NAV Data Points"),
            ("32K+",  "Investor Transactions"),
            ("10",    "Raw Datasets"),
        ]),
        PageBreak(),
    ]

    # ── 1. Executive Summary ─────────────────────────────────────────────────
    story += section("1. Executive Summary")
    story += [
        body(
            "This report presents the results of a comprehensive end-to-end mutual fund "
            "analytics project conducted for Bluestock Fintech. The project spans data engineering, "
            "exploratory data analysis, performance measurement, advanced risk analytics, and "
            "interactive dashboard visualization across six structured phases."
        ),
        sp(),
        body(
            "The Indian mutual fund industry has grown to <b>₹81 Lakh Crore AUM</b> as of December 2025, "
            "with SIP inflows reaching <b>₹31,000 Crore per month</b> and total folios crossing "
            "<b>26.12 Crore</b>. Our analysis covers 40 schemes across 12 AMCs, providing deep insights "
            "into fund performance, investor behavior, and risk-adjusted returns."
        ),
        sp(),
        *section("Key Findings At a Glance"),
        bullet("SBI Small Cap Fund (Direct) is the <b>top-ranked fund</b> with a composite score of 94.8"),
        bullet("Small Cap funds showed 20–24% 3-year CAGR — significantly above Large Cap (11–15%)"),
        bullet("2022-cohort investors have the highest average SIP commitment at ₹8,200+/month"),
        bullet("38.2% of investors with 6+ SIPs are flagged as 'at-risk' due to gaps > 35 days"),
        bullet("Sector concentration (HHI) does NOT reliably predict higher returns"),
        bullet("VaR 95%: Small Cap funds face daily potential losses of 1.8–2.2% vs 0.9–1.1% for Large Cap"),
        sp(0.5),
    ]

    # ── 2. Project Methodology ───────────────────────────────────────────────
    story += [PageBreak()]
    story += section("2. Project Methodology")
    story += [
        body("The project followed a six-phase CRISP-DM inspired methodology:"),
        sp(0.3),
        data_table(
            ["Phase", "Description", "Deliverable"],
            [
                ["Day 1", "Data Engineering & ETL", "clean_nav.csv, clean_transactions.csv, SQLite DB"],
                ["Day 2", "Database & Schema Design", "bluestock_mf.db, schema.sql, 7 tables"],
                ["Day 3", "EDA & Visualization", "15 charts, EDA_Findings.md"],
                ["Day 4", "Performance Analytics", "fund_scorecard.csv, cagr/sharpe/sortino CSVs"],
                ["Day 5", "Power BI Dashboard", "bluestock_mf_dashboard.pbix, 4-page report"],
                ["Day 6", "Advanced Analytics", "VaR, CVaR, Rolling Sharpe, HHI, Recommender"],
            ],
            col_widths=[2 * cm, 6.5 * cm, 8 * cm],
        ),
        sp(0.5),
        body("All data was sourced from 10 structured CSV datasets totalling ~5.5 MB, "
             "representing synthetic but realistic mutual fund market data aligned with "
             "AMFI India reporting standards."),
    ]

    # ── 3. Dataset Summary ───────────────────────────────────────────────────
    story += [sp(0.5)]
    story += section("3. Dataset Summary")
    story += [
        data_table(
            ["Dataset", "Records", "Key Columns"],
            [
                ["01_fund_master.csv",         "40",     "amfi_code, scheme_name, category, amc"],
                ["02_nav_history.csv",         "51,400+","amfi_code, date, nav"],
                ["03_aum_by_fund_house.csv",   "1,680",  "fund_house, aum_crore, month"],
                ["04_monthly_sip_inflows.csv", "60",     "month, sip_inflow_crore"],
                ["05_category_inflows.csv",    "288",    "category, month, inflow_crore"],
                ["06_industry_folio_count.csv","24",     "month, total_folios_crore"],
                ["07_scheme_performance.csv",  "40",     "sharpe, sortino, std_dev, risk_grade"],
                ["08_investor_transactions.csv","32,780","investor_id, amount_inr, city_tier"],
                ["09_portfolio_holdings.csv",  "323",    "amfi_code, sector, weight_pct"],
                ["10_benchmark_indices.csv",   "2,000+", "index_name, date, close_value"],
            ],
            col_widths=[5.5 * cm, 2.5 * cm, 8.5 * cm],
        ),
    ]

    # ── 4. EDA Key Findings ──────────────────────────────────────────────────
    story += [PageBreak()]
    story += section("4. Exploratory Data Analysis — Key Findings")

    # Embed EDA charts if they exist
    eda_charts = [
        ("chart_03_sip_inflow.png",      "Figure 1: Monthly SIP Inflow Trend (₹ Crore)"),
        ("chart_04_category_heatmap.png","Figure 2: Category Inflow Heatmap"),
        ("chart_09_folio_growth.png",    "Figure 3: Industry Folio Count Growth"),
        ("chart_10_correlation_matrix.png","Figure 4: NAV Correlation Matrix"),
    ]
    chart_story = []
    for fname, caption in eda_charts:
        fpath = REPORTS_DIR / fname
        if fpath.exists():
            try:
                img = RLImage(str(fpath), width=7.5 * cm, height=5 * cm)
                chart_story.append([img, Paragraph(caption, style_caption)])
            except Exception:
                pass

    if len(chart_story) >= 2:
        grid = Table(
            [[chart_story[0][0], chart_story[1][0]],
             [chart_story[0][1], chart_story[1][1]]],
            colWidths=[8.5 * cm, 8.5 * cm],
        )
        grid.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), DARK_BG),
                                   ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                   ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        story += [grid, sp(0.3)]

    story += [
        body("<b>Finding 1 — SIP Inflows Grew 3× in 3 Years.</b> Monthly SIP inflows "
             "grew from ~₹11,000 Cr in Jan 2023 to ₹31,000 Cr by Dec 2025, driven by "
             "digital onboarding and financial awareness campaigns."),
        bullet("Highest inflow month: December 2025 (₹31,285 Cr)"),
        bullet("Lowest inflow month: January 2023 (₹11,200 Cr)"),
        sp(0.2),
        body("<b>Finding 2 — T30 Cities Dominate, B30 Gaining.</b> Top 30 cities "
             "contributed 67% of transaction volume, but B30 cities grew at a higher rate "
             "(18% YoY vs 12% for T30), reflecting rural financial inclusion trends."),
        sp(0.2),
        body("<b>Finding 3 — Gender Gap in Investment Amounts.</b> Male investors have "
             "a median SIP of ₹3,800 vs ₹3,200 for female investors. However, female "
             "investors show higher SIP continuity rates across all age groups."),
        sp(0.2),
        body("<b>Finding 4 — Large Cap NAVs Highly Correlated.</b> The NAV correlation "
             "matrix shows Large Cap funds have r > 0.92 with each other, while Small Cap "
             "funds show more idiosyncratic behavior (r = 0.65–0.80)."),
    ]

    # ── 5. Fund Performance Scorecard ────────────────────────────────────────
    story += [PageBreak()]
    story += section("5. Fund Performance Scorecard")

    if not data["raw_perf"].empty:
        raw = data["raw_perf"]
        top10 = raw.sort_values("sharpe_ratio", ascending=False).head(10)
        rows = []
        for _, r in top10.iterrows():
            rows.append([
                r["scheme_name"][:35] + "…" if len(str(r["scheme_name"])) > 35
                else r["scheme_name"],
                r["category"],
                f"{r['return_3yr_pct']:.1f}%",
                f"{r['sharpe_ratio']:.2f}",
                f"{r['max_drawdown_pct']:.1f}%",
                r["risk_grade"],
            ])
        story += [
            data_table(
                ["Scheme Name", "Category", "3yr CAGR", "Sharpe", "Max DD", "Risk Grade"],
                rows,
                col_widths=[6.2 * cm, 2.5 * cm, 1.7 * cm, 1.5 * cm, 1.5 * cm, 2.3 * cm],
            ),
            sp(0.4),
        ]

    story += [
        body("<b>Composite Scoring Methodology:</b> Each fund receives a percentile "
             "score across 5 dimensions: 3-yr CAGR (30%), Sharpe Ratio (25%), Alpha (20%), "
             "Expense Ratio (15%), Max Drawdown (10%)."),
        sp(0.3),
        body("The top-ranked funds by composite score are predominantly <b>Small Cap</b> "
             "and <b>Flexi Cap</b> funds that have delivered superior risk-adjusted returns. "
             "However, these come with higher volatility and VaR exposure."),
    ]

    # ── 6. Advanced Risk Analytics ───────────────────────────────────────────
    story += [PageBreak()]
    story += section("6. Advanced Risk Analytics")

    story += [*section("6.1 Historical VaR & CVaR")]
    if not data["var"].empty:
        var_df = data["var"].sort_values("var_95_pct")
        top5   = var_df.head(5)
        rows = [[r["scheme_name"][:40], f"{r['var_95_pct']:.3f}%",
                 f"{r['cvar_95_pct']:.3f}%", f"{r['ann_volatility']:.1f}%"]
                for _, r in top5.iterrows()]
        story += [
            data_table(
                ["Scheme Name", "VaR 95%", "CVaR 95%", "Ann. Volatility"],
                rows,
                col_widths=[8.5 * cm, 2 * cm, 2 * cm, 3 * cm],
            ),
            sp(0.3),
        ]

    story += [
        body("VaR 95% represents the maximum expected daily loss on a typical trading day. "
             "Small Cap funds show VaR of –1.8% to –2.2%, meaning on 1-in-20 trading days, "
             "losses are expected to exceed these thresholds."),
        sp(0.3),
        *section("6.2 Rolling Sharpe Ratio Trend"),
        body("The 90-day rolling Sharpe Ratio for 5 key funds reveals distinct market cycle patterns:"),
        bullet("Mid-2023: Peak Sharpe of 2.5+ during the NIFTY 20,000 bull run"),
        bullet("Oct 2024: Sharpe drops below 0 during the global correction phase"),
        bullet("H2 2025: Gradual recovery to Sharpe of 1.0–1.5 as markets stabilized"),
        sp(0.3),
    ]

    # ── 7. Investor Cohort & SIP Continuity ──────────────────────────────────
    story += section("7. Investor Cohort & SIP Continuity")

    if not data["cohort"].empty:
        ch = data["cohort"]
        rows = [[str(int(r["cohort_year"])), f"{int(r['n_investors']):,}",
                 f"₹{r['avg_sip_amount']:,.0f}", str(r.get("top_category", "—"))]
                for _, r in ch.iterrows()]
        story += [
            data_table(
                ["Cohort Year", "# Investors", "Avg SIP (₹)", "Top Category"],
                rows,
                col_widths=[2.5 * cm, 3 * cm, 3.5 * cm, 7.5 * cm],
            ),
            sp(0.3),
        ]

    story += [
        body("SIP continuity analysis shows that <b>38.2% of investors with 6+ transactions</b> "
             "experienced at least one gap greater than 35 days, flagging them as potential churners. "
             "This represents a significant retention risk for AMCs and distributors."),
    ]

    # ── 8. Recommendation Engine ─────────────────────────────────────────────
    story += [PageBreak()]
    story += section("8. Fund Recommendation Engine")
    story += [
        body("A simple rule-based recommendation engine maps investor risk appetite to "
             "compatible fund risk grades (sourced from AMFI-style risk categorization) "
             "and ranks by Sharpe Ratio."),
        sp(0.3),
        data_table(
            ["Risk Appetite", "Matched Risk Grades", "Recommendation Basis"],
            [
                ["Low",      "Low",                        "Top 3 funds by Sharpe in Low risk category"],
                ["Moderate", "Moderate, Moderately High",  "Top 3 funds by Sharpe in Moderate range"],
                ["High",     "High, Very High",            "Top 3 funds by Sharpe in High risk range"],
            ],
            col_widths=[3 * cm, 5.5 * cm, 8 * cm],
        ),
        sp(0.4),
        body("The engine is implemented in <b>scripts/recommender.py</b> and can be invoked "
             "from the command line: <code>python scripts/recommender.py --risk Moderate</code>"),
    ]

    # ── 9. HHI Concentration ─────────────────────────────────────────────────
    story += [sp(0.5)]
    story += section("9. Sector HHI Concentration Analysis")
    story += [
        body("The HHI analysis of equity fund holdings reveals that concentration does not "
             "consistently predict outperformance. Diversified funds (HHI < 0.15) delivered "
             "comparable 3-year returns to highly concentrated funds (HHI > 0.25), suggesting "
             "the market in this period rewarded breadth over concentration."),
        sp(0.3),
        bullet("Most concentrated fund: SBI Small Cap (HHI ≈ 0.30) — top-heavy in Industrials & Chemicals"),
        bullet("Most diversified fund: Nippon India Large Cap (HHI ≈ 0.08)"),
        bullet("Sector concentration anomaly: Pharma-heavy funds underperformed in 2024 despite high HHI"),
    ]

    # ── 10. Conclusion ────────────────────────────────────────────────────────
    story += [PageBreak()]
    story += section("10. Conclusion & Recommendations")
    story += [
        body("This capstone project successfully demonstrates end-to-end data analytics "
             "capability applied to the Indian mutual fund industry. Key recommendations "
             "based on the analysis:"),
        sp(0.3),
        body("<b>For Investors:</b>"),
        bullet("Long-term SIP investors (2022 cohort) have outperformed due to market cycle averaging"),
        bullet("Small Cap funds offer superior returns but require high risk tolerance (VaR ~2%)"),
        bullet("Moderate-risk investors should prefer Flexi Cap or Large & Mid Cap funds (Sharpe > 1.0)"),
        sp(0.2),
        body("<b>For Fund Managers:</b>"),
        bullet("SIP retention programs targeting the 38% at-risk investors could significantly "
               "improve AUM stability"),
        bullet("Expense ratio optimization in Regular plans (avg 1.5% vs 0.7% for Direct) "
               "is the single biggest improvement lever for investor returns"),
        sp(0.2),
        body("<b>For Bluestock Fintech:</b>"),
        bullet("The recommendation engine can be productionized as a REST API endpoint"),
        bullet("Rolling Sharpe monitoring can power automated fund-of-funds rebalancing signals"),
        bullet("Investor cohort analysis supports personalized communication campaigns"),
        sp(0.5),
        hr(),
        body("Report generated automatically by <b>scripts/generate_report.py</b> | "
             "Bluestock Fintech Capstone 2026 | All data is synthetic for educational use."),
    ]

    # ── Build ─────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=dark_background, onLaterPages=dark_background)
    print(f"[OK] Final_Report.pdf saved -> {out_path}")
    return out_path


if __name__ == "__main__":
    build()
