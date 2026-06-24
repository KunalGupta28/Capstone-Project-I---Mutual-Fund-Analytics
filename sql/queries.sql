-- 1. Top 5 funds by AUM (from fact_performance, order by aum_crore DESC)
SELECT scheme_name, fund_house, aum_crore 
FROM fact_performance
ORDER BY aum_crore DESC 
LIMIT 5;

-- 2. Average NAV per month across all funds (from fact_nav, group by year+month)
SELECT strftime('%Y-%m', date) AS year_month, AVG(nav) AS avg_nav 
FROM fact_nav 
GROUP BY strftime('%Y-%m', date)
ORDER BY year_month;

-- 3. SIP inflow year-on-year growth (from fact_sip_industry, compare year totals)
WITH YearlyInflow AS (
  SELECT substr(month, 1, 4) AS sip_year, SUM(sip_inflow_crore) AS total_inflow
  FROM fact_sip_industry
  GROUP BY substr(month, 1, 4)
)
SELECT 
  curr.sip_year, 
  curr.total_inflow, 
  prev.total_inflow AS prev_year_inflow,
  ((curr.total_inflow - prev.total_inflow) / prev.total_inflow) * 100 AS yoy_growth_pct
FROM YearlyInflow curr
LEFT JOIN YearlyInflow prev ON CAST(curr.sip_year AS INTEGER) = CAST(prev.sip_year AS INTEGER) + 1;

-- 4. Total transaction amount by state (from fact_transactions, group by state)
SELECT state, SUM(amount_inr) AS total_transaction_amount 
FROM fact_transactions 
GROUP BY state 
ORDER BY total_transaction_amount DESC;

-- 5. Funds with expense_ratio_pct < 1% (join dim_fund and fact_performance)
SELECT d.scheme_name, d.fund_house, f.expense_ratio_pct 
FROM dim_fund d
JOIN fact_performance f ON d.amfi_code = f.amfi_code
WHERE f.expense_ratio_pct < 1.0;

-- 6. Top 5 funds by 3-year CAGR (from fact_performance, order by return_3yr_pct DESC)
SELECT scheme_name, fund_house, return_3yr_pct 
FROM fact_performance 
ORDER BY return_3yr_pct DESC 
LIMIT 5;

-- 7. Average SIP amount by age group (from fact_transactions where transaction_type = 'SIP', group by age_group)
SELECT age_group, AVG(amount_inr) AS avg_sip_amount 
FROM fact_transactions 
WHERE transaction_type = 'SIP' 
GROUP BY age_group 
ORDER BY avg_sip_amount DESC;

-- 8. AUM growth per fund house from 2022 to 2025 (from fact_aum)
WITH AUM_2022 AS (
  SELECT fund_house, AVG(aum_crore) AS avg_aum_2022
  FROM fact_aum
  WHERE date LIKE '2022-%' OR date LIKE '%-2022'
  GROUP BY fund_house
),
AUM_2025 AS (
  SELECT fund_house, AVG(aum_crore) AS avg_aum_2025
  FROM fact_aum
  WHERE date LIKE '2025-%' OR date LIKE '%-2025'
  GROUP BY fund_house
)
SELECT 
  a22.fund_house, 
  a22.avg_aum_2022, 
  a25.avg_aum_2025, 
  ((a25.avg_aum_2025 - a22.avg_aum_2022) / a22.avg_aum_2022) * 100 AS growth_pct
FROM AUM_2022 a22
JOIN AUM_2025 a25 ON a22.fund_house = a25.fund_house
ORDER BY growth_pct DESC;

-- 9. Funds with Sharpe ratio > 1 (from fact_performance)
SELECT scheme_name, fund_house, sharpe_ratio 
FROM fact_performance 
WHERE sharpe_ratio > 1.0 
ORDER BY sharpe_ratio DESC;

-- 10. Monthly transaction volume count (from fact_transactions, group by year+month)
SELECT strftime('%Y-%m', transaction_date) AS year_month, COUNT(tx_id) AS transaction_volume_count 
FROM fact_transactions 
GROUP BY strftime('%Y-%m', transaction_date)
ORDER BY year_month;

-- Git commit message for Day 2:
-- git add .
-- git commit -m "Day 2: Cleaned data + SQLite DB loaded"
