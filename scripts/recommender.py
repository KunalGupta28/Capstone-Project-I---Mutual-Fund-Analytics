"""
recommender.py — Simple Fund Recommendation Engine
Usage: python scripts/recommender.py --risk Low
       python scripts/recommender.py --risk Moderate
       python scripts/recommender.py --risk High
       python scripts/recommender.py  (interactive prompt)

Input:  risk appetite string (Low / Moderate / High)
Output: top 3 funds by Sharpe ratio within matching risk_grade
"""
import sys
import argparse
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RISK_MAP = {
    "low":      ["Low"],
    "moderate": ["Moderate", "Moderately High"],
    "high":     ["High", "Very High"],
}

DISPLAY_MAP = {
    "low":      "Low Risk",
    "moderate": "Moderate / Moderately High Risk",
    "high":     "High / Very High Risk",
}


def load_performance() -> pd.DataFrame:
    path = BASE_DIR / "data_sets" / "07_scheme_performance.csv"
    df = pd.read_csv(path)
    df["risk_grade_lower"] = df["risk_grade"].str.strip().str.lower()
    return df


def recommend(risk_appetite: str) -> pd.DataFrame:
    risk_key = risk_appetite.strip().lower()
    if risk_key not in RISK_MAP:
        raise ValueError(
            f"Invalid risk appetite '{risk_appetite}'. "
            f"Choose from: Low, Moderate, High"
        )

    df = load_performance()
    grades = [g.lower() for g in RISK_MAP[risk_key]]
    filtered = df[df["risk_grade_lower"].isin(grades)]

    if filtered.empty:
        print(f"⚠️  No funds found for risk grade: {risk_appetite}")
        return pd.DataFrame()

    top3 = (
        filtered.sort_values("sharpe_ratio", ascending=False)
        .head(3)[["scheme_name", "fund_house", "category",
                  "sharpe_ratio", "return_3yr_pct",
                  "max_drawdown_pct", "expense_ratio_pct", "risk_grade"]]
        .reset_index(drop=True)
    )
    top3.index += 1  # rank from 1
    return top3


def print_recommendation(risk_appetite: str):
    print("\n" + "=" * 70)
    print(f"  🏆  BLUESTOCK FUND RECOMMENDER — Risk Appetite: "
          f"{DISPLAY_MAP.get(risk_appetite.lower(), risk_appetite)}")
    print("=" * 70)

    result = recommend(risk_appetite)
    if result.empty:
        return

    pd.set_option("display.max_colwidth", 45)
    pd.set_option("display.float_format", "{:.2f}".format)
    print(result.to_string())
    print("\n" + "-" * 70)
    print("Metrics: Sharpe Ratio (higher = better risk-adjusted return)")
    print("         3-Year Return | Max Drawdown (negative = loss) | Expense Ratio")
    print("=" * 70 + "\n")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Bluestock Fund Recommender — Top 3 funds by Sharpe for a risk appetite"
    )
    parser.add_argument(
        "--risk", "-r",
        type=str,
        choices=["Low", "Moderate", "High"],
        help="Risk appetite: Low, Moderate, or High",
    )
    args = parser.parse_args()

    if args.risk:
        risk = args.risk
    else:
        print("\n  Bluestock Fund Recommender")
        print("  Risk Appetite Options: Low | Moderate | High")
        risk = input("  Enter your risk appetite: ").strip()

    try:
        print_recommendation(risk)
    except ValueError as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
