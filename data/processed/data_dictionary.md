# Data Dictionary

This document contains the table structures and column definitions for the `bluestock_mf.db` database.

## 1. dim_fund
Source: `01_fund_master.csv`

| Column Name | Data Type | Business Definition |
| :--- | :--- | :--- |
| `amfi_code` | TEXT (PK) | Unique AMFI identifier for the mutual fund scheme |
| `fund_house` | TEXT | Name of the Asset Management Company (AMC) |
| `scheme_name` | TEXT | Full name of the mutual fund scheme |
| `category` | TEXT | Broad category of the fund (e.g., Equity, Debt) |
| `sub_category` | TEXT | Specific sub-category of the fund (e.g., Large Cap) |
| `plan` | TEXT | Direct or Regular plan type |
| `launch_date` | TEXT | Inception date of the scheme |
| `benchmark` | TEXT | Benchmark index against which the scheme is evaluated |
| `expense_ratio_pct` | REAL | Total Expense Ratio (TER) expressed as a percentage |
| `exit_load_pct` | REAL | Exit load penalty percentage for early redemption |
| `min_sip_amount` | REAL | Minimum allowable SIP investment amount (INR) |
| `min_lumpsum_amount` | REAL | Minimum allowable lumpsum investment amount (INR) |
| `fund_manager` | TEXT | Name of the fund's portfolio manager |
| `risk_category` | TEXT | Risk classification (e.g., Very High, Moderate) |
| `sebi_category_code` | TEXT | SEBI regulatory classification code |

## 2. dim_date
Source: Generated dynamically

| Column Name | Data Type | Business Definition |
| :--- | :--- | :--- |
| `date_id` | INTEGER (PK) | Auto-incremented unique date identifier |
| `date` | TEXT | Calendar date in YYYY-MM-DD format |
| `year` | INTEGER | Calendar year |
| `month` | INTEGER | Calendar month (1-12) |
| `quarter` | INTEGER | Calendar quarter (1-4) |
| `day_of_week` | INTEGER | Day of the week (0=Monday, 6=Sunday) |
| `is_weekday` | INTEGER | 1 if it is a weekday, 0 if it is a weekend |

## 3. fact_nav
Source: `clean_nav.csv` (from `02_nav_history.csv`)

| Column Name | Data Type | Business Definition |
| :--- | :--- | :--- |
| `nav_id` | INTEGER (PK) | Auto-incremented unique NAV identifier |
| `amfi_code` | TEXT (FK) | Reference to `dim_fund.amfi_code` |
| `date` | TEXT | Date of the NAV record |
| `nav` | REAL | Net Asset Value on the given date |
| `daily_return_pct` | REAL | Percentage return compared to the previous day |

## 4. fact_transactions
Source: `clean_transactions.csv` (from `08_investor_transactions.csv`)

| Column Name | Data Type | Business Definition |
| :--- | :--- | :--- |
| `tx_id` | INTEGER (PK) | Auto-incremented unique transaction identifier |
| `investor_id` | TEXT | Unique identifier for the investor |
| `transaction_date` | TEXT | Date of the transaction |
| `amfi_code` | TEXT (FK) | Reference to `dim_fund.amfi_code` |
| `transaction_type` | TEXT | SIP, Lumpsum, or Redemption |
| `amount_inr` | REAL | Value of the transaction in INR |
| `state` | TEXT | Investor's residential state |
| `city` | TEXT | Investor's residential city |
| `city_tier` | TEXT | Tier classification of the city |
| `age_group` | TEXT | Demographic age bracket of the investor |
| `gender` | TEXT | Gender of the investor |
| `annual_income_lakh` | REAL | Annual income of the investor in Lakhs |
| `payment_mode` | TEXT | Method used for payment (e.g., UPI, NetBanking) |
| `kyc_status` | TEXT | KYC verification status (Verified, Pending) |

## 5. fact_performance
Source: `clean_performance.csv` (from `07_scheme_performance.csv`)

| Column Name | Data Type | Business Definition |
| :--- | :--- | :--- |
| `perf_id` | INTEGER (PK) | Auto-incremented unique performance identifier |
| `amfi_code` | TEXT (FK) | Reference to `dim_fund.amfi_code` |
| `scheme_name` | TEXT | Full name of the mutual fund scheme |
| `fund_house` | TEXT | Name of the AMC |
| `category` | TEXT | Broad category of the fund |
| `plan` | TEXT | Direct or Regular plan type |
| `return_1yr_pct` | REAL | 1-Year trailing return percentage |
| `return_3yr_pct` | REAL | 3-Year trailing return percentage |
| `return_5yr_pct` | REAL | 5-Year trailing return percentage |
| `benchmark_3yr_pct` | REAL | Benchmark's 3-Year trailing return percentage |
| `alpha` | REAL | Alpha risk-adjusted metric |
| `beta` | REAL | Beta risk-adjusted metric |
| `sharpe_ratio` | REAL | Sharpe ratio of the fund |
| `sortino_ratio` | REAL | Sortino ratio of the fund |
| `std_dev_ann_pct` | REAL | Annualized standard deviation of returns |
| `max_drawdown_pct` | REAL | Maximum drawdown percentage over the period |
| `aum_crore` | REAL | Assets Under Management in Crores |
| `expense_ratio_pct` | REAL | Total Expense Ratio (TER) expressed as a percentage |
| `morningstar_rating` | INTEGER | Star rating assigned by Morningstar |
| `risk_grade` | TEXT | Descriptive risk grading |

## 6. fact_aum
Source: `03_aum_by_fund_house.csv`

| Column Name | Data Type | Business Definition |
| :--- | :--- | :--- |
| `aum_id` | INTEGER (PK) | Auto-incremented unique AUM identifier |
| `date` | TEXT | Reporting date or quarter |
| `fund_house` | TEXT | Name of the AMC |
| `aum_lakh_crore` | REAL | Total AUM expressed in Lakh Crores |
| `aum_crore` | REAL | Total AUM expressed in Crores |
| `num_schemes` | INTEGER | Number of active schemes managed by the AMC |

## 7. fact_sip_industry
Source: `04_monthly_sip_inflows.csv`

| Column Name | Data Type | Business Definition |
| :--- | :--- | :--- |
| `sip_id` | INTEGER (PK) | Auto-incremented unique SIP record identifier |
| `month` | TEXT | Reporting month |
| `sip_inflow_crore` | REAL | Total industry SIP inflow in Crores |
| `active_sip_accounts_crore` | REAL | Total active SIP accounts in Crores |
| `new_sip_accounts_lakh` | REAL | New SIP accounts registered in Lakhs |
| `sip_aum_lakh_crore` | REAL | Total AUM aggregated via SIPs in Lakh Crores |
| `yoy_growth_pct` | REAL | Year-over-Year growth percentage |

## 8. fact_portfolio
Source: `09_portfolio_holdings.csv`

| Column Name | Data Type | Business Definition |
| :--- | :--- | :--- |
| `holding_id` | INTEGER (PK) | Auto-incremented unique holding identifier |
| `amfi_code` | TEXT (FK) | Reference to `dim_fund.amfi_code` |
| `stock_symbol` | TEXT | Stock exchange ticker symbol |
| `stock_name` | TEXT | Full name of the underlying stock |
| `sector` | TEXT | Industrial sector of the stock |
| `weight_pct` | REAL | Portfolio allocation weight percentage |
| `market_value_cr` | REAL | Total market value held in Crores |
| `current_price_inr` | REAL | Last traded price of the stock |
| `portfolio_date` | TEXT | Date the holding was recorded |
