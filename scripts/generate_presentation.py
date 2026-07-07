"""
generate_presentation.py — Produces reports/Presentation.pptx
Uses python-pptx to create a 9-slide professional presentation.
"""
import sys
from pathlib import Path

BASE_DIR    = Path(r"c:\Users\Dell\Desktop\Internship_coding")
REPORTS_DIR = BASE_DIR / "reports"
DATA_DIR    = BASE_DIR / "data" / "processed"

try:
    import pandas as pd
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Cm
    print("python-pptx imports OK")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# ── Color Constants ───────────────────────────────────────────────────────────
C_DARK    = RGBColor(0x0F, 0x17, 0x2A)   # #0F172A
C_SLATE   = RGBColor(0x1E, 0x29, 0x3B)   # #1E293B
C_EMERALD = RGBColor(0x10, 0xB9, 0x81)   # #10B981
C_BLUE    = RGBColor(0x3B, 0x82, 0xF6)   # #3B82F6
C_AMBER   = RGBColor(0xF5, 0x9E, 0x0B)   # #F59E0B
C_RED     = RGBColor(0xEF, 0x44, 0x44)   # #EF4444
C_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
C_DIM     = RGBColor(0x94, 0xA3, 0xB8)   # #94A3B8
C_LIGHT   = RGBColor(0xE2, 0xE8, 0xF0)   # #E2E8F0

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


# ── Helpers ───────────────────────────────────────────────────────────────────
def add_rect(slide, l, t, w, h, fill_rgb, alpha=None):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(l), Inches(t), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    shape.line.fill.background()
    return shape


def add_text(slide, text, l, t, w, h, font_size=18, bold=False,
             color=C_WHITE, align=PP_ALIGN.LEFT, italic=False):
    txbox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = txbox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return txbox


def set_bg(slide, color=C_DARK):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_line(slide, l, t, w, color=C_EMERALD, thickness=Pt(2)):
    connector = slide.shapes.add_connector(
        1,  # MSO_CONNECTOR_TYPE.STRAIGHT
        Inches(l), Inches(t), Inches(l + w), Inches(t)
    )
    connector.line.color.rgb = color
    connector.line.width = thickness
    return connector


def add_bullet_box(slide, bullets, l, t, w, h, icon_color=C_EMERALD):
    from pptx.util import Pt
    txbox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = txbox.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.space_before = Pt(4)
        run_icon = p.add_run()
        run_icon.text = "▸ "
        run_icon.font.color.rgb = icon_color
        run_icon.font.size = Pt(14)
        run_icon.font.name = "Calibri"
        run = p.add_run()
        run.text = b
        run.font.color.rgb = C_LIGHT
        run.font.size = Pt(13)
        run.font.name = "Calibri"


def add_kpi_box(slide, value, label, l, t, w=1.8, h=1.4,
                val_color=C_EMERALD, bg=C_SLATE):
    add_rect(slide, l, t, w, h, bg)
    add_text(slide, value, l, t + 0.15, w, 0.7,
             font_size=24, bold=True, color=val_color, align=PP_ALIGN.CENTER)
    add_text(slide, label, l, t + 0.85, w, 0.45,
             font_size=10, color=C_DIM, align=PP_ALIGN.CENTER)


def slide_title_block(slide, title, subtitle=None):
    add_rect(slide, 0, 0, 13.33, 1.2, C_SLATE)
    add_text(slide, title, 0.5, 0.15, 12, 0.7, font_size=28, bold=True, color=C_EMERALD)
    if subtitle:
        add_text(slide, subtitle, 0.5, 0.85, 12, 0.35, font_size=13, color=C_DIM)
    # Emerald underline
    add_line(slide, 0.5, 1.15, 12.3)


# ── Slide Builders ────────────────────────────────────────────────────────────

