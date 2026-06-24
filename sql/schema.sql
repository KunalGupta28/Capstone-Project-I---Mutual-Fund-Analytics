-- dim_fund: from 01_fund_master.csv
CREATE TABLE IF NOT EXISTS dim_fund (
  amfi_code TEXT PRIMARY KEY,
  fund_house TEXT,
  scheme_name TEXT,
  category TEXT,
  sub_category TEXT,
  plan TEXT,
  launch_date TEXT,
  benchmark TEXT,
  expense_ratio_pct REAL,
  exit_load_pct REAL,
  min_sip_amount REAL,
  min_lumpsum_amount REAL,
  fund_manager TEXT,
  risk_category TEXT,
  sebi_category_code TEXT
);

-- dim_date: generated date dimension
CREATE TABLE IF NOT EXISTS dim_date (
  date_id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT UNIQUE,
  year INTEGER,
  month INTEGER,
  quarter INTEGER,
  day_of_week INTEGER,
  is_weekday INTEGER  -- 1 = weekday, 0 = weekend
);

-- fact_nav: from clean_nav.csv
CREATE TABLE IF NOT EXISTS fact_nav (
  nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
  amfi_code TEXT,
  date TEXT,
  nav REAL,
  daily_return_pct REAL,
  FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- fact_transactions: from clean_transactions.csv
CREATE TABLE IF NOT EXISTS fact_transactions (
  tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
  investor_id TEXT,
  transaction_date TEXT,
  amfi_code TEXT,
  transaction_type TEXT,
  amount_inr REAL,
  state TEXT,
  city TEXT,
  city_tier TEXT,
  age_group TEXT,
  gender TEXT,
  annual_income_lakh REAL,
  payment_mode TEXT,
  kyc_status TEXT,
  FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- fact_performance: from clean_performance.csv
CREATE TABLE IF NOT EXISTS fact_performance (
  perf_id INTEGER PRIMARY KEY AUTOINCREMENT,
  amfi_code TEXT,
  scheme_name TEXT,
  fund_house TEXT,
  category TEXT,
  plan TEXT,
  return_1yr_pct REAL,
  return_3yr_pct REAL,
  return_5yr_pct REAL,
  benchmark_3yr_pct REAL,
  alpha REAL,
  beta REAL,
  sharpe_ratio REAL,
  sortino_ratio REAL,
  std_dev_ann_pct REAL,
  max_drawdown_pct REAL,
  aum_crore REAL,
  expense_ratio_pct REAL,
  morningstar_rating INTEGER,
  risk_grade TEXT,
  FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- fact_aum: from 03_aum_by_fund_house.csv
CREATE TABLE IF NOT EXISTS fact_aum (
  aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT,
  fund_house TEXT,
  aum_lakh_crore REAL,
  aum_crore REAL,
  num_schemes INTEGER
);

-- fact_sip_industry: from 04_monthly_sip_inflows.csv
CREATE TABLE IF NOT EXISTS fact_sip_industry (
  sip_id INTEGER PRIMARY KEY AUTOINCREMENT,
  month TEXT,
  sip_inflow_crore REAL,
  active_sip_accounts_crore REAL,
  new_sip_accounts_lakh REAL,
  sip_aum_lakh_crore REAL,
  yoy_growth_pct REAL
);

-- fact_portfolio: from 09_portfolio_holdings.csv
CREATE TABLE IF NOT EXISTS fact_portfolio (
  holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
  amfi_code TEXT,
  stock_symbol TEXT,
  stock_name TEXT,
  sector TEXT,
  weight_pct REAL,
  market_value_cr REAL,
  current_price_inr REAL,
  portfolio_date TEXT,
  FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_fact_nav_amfi_code ON fact_nav(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_nav_date ON fact_nav(date);
CREATE INDEX IF NOT EXISTS idx_fact_tx_amfi_code ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_tx_date ON fact_transactions(transaction_date);

-- Git commit message for Day 2:
-- git add .
-- git commit -m "Day 2: Cleaned data + SQLite DB loaded"
