"""
compute_metrics.py — Standalone Performance Metrics Script
Computes CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown for all 40 funds.
Reads:  data/processed/clean_nav.csv
Writes: data/processed/{cagr_report, sharpe_values, sortino_values,
                         alpha_beta, max_drawdown, fund_scorecard}.csv
"""
import sys
import logging
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from config import DATA_PROCESSED_DIR, REPORTS_DIR, SOURCE_DATASETS_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [METRICS] %(levelname)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("METRICS")

RISK_FREE_ANNUAL = 0.065
TRADING_DAYS = 252


def load_nav() -> pd.DataFrame:
    path = DATA_PROCESSED_DIR / "clean_nav.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    df.sort_values(["amfi_code", "date"], inplace=True)
    df["daily_return"] = df.groupby("amfi_code")["nav"].pct_change()
    logger.info(f"NAV loaded: {len(df):,} rows, {df['amfi_code'].nunique()} funds")
    return df


def load_benchmark() -> pd.DataFrame:
    raw = BASE_DIR / "data" / "raw" / "10_benchmark_indices.csv"
    if not raw.exists():
        raw = BASE_DIR / "data_sets" / "10_benchmark_indices.csv"
    df = pd.read_csv(raw, parse_dates=["date"])
    nifty = df[df["index_name"] == "NIFTY100"].set_index("date")["close_value"]
    nifty_ret = nifty.pct_change().dropna()
    logger.info(f"Benchmark loaded: {len(nifty_ret):,} Nifty100 daily returns")
    return nifty_ret


