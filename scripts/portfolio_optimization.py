"""
portfolio_optimization.py — Bonus Challenge B4: Markowitz Efficient Frontier
Performs portfolio optimization for 5 selected top Sharpe funds.
Simulates 5000 random portfolio weights, computes Sharpe ratio, expected return,
volatility, and plots the Efficient Frontier.
Saves plot to reports/advanced_portfolio_optimization.png
"""
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from config import DATA_PROCESSED_DIR, REPORTS_DIR

plt.rcParams.update({
    "figure.facecolor": "#0F172A",
    "axes.facecolor":   "#1E293B",
    "axes.edgecolor":   "#334155",
    "axes.labelcolor":  "#E2E8F0",
    "text.color":       "#E2E8F0",
    "xtick.color":      "#94A3B8",
    "ytick.color":      "#94A3B8",
    "grid.color":       "#334155",
    "grid.alpha":       0.4,
    "legend.facecolor": "#1E293B",
    "legend.edgecolor": "#334155",
    "font.family":      "DejaVu Sans",
})

EMERALD  = "#10B981"
BLUE     = "#3B82F6"
AMBER    = "#F59E0B"
RED      = "#EF4444"
C_LIGHT  = "#E2E8F0"
C_DIM    = "#94A3B8"
TRADING_DAYS = 252
RISK_FREE_RATE = 0.065


def main():
    print("Running Markowitz Portfolio Optimization...")
    # Load NAV daily returns
    nav_path = DATA_PROCESSED_DIR / "clean_nav.csv"
    if not nav_path.exists():
        print(f"Error: {nav_path} not found. Run etl_pipeline first.")
        sys.exit(1)

    df_nav = pd.read_csv(nav_path, parse_dates=["date"])
    df_nav.sort_values(["amfi_code", "date"], inplace=True)
    df_nav["daily_return"] = df_nav.groupby("amfi_code")["nav"].pct_change()

    # Load fund metadata for names
    perf_path = BASE_DIR / "data_sets" / "07_scheme_performance.csv"
    df_perf = pd.read_csv(perf_path)
    df_perf["amfi_code"] = df_perf["amfi_code"].astype(str)
    name_map = dict(zip(df_perf["amfi_code"], df_perf["scheme_name"]))

    # Select top 5 Sharpe funds
    top_funds = (
        df_perf.sort_values("sharpe_ratio", ascending=False)
        .head(5)["amfi_code"]
        .tolist()
    )

    # Pivot returns to wide format
    returns_list = []
    fund_names = []
    for amfi in top_funds:
        name = name_map.get(amfi, f"Scheme {amfi}")
        short_name = name[:30] + "..." if len(name) > 30 else name
        fund_names.append(short_name)
        
        fund_ret = df_nav[df_nav["amfi_code"] == int(amfi)].set_index("date")["daily_return"].dropna()
        returns_list.append(fund_ret)

    df_returns = pd.concat(returns_list, axis=1, join="inner")
    df_returns.columns = fund_names

    # Compute stats
    mean_daily = df_returns.mean()
    cov_matrix = df_returns.cov()

    # Annualize stats
    expected_returns_ann = mean_daily * TRADING_DAYS
    cov_matrix_ann = cov_matrix * TRADING_DAYS

    # Monte Carlo simulation of weights
    num_portfolios = 5000
    results = np.zeros((3, num_portfolios))
    weights_record = []

    for i in range(num_portfolios):
        weights = np.random.random(len(top_funds))
        weights /= np.sum(weights)
        weights_record.append(weights)
        
        # Portfolio stats
        p_ret = np.sum(expected_returns_ann * weights)
        p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix_ann, weights)))
        p_sharpe = (p_ret - RISK_FREE_RATE) / p_vol
        
        results[0, i] = p_ret
        results[1, i] = p_vol
        results[2, i] = p_sharpe

    # Optimal Portfolios
    max_sharpe_idx = np.argmax(results[2])
    sd_max, ret_max = results[1, max_sharpe_idx], results[0, max_sharpe_idx]
    w_max = weights_record[max_sharpe_idx]

    min_vol_idx = np.argmin(results[1])
    sd_min, ret_min = results[1, min_vol_idx], results[0, min_vol_idx]
    w_min = weights_record[min_vol_idx]

    # Plot
    plt.figure(figsize=(10, 7))
    sc = plt.scatter(results[1] * 100, results[0] * 100, c=results[2], cmap="viridis", marker="o", s=10, alpha=0.3)
    plt.colorbar(sc, label="Sharpe Ratio (Rf=6.5%)")

    # Mark Max Sharpe and Min Volatility
    plt.scatter(sd_max * 100, ret_max * 100, marker="*", color=RED, s=200, label="Max Sharpe Ratio Portfolio")
    plt.scatter(sd_min * 100, ret_min * 100, marker="D", color=BLUE, s=100, label="Minimum Volatility Portfolio")

    plt.title("Markowitz Efficient Frontier (Top 5 Sharpe Ratio Funds)", fontsize=13, color=EMERALD, fontweight="bold")
    plt.xlabel("Annualized Volatility (%)", color=C_LIGHT)
    plt.ylabel("Expected Annualized Return (%)", color=C_LIGHT)
    plt.grid(True)
    plt.legend(loc="upper left")

    # Add portfolio metrics info text
    text_info = "Max Sharpe Weights:\n"
    for name, w in zip(fund_names, w_max):
        text_info += f"  • {name}: {w * 100:.1f}%\n"
    text_info += f"Expected Return: {ret_max*100:.1f}%\nVolatility: {sd_max*100:.1f}%\nSharpe: {results[2, max_sharpe_idx]:.2f}"
    
    plt.gcf().text(0.72, 0.15, text_info, fontsize=8, color=C_LIGHT, bbox=dict(facecolor="#1E293B", alpha=0.8, boxstyle="round"))

    plt.tight_layout()
    plot_path = REPORTS_DIR / "advanced_portfolio_optimization.png"
    plt.savefig(plot_path, dpi=300, facecolor="#0F172A")
    plt.close()
    print(f"Saved Portfolio Optimization Plot: {plot_path}")

    # Save stats CSV
    stats_data = {
        "portfolio": ["Max Sharpe", "Min Volatility"],
        "expected_return_pct": [ret_max * 100, ret_min * 100],
        "volatility_pct": [sd_max * 100, sd_min * 100],
        "sharpe_ratio": [results[2, max_sharpe_idx], results[2, min_vol_idx]],
    }
    for i, name in enumerate(fund_names):
        stats_data[f"weight_{name}"] = [w_max[i] * 100, w_min[i] * 100]

    df_stats = pd.DataFrame(stats_data)
    csv_path = DATA_PROCESSED_DIR / "efficient_frontier_statistics.csv"
    df_stats.to_csv(csv_path, index=False)
    print(f"Saved Portfolio Optimization Summary CSV: {csv_path}")


if __name__ == "__main__":
    main()
