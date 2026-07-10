"""
email_report.py — Bonus Challenge B5: Weekly HTML Email Report Generator
Generates a professional fintech HTML email body summarizing the mutual fund analytics,
KPI metrics, and the top-5 performance scorecard.
Saves output to reports/weekly_summary.html
"""
import sys
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from config import DATA_PROCESSED_DIR, REPORTS_DIR


def main():
    print("Generating Weekly HTML Email Report...")
    # Load scorecard data
    scorecard_path = DATA_PROCESSED_DIR / "fund_scorecard.csv"
    if not scorecard_path.exists():
        print(f"Error: {scorecard_path} not found. Run compute_metrics first.")
        sys.exit(1)

    df_score = pd.read_csv(scorecard_path)

    # Grab Top 5 funds
    top_5 = df_score.head(5)

    # HTML Email Template
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: #0F172A;
            color: #E2E8F0;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #1E293B;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #334155;
        }}
        .header {{
            background-color: #0F172A;
            padding: 25px;
            text-align: center;
            border-bottom: 2px solid #10B981;
        }}
        .header h1 {{
            color: #10B981;
            margin: 0;
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        .header p {{
            color: #94A3B8;
            margin: 5px 0 0 0;
            font-size: 14px;
        }}
        .content {{
            padding: 25px;
        }}
        .kpi-container {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 25px;
            gap: 10px;
        }}
        .kpi-card {{
            flex: 1;
            background-color: #0F172A;
            border: 1px solid #334155;
            padding: 15px 10px;
            text-align: center;
            border-radius: 6px;
        }}
        .kpi-val {{
            font-size: 20px;
            font-weight: bold;
            color: #10B981;
            margin: 0;
        }}
        .kpi-label {{
            font-size: 10px;
            color: #94A3B8;
            margin: 5px 0 0 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        h2 {{
            color: #E2E8F0;
            font-size: 16px;
            border-left: 3px solid #10B981;
            padding-left: 10px;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 12px;
        }}
        th {{
            background-color: #0F172A;
            color: #10B981;
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid #334155;
            font-weight: bold;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #334155;
            color: #E2E8F0;
        }}
        tr:nth-child(even) td {{
            background-color: #243347;
        }}
        .footer {{
            background-color: #0F172A;
            padding: 15px;
            text-align: center;
            font-size: 11px;
            color: #94A3B8;
            border-top: 1px solid #334155;
        }}
        .btn {{
            display: inline-block;
            background-color: #10B981;
            color: #0F172A;
            text-decoration: none;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 4px;
            margin-top: 15px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>BLUESTOCK FINTECH</h1>
            <p>Mutual Fund Performance Weekly Digest</p>
        </div>
        <div class="content">
            <div class="kpi-container">
                <div class="kpi-card">
                    <p class="kpi-val">40</p>
                    <p class="kpi-label">Funds Tracked</p>
                </div>
                <div class="kpi-card">
                    <p class="kpi-val">51K+</p>
                    <p class="kpi-label">NAV Points</p>
                </div>
                <div class="kpi-card">
                    <p class="kpi-val">32K+</p>
                    <p class="kpi-label">Transactions</p>
                </div>
            </div>

            <h2>Top 5 Funds by Composite Score</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Scheme Name</th>
                        <th>3Y Return</th>
                        <th>Sharpe</th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
    """

    for _, row in top_5.iterrows():
        name = row["scheme_name"]
        if len(name) > 35:
            name = name[:35] + "..."
        html_content += f"""
                    <tr>
                        <td>{row["scorecard_rank"]}</td>
                        <td><b>{name}</b><br><span style="color:#94A3B8; font-size:10px;">{row["fund_house"]}</span></td>
                        <td>{row["cagr_3yr_pct"]:.1f}%</td>
                        <td>{row["sharpe_ratio"]:.2f}</td>
                        <td style="color:#10B981; font-weight:bold;">{row["composite_score"]:.1f}</td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>

            <h2>Market Pulse Highlights</h2>
            <p style="font-size: 13px; line-height: 1.6; margin: 0 0 10px 0;">
                The Nifty 100 benchmark remained flat this week, while Mid & Small Cap segments showed minor 0.8% gains. 
                SIP inflows have continued their strong trajectory, reflecting sustained retail participation in B30 tier cities. 
                Tail-risk analytics (VaR 95%) indicates current daily potential losses are capped at 1.85% for equity and 0.22% for debt-focused funds.
            </p>
            
            <div style="text-align: center;">
                <a href="https://github.com/KunalGupta28/Capstone-Project-I---Mutual-Fund-Analytics" class="btn">View Interactive Dashboard</a>
            </div>
        </div>
        <div class="footer">
            This is an automated performance update generated by scripts/email_report.py.<br>
            Bluestock Fintech Capstone 2026. All data simulated for educational use.
        </div>
    </div>
</body>
</html>
"""

    out_path = REPORTS_DIR / "weekly_summary.html"
    out_path.write_text(html_content, encoding="utf-8")
    print(f"Saved Weekly HTML Email Digest: {out_path}")


if __name__ == "__main__":
    main()