def slide_01_cover(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_bg(slide)
    # Gradient overlay box
    add_rect(slide, 0, 0, 13.33, 7.5, C_DARK)
    add_rect(slide, 0, 0, 13.33, 3, C_SLATE)
    add_text(slide, "BLUESTOCK FINTECH",
             0.5, 0.4, 12.33, 1.0, font_size=40, bold=True, color=C_EMERALD, align=PP_ALIGN.CENTER)
    add_text(slide, "Mutual Fund Analytics — Capstone Project",
             0.5, 1.4, 12.33, 0.7, font_size=22, color=C_LIGHT, align=PP_ALIGN.CENTER)
    add_text(slide, "Final Presentation",
             0.5, 2.0, 12.33, 0.6, font_size=17, color=C_DIM, align=PP_ALIGN.CENTER, italic=True)
    add_line(slide, 2, 2.9, 9.33)
    # KPI boxes
    kpis = [("40", "Schemes Analysed", 1.2),
            ("51K+", "NAV Data Points", 3.4),
            ("32K+", "Transactions", 5.6),
            ("10", "Raw Datasets", 7.8),
            ("6", "Analysis Phases", 10.0)]
    for val, lbl, x in kpis:
        add_kpi_box(slide, val, lbl, x, 3.4, w=2.0, h=1.4)
    add_text(slide, "Prepared by: Kunal Gupta  |  July 2026",
             0.5, 5.5, 12.33, 0.5, font_size=12, color=C_DIM, align=PP_ALIGN.CENTER)
    add_text(slide, "Internship @ Bluestock Fintech  |  AI/ML Data Analytics Track",
             0.5, 5.9, 12.33, 0.5, font_size=11, color=C_DIM, align=PP_ALIGN.CENTER)


def slide_02_objective(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    slide_title_block(slide, "Project Objective & Methodology", "End-to-end MF analytics pipeline")
    add_bullet_box(slide, [
        "Build a complete data pipeline for 40 mutual fund schemes across 12 AMCs",
        "Perform EDA, performance analytics, and advanced risk metrics",
        "Develop an interactive Power BI dashboard for business stakeholders",
        "Implement a rule-based fund recommendation engine",
    ], 0.5, 1.6, 5.8, 3.5)
    phases = [("1", "ETL", C_EMERALD), ("2", "SQL DB", C_BLUE),
              ("3", "EDA", C_AMBER), ("4", "Perf.", C_RED),
              ("5", "Dashboard", C_EMERALD), ("6", "Adv. Analytics", C_BLUE)]
    for i, (num, label, col) in enumerate(phases):
        x = 7.5 + (i % 3) * 1.9
        y = 1.7 + (i // 3) * 1.8
        add_rect(slide, x, y, 1.7, 1.4, col)
        add_text(slide, num, x, y + 0.1, 1.7, 0.6, font_size=22, bold=True,
                 color=C_WHITE, align=PP_ALIGN.CENTER)
        add_text(slide, label, x, y + 0.75, 1.7, 0.5, font_size=10,
                 color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, "6-Phase Pipeline", 7.5, 1.3, 5.7, 0.4,
             font_size=13, bold=True, color=C_DIM)


def slide_03_dataset(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    slide_title_block(slide, "Dataset Summary", "10 structured CSV datasets | Synthetic, realistic data")
    datasets = [
        ("01 Fund Master", "40 schemes, AMC, category, plan type"),
        ("02 NAV History", "51,400+ daily NAV records (2020-2025)"),
        ("03 AUM by Fund House", "140 AMCs × monthly AUM data"),
        ("04 Monthly SIP Inflows", "60 months of industry SIP data"),
        ("05 Category Inflows", "Inflow by fund category per month"),
        ("06 Folio Count", "Industry folio growth (24 months)"),
        ("07 Scheme Performance", "Sharpe, Sortino, Alpha, Beta, VaR"),
        ("08 Investor Transactions", "32,780 SIP/redemption records"),
        ("09 Portfolio Holdings", "323 stock-level equity holdings"),
        ("10 Benchmark Indices", "NIFTY 50/100/SENSEX daily OHLCV"),
    ]
    for i, (name, desc) in enumerate(datasets):
        col = i // 5
        row = i % 5
        x = 0.5 + col * 6.5
        y = 1.6 + row * 1.0
        add_rect(slide, x, y, 6.0, 0.85, C_SLATE)
        add_text(slide, name, x + 0.15, y + 0.05, 2.5, 0.4,
                 font_size=11, bold=True, color=C_EMERALD)
        add_text(slide, desc, x + 0.15, y + 0.45, 5.7, 0.35,
                 font_size=10, color=C_LIGHT)


def slide_04_eda(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    slide_title_block(slide, "EDA Highlights", "15 visualizations | 10 business insights")
    insights = [
        "SIP inflows grew 3x: ₹11K Cr (Jan'23) to ₹31K Cr (Dec'25)",
        "T30 cities = 67% volume | B30 growing faster at +18% YoY",
        "36-45 age group = highest SIP investors (32% of volume)",
        "Female investors show higher SIP continuity despite lower avg amount",
        "Large Cap NAV correlation > 0.92 | Small Cap more idiosyncratic",
        "Pharma & Banking sectors dominate equity fund holdings",
        "Redemptions spike in Jan/Apr (tax planning) and Oct (corrections)",
        "UPI is now the dominant payment mode at 42% of transactions",
        "Folio count grew 18% YoY — reflecting market participation surge",
        "December is consistently the highest SIP inflow month",
    ]
    for i, insight in enumerate(insights):
        row = i % 5
        col = i // 5
        x = 0.5 + col * 6.5
        y = 1.6 + row * 1.0
        add_rect(slide, x, y, 6.0, 0.85, C_SLATE)
        add_text(slide, f"{i+1:02d}.", x + 0.1, y + 0.2, 0.6, 0.5,
                 font_size=14, bold=True, color=C_EMERALD)
        add_text(slide, insight, x + 0.7, y + 0.18, 5.2, 0.55,
                 font_size=10, color=C_LIGHT)


def slide_05_performance(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    slide_title_block(slide, "Fund Performance Analytics", "Composite scorecard | Risk-adjusted returns")
    add_kpi_box(slide, "24.6%", "Top 3yr CAGR\n(Small Cap)", 0.5, 1.6, val_color=C_EMERALD)
    add_kpi_box(slide, "0.94", "Best Sharpe\n(SBI Small Cap)", 2.5, 1.6, val_color=C_BLUE)
    add_kpi_box(slide, "1.0%", "Avg Expense\nDirect Plans", 4.5, 1.6, val_color=C_AMBER)
    add_kpi_box(slide, "94.8", "Top Composite\nScore", 6.5, 1.6, val_color=C_RED)
    add_kpi_box(slide, "5", "Metrics in\nScorecard", 8.5, 1.6, val_color=C_EMERALD)
    add_kpi_box(slide, "40", "Funds Ranked",  10.5, 1.6, val_color=C_BLUE)
    add_text(slide, "Composite Score = 30% CAGR + 25% Sharpe + 20% Alpha + 15% Expense(inv) + 10% MaxDD(inv)",
             0.5, 3.2, 12.33, 0.5, font_size=12, color=C_DIM, italic=True, align=PP_ALIGN.CENTER)
    add_bullet_box(slide, [
        "SBI Small Cap Direct is the #1 ranked fund (Composite Score: 94.8)",
        "All top-10 funds by Sharpe Ratio are either Small Cap or Flexi Cap",
        "Direct plans outperform Regular plans by 0.6-0.9% annually (expense drag)",
        "Max Drawdown range: -10% (Low Risk) to -25% (Very High Risk)",
        "Alpha > 1% for 18 out of 40 funds — indicating active management value",
    ], 0.5, 3.8, 12, 3.2)


def slide_06_risk(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    slide_title_block(slide, "Advanced Risk Metrics", "VaR, CVaR, Rolling Sharpe, HHI Concentration")
    # Rolling Sharpe chart
    chart_path = REPORTS_DIR / "rolling_sharpe_chart.png"
    if chart_path.exists():
        slide.shapes.add_picture(str(chart_path), Inches(0.5), Inches(1.5),
                                 Inches(6.5), Inches(4.5))
    add_text(slide, "Key Risk Findings", 7.5, 1.5, 5.3, 0.5,
             font_size=14, bold=True, color=C_EMERALD)
    add_bullet_box(slide, [
        "VaR 95%: Small Cap = -1.8% to -2.2% daily",
        "VaR 95%: Large Cap = -0.9% to -1.1% daily",
        "CVaR shows 40% worse loss on the worst 5% of days",
        "Rolling Sharpe peaked at 2.5+ in mid-2023 bull run",
        "38.2% of SIP investors are 'at-risk' (gap > 35 days)",
        "HHI: Concentration does NOT predict higher returns",
        "Most diversified fund: Nippon India Large Cap (HHI=0.08)",
    ], 7.5, 2.1, 5.5, 4.5)


def slide_07_dashboard(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    slide_title_block(slide, "Power BI Dashboard", "4-page interactive report | Dark slate theme")
    pages = [
        ("Page 1", "Industry Overview — AUM trend, Top AMCs, SIP inflow, Folio growth"),
        ("Page 2", "Fund Performance — Risk-return scatter, NAV trends, Scorecard"),
        ("Page 3", "Investor Behaviour — Demographics, SIP box, Geo heatmap, Cohort"),
        ("Page 4", "Benchmark Analysis — NAV vs Index, Category flows, Sector HHI"),
    ]
    for i, (pg, desc) in enumerate(pages):
        x = 0.5 + (i % 2) * 6.5
        y = 1.6 + (i // 2) * 2.5
        add_rect(slide, x, y, 6.2, 2.2, C_SLATE)
        add_text(slide, pg, x + 0.2, y + 0.15, 5.8, 0.6,
                 font_size=16, bold=True, color=C_EMERALD)
        add_text(slide, desc, x + 0.2, y + 0.75, 5.8, 1.2,
                 font_size=11, color=C_LIGHT)
    add_text(slide, "Technology: Power BI Desktop | DAX Measures | Star Schema (9 tables)",
             0.5, 7.0, 12.33, 0.4, font_size=10, color=C_DIM, align=PP_ALIGN.CENTER)


def slide_08_recommendations(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    slide_title_block(slide, "Key Recommendations", "Data-driven insights for AMCs, distributors & investors")
    recs = [
        (C_EMERALD, "For Investors",
         ["SIP investors in 2022 cohort have benefited most — stay invested through cycles",
          "Small Cap: High returns (24% CAGR) but requires 3+ year horizon & high risk tolerance",
          "Prefer Direct Plans: Save 0.7-1.0% annually over Regular Plans"]),
        (C_BLUE, "For Fund Managers / AMCs",
         ["SIP retention: 38% at-risk investors need proactive outreach programs",
          "Expense ratio reduction in Regular plans would improve competitiveness",
          "Diversified portfolios (low HHI) delivered comparable returns with less risk"]),
        (C_AMBER, "For Bluestock Fintech",
         ["Productionize the recommender API as a client-facing tool",
          "Build rolling Sharpe monitoring for real-time fund-of-funds rebalancing",
          "Use cohort analysis to power personalized investor communication"]),
    ]
    for i, (color, title, bullets) in enumerate(recs):
        x = 0.5 + i * 4.3
        add_rect(slide, x, 1.5, 4.0, 5.5, C_SLATE)
        add_rect(slide, x, 1.5, 4.0, 0.55, color)
        add_text(slide, title, x + 0.15, 1.55, 3.7, 0.45,
                 font_size=13, bold=True, color=C_WHITE)
        add_bullet_box(slide, bullets, x + 0.1, 2.2, 3.8, 4.5, icon_color=color)


def slide_09_conclusion(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_rect(slide, 0, 0, 13.33, 7.5, C_DARK)
    add_rect(slide, 0, 0, 13.33, 2.0, C_SLATE)
    add_text(slide, "Conclusion", 0.5, 0.2, 12.33, 1.0,
             font_size=36, bold=True, color=C_EMERALD, align=PP_ALIGN.CENTER)
    add_text(slide, "Bluestock Fintech | Mutual Fund Analytics Capstone",
             0.5, 1.2, 12.33, 0.6, font_size=14, color=C_DIM, align=PP_ALIGN.CENTER)
    add_line(slide, 1.5, 2.1, 10.33)
    achievements = [
        "10 raw datasets → cleaned, modelled, and loaded into SQLite",
        "15 EDA visualizations with 10 actionable business insights",
        "40 funds scored on 5 performance dimensions",
        "4-page interactive Power BI dashboard with DAX-driven metrics",
        "Advanced risk analytics: VaR, CVaR, Rolling Sharpe, HHI, Cohort, SIP Continuity",
        "Rule-based fund recommendation engine",
        "Comprehensive final report + this presentation",
    ]
    for i, a in enumerate(achievements):
        y = 2.3 + i * 0.65
        add_rect(slide, 0.5, y, 12.33, 0.55, C_SLATE)
        add_text(slide, "✓", 0.65, y + 0.07, 0.4, 0.4,
                 font_size=14, bold=True, color=C_EMERALD)
        add_text(slide, a, 1.1, y + 0.07, 11.5, 0.4,
                 font_size=12, color=C_LIGHT)
    add_text(slide, "Thank You",
             0.5, 7.0, 12.33, 0.45, font_size=14, color=C_DIM,
             align=PP_ALIGN.CENTER, italic=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def build():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_01_cover(prs)
    slide_02_objective(prs)
    slide_03_dataset(prs)
    slide_04_eda(prs)
    slide_05_performance(prs)
    slide_06_risk(prs)
    slide_07_dashboard(prs)
    slide_08_recommendations(prs)
    slide_09_conclusion(prs)

    out = REPORTS_DIR / "Presentation.pptx"
    prs.save(str(out))
    print(f"[OK] Presentation.pptx saved -> {out}")
    print(f"     Total slides: {len(prs.slides)}")
    return out


if __name__ == "__main__":
    build()
