"""
monte_carlo.py — Bonus Challenge B3: Monte Carlo Simulation
Project daily returns of top 5 funds over 5 years (1260 trading days)
with uncertainty bands (5th, 50th, 95th percentiles).
Saves plot to reports/advanced_monte_carlo.png
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
PURPLE   = "#8B5CF6"
COLORS = [EMERALD, BLUE, AMBER, RED, PURPLE]


def main():
    print("Running Monte Carlo Projections...")
    # Load NAV data
    nav_path = DATA_PROCESSED_DIR / "clean_nav.csv"
    if not nav_path.exists():
        print(f"Error: {nav_path} not found. Run etl_pipeline first.")
        sys.exit(1)

    df_nav = pd.read_csv(nav_path, parse_dates=["date"])
    df_nav.sort_values(["amfi_code", "date"], inplace=True)
    df_nav["daily_return"] = df_nav.groupby("amfi_code")["nav"].pct_change()

    # Load fund master metadata for names
    perf_path = BASE_DIR / "data_sets" / "07_scheme_performance.csv"
    df_perf = pd.read_csv(perf_path)
    df_perf["amfi_code"] = df_perf["amfi_code"].astype(str)
    name_map = dict(zip(df_perf["amfi_code"], df_perf["scheme_name"]))

    # Select top 5 funds by Sharpe ratio
    top_funds = (
        df_perf.sort_values("sharpe_ratio", ascending=False)
        .head(5)["amfi_code"]
        .tolist()
    )

    n_simulations = 1000
    n_days = 1260  # 5 years * 252 trading days
    sim_results = {}

    fig, axes = plt.subplots(3, 2, figsize=(14, 12), sharex=True)
    axes = axes.flatten()

    for idx, amfi in enumerate(top_funds):
        fund_nav = df_nav[df_nav["amfi_code"] == int(amfi)].dropna(subset=["daily_return"])
        if fund_nav.empty:
            continue
        
        returns = fund_nav["daily_return"].values
        mu = np.mean(returns)
        sigma = np.std(returns)
        
        # Drift and Volatility for geometric Brownian motion
        drift = mu - (0.5 * (sigma ** 2))
        
        last_nav = fund_nav["nav"].iloc[-1]
        sim_paths = np.zeros((n_days + 1, n_simulations))
        sim_paths[0] = last_nav
        
        for t in range(1, n_days + 1):
            shocks = np.random.normal(0, 1, n_simulations)
            sim_paths[t] = sim_paths[t - 1] * np.exp(drift + sigma * shocks)
            
        p5 = np.percentile(sim_paths, 5, axis=1)
        p50 = np.percentile(sim_paths, 50, axis=1)
        p95 = np.percentile(sim_paths, 95, axis=1)
        
        fund_name = name_map.get(amfi, f"Scheme {amfi}")
        if len(fund_name) > 35:
            fund_name = fund_name[:35] + "..."
            
        ax = axes[idx]
        ax.plot(p50, label="Median (50th)", color=COLORS[idx % len(COLORS)], lw=1.5)
        ax.fill_between(range(n_days + 1), p5, p95, color=COLORS[idx % len(COLORS)], alpha=0.15, label="90% Uncertainty Band")
        ax.set_title(fund_name, fontsize=10, color=EMERALD, fontweight="bold")
        ax.grid(True)
        ax.legend(fontsize=8, loc="upper left")
        
        sim_results[amfi] = {
            "name": fund_name,
            "last_nav": last_nav,
            "median_5y": p50[-1],
            "p5_5y": p5[-1],
            "p95_5y": p95[-1],
        }

    # Remove the last unused subplot
    fig.delaxes(axes[-1])

    fig.suptitle("5-Year Mutual Fund NAV Monte Carlo Projections (1000 Simulations)",
                 fontsize=15, color=EMERALD, fontweight="bold", y=0.98)
    plt.tight_layout()
    plot_path = REPORTS_DIR / "advanced_monte_carlo.png"
    plt.savefig(plot_path, dpi=300, facecolor="#0F172A")
    plt.close()
    print(f"Saved Monte Carlo Plot: {plot_path}")

    # Save simulation summary CSV
    df_sim = pd.DataFrame.from_dict(sim_results, orient="index")
    df_sim.index.name = "amfi_code"
    csv_path = DATA_PROCESSED_DIR / "monte_carlo_projections.csv"
    df_sim.to_csv(csv_path)
    print(f"Saved Monte Carlo Summary CSV: {csv_path}")


if __name__ == "__main__":
    main()