def compute_cagr(nav_df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for amfi, grp in nav_df.groupby("amfi_code"):
        grp = grp.dropna(subset=["nav"]).sort_values("date")
        n_total = len(grp)
        if n_total < 2:
            continue
        
        nav_end = grp["nav"].iloc[-1]
        
        # 1-Year CAGR (252 trading days)
        if n_total >= 253:
            nav_start_1y = grp["nav"].iloc[-253]
            cagr_1yr = (nav_end / nav_start_1y) ** (252 / 252) - 1
        else:
            cagr_1yr = np.nan
            
        # 3-Year CAGR (756 trading days)
        if n_total >= 757:
            nav_start_3y = grp["nav"].iloc[-757]
            cagr_3yr = (nav_end / nav_start_3y) ** (252 / 756) - 1
        else:
            cagr_3yr = np.nan
            
        # 5-Year CAGR (1260 trading days)
        if n_total >= 1261:
            nav_start_5y = grp["nav"].iloc[-1261]
            cagr_5yr = (nav_end / nav_start_5y) ** (252 / 1260) - 1
        else:
            cagr_5yr = np.nan
            
        records.append(dict(
            amfi_code=amfi,
            cagr_1yr_pct=round(cagr_1yr * 100, 4) if not np.isnan(cagr_1yr) else np.nan,
            cagr_3yr_pct=round(cagr_3yr * 100, 4) if not np.isnan(cagr_3yr) else np.nan,
            cagr_5yr_pct=round(cagr_5yr * 100, 4) if not np.isnan(cagr_5yr) else np.nan
        ))
    return pd.DataFrame(records)


def compute_sharpe(nav_df: pd.DataFrame) -> pd.DataFrame:
    daily_rf = RISK_FREE_ANNUAL / TRADING_DAYS
    records = []
    for amfi, grp in nav_df.groupby("amfi_code"):
        ret = grp["daily_return"].dropna()
        if len(ret) < 30:
            continue
        excess = ret - daily_rf
        sharpe = (excess.mean() / ret.std()) * np.sqrt(TRADING_DAYS)
        records.append(dict(amfi_code=amfi, sharpe_ratio=round(sharpe, 6)))
    return pd.DataFrame(records)


def compute_sortino(nav_df: pd.DataFrame) -> pd.DataFrame:
    daily_rf = RISK_FREE_ANNUAL / TRADING_DAYS
    records = []
    for amfi, grp in nav_df.groupby("amfi_code"):
        ret = grp["daily_return"].dropna()
        if len(ret) < 30:
            continue
        excess = ret - daily_rf
        downside = excess[excess < 0]
        dd_std = downside.std()
        if dd_std > 0:
            sortino = (excess.mean() / dd_std) * np.sqrt(TRADING_DAYS)
        else:
            sortino = np.nan
        records.append(dict(amfi_code=amfi, sortino_ratio=round(sortino, 6)))
    return pd.DataFrame(records)


def compute_alpha_beta(nav_df: pd.DataFrame, benchmark: pd.Series) -> pd.DataFrame:
    records = []
    for amfi, grp in nav_df.groupby("amfi_code"):
        fund_ret = grp.set_index("date")["daily_return"].dropna()
        aligned = pd.concat([fund_ret, benchmark], axis=1, join="inner").dropna()
        aligned.columns = ["fund", "bench"]
        if len(aligned) < 30:
            continue
        slope, intercept, r_val, *_ = stats.linregress(aligned["bench"], aligned["fund"])
        alpha_ann = intercept * TRADING_DAYS
        records.append(dict(amfi_code=amfi,
                            beta=round(slope, 6),
                            alpha=round(alpha_ann, 6),
                            r_squared=round(r_val ** 2, 6)))
    return pd.DataFrame(records)


def compute_max_drawdown(nav_df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for amfi, grp in nav_df.groupby("amfi_code"):
        nav = grp.sort_values("date")["nav"]
        rolling_max = nav.cummax()
        drawdown = (nav - rolling_max) / rolling_max
        max_dd = drawdown.min()
        max_dd_date = grp.sort_values("date")["date"].iloc[drawdown.argmin()]
        records.append(dict(amfi_code=amfi,
                            max_drawdown_pct=round(max_dd * 100, 4),
                            max_drawdown_date=str(max_dd_date.date())))
    return pd.DataFrame(records)


def compute_scorecard(cagr_df, sharpe_df, alpha_beta_df, dd_df) -> pd.DataFrame:
    perf = pd.read_csv(SOURCE_DATASETS_DIR / "07_scheme_performance.csv")
    perf["amfi_code"] = perf["amfi_code"].astype(str)

    merged = perf[["amfi_code", "scheme_name", "fund_house", "category", "expense_ratio_pct"]].copy()

    for df, col in [(cagr_df, "cagr_3yr_pct"), (sharpe_df, "sharpe_ratio"),
                    (dd_df, "max_drawdown_pct")]:
        df["amfi_code"] = df["amfi_code"].astype(str)
        merged = merged.merge(df[["amfi_code", col]], on="amfi_code", how="left")

    if "alpha" in alpha_beta_df.columns:
        alpha_beta_df["amfi_code"] = alpha_beta_df["amfi_code"].astype(str)
        merged = merged.merge(alpha_beta_df[["amfi_code", "alpha"]], on="amfi_code", how="left")
    else:
        merged["alpha"] = np.nan

    # Composite score: 30% cagr + 25% sharpe + 20% alpha + 15% expense(inv) + 10% maxdd(inv)
    def pct_rank(s, ascending=True):
        return s.rank(pct=True, ascending=ascending, na_option="bottom") * 100

    merged["score_cagr"]    = pct_rank(merged["cagr_3yr_pct"]) * 0.30
    merged["score_sharpe"]  = pct_rank(merged["sharpe_ratio"])  * 0.25
    merged["score_alpha"]   = pct_rank(merged["alpha"])          * 0.20
    merged["score_expense"] = pct_rank(merged["expense_ratio_pct"], ascending=False) * 0.15
    merged["score_dd"]      = pct_rank(merged["max_drawdown_pct"], ascending=False)  * 0.10

    merged["composite_score"] = (merged["score_cagr"] + merged["score_sharpe"] +
                                  merged["score_alpha"] + merged["score_expense"] +
                                  merged["score_dd"]).round(2)
    merged["scorecard_rank"] = merged["composite_score"].rank(
        method="first", ascending=False).astype(int)

    cols = ["amfi_code", "scheme_name", "fund_house", "category",
            "cagr_3yr_pct", "sharpe_ratio", "alpha",
            "expense_ratio_pct", "max_drawdown_pct",
            "composite_score", "scorecard_rank"]
    return merged[cols].sort_values("scorecard_rank")


def main():
    nav_df = load_nav()
    benchmark = load_benchmark()

    logger.info("Computing CAGR...")
    cagr_df = compute_cagr(nav_df)
    cagr_df.to_csv(DATA_PROCESSED_DIR / "cagr_report.csv", index=False)
    logger.info(f"  -> cagr_report.csv ({len(cagr_df)} rows)")

    logger.info("Computing Sharpe...")
    sharpe_df = compute_sharpe(nav_df)
    sharpe_df.to_csv(DATA_PROCESSED_DIR / "sharpe_values.csv", index=False)

    logger.info("Computing Sortino...")
    sortino_df = compute_sortino(nav_df)
    sortino_df.to_csv(DATA_PROCESSED_DIR / "sortino_values.csv", index=False)

    logger.info("Computing Alpha/Beta...")
    ab_df = compute_alpha_beta(nav_df, benchmark)
    ab_df.to_csv(DATA_PROCESSED_DIR / "alpha_beta.csv", index=False)

    logger.info("Computing Max Drawdown...")
    dd_df = compute_max_drawdown(nav_df)
    dd_df.to_csv(DATA_PROCESSED_DIR / "max_drawdown.csv", index=False)

    logger.info("Building Fund Scorecard...")
    scorecard = compute_scorecard(cagr_df, sharpe_df, ab_df, dd_df)
    scorecard.to_csv(DATA_PROCESSED_DIR / "fund_scorecard.csv", index=False)
    logger.info(f"  -> fund_scorecard.csv ({len(scorecard)} funds ranked)")

    logger.info("All metrics computed successfully. [OK]")


if __name__ == "__main__":
    main()
