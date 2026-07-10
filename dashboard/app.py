import sys
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
# Set Page Config
st.set_page_config(
    page_title="Bluestock Fintech — Mutual Fund Analytics Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Append scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import config
# Custom CSS for Bluestock Branding (Fintech Blue + Emerald Green Theme)
st.markdown("""
<style>
    .reportview-container {
        background-color: #0F172A;
    }
    .sidebar .sidebar-content {
        background-color: #1E293B;
    }
    h1, h2, h3 {
        color: #F8FAFC;
        font-family: 'Outfit', sans-serif;
    }
    .metric-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-title {
        font-size: 14px;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 32px;
        color: #10B981;
        font-weight: 700;
    }
    .metric-delta {
        font-size: 12px;
        color: #38BDF8;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)
# Load data helper functions with caching
@st.cache_data
def load_industry_data():
    df_aum = pd.read_csv(config.DATA_RAW_DIR / "03_aum_by_fund_house.csv")
    df_sip = pd.read_csv(config.DATA_RAW_DIR / "04_monthly_sip_inflows.csv")
    df_cat = pd.read_csv(config.DATA_RAW_DIR / "05_category_inflows.csv")
    return df_aum, df_sip, df_cat
@st.cache_data
def load_performance_data():
    df_scorecard = pd.read_csv(config.DATA_PROCESSED_DIR / "fund_scorecard.csv")
    df_perf_raw = pd.read_csv(config.DATA_RAW_DIR / "07_scheme_performance.csv")
    df_nav = pd.read_csv(config.DATA_PROCESSED_DIR / "clean_nav.csv")
    df_bench = pd.read_csv(config.DATA_RAW_DIR / "10_benchmark_indices.csv")
    df_nav["date"] = pd.to_datetime(df_nav["date"])
    df_bench["date"] = pd.to_datetime(df_bench["date"])
    return df_scorecard, df_perf_raw, df_nav, df_bench
@st.cache_data
def load_investor_data():
    df_tx = pd.read_csv(config.DATA_PROCESSED_DIR / "clean_transactions.csv")
    df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])
    return df_tx
# Load datasets
df_aum, df_sip, df_cat = load_industry_data()
df_scorecard, df_perf_raw, df_nav, df_bench = load_performance_data()
df_tx = load_investor_data()
# ----------------- SIDEBAR NAV & LOGO -----------------
st.sidebar.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
logo_path = Path(__file__).resolve().parent / "bluestock_logo.png"
if logo_path.exists():
    st.sidebar.image(str(logo_path), width=180)
else:
    st.sidebar.title("BLUESTOCK FINTECH")
st.sidebar.markdown("</div>", unsafe_allow_html=True)
st.sidebar.markdown("---")
pages = ["Industry Overview", "Fund Performance", "Investor Analytics", "SIP & Market Trends"]
default_idx = 0
if "page" in st.query_params:
    p_param = st.query_params["page"]
    if p_param in pages:
        default_idx = pages.index(p_param)
    elif p_param.isdigit():
        p_num = int(p_param) - 1
        if 0 <= p_num < len(pages):
            default_idx = p_num
page = st.sidebar.radio(
    "Select Dashboard Page",
    pages,
    index=default_idx
)
# ----------------- PAGE 1: INDUSTRY OVERVIEW -----------------
if page == "Industry Overview":
    st.title("📈 Industry Overview Dashboard")
    st.markdown("Comprehensive overview of the Indian Mutual Fund Industry landscape.")
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Total Industry AUM</div>
            <div class="metric-value">₹81L Cr</div>
            <div class="metric-delta">As of Dec 2025</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Monthly SIP Inflow</div>
            <div class="metric-value">₹31K Cr</div>
            <div class="metric-delta">All-Time High (Dec '25)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Total Folio Count</div>
            <div class="metric-value">26.12 Cr</div>
            <div class="metric-delta">Growing Investor Base</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Total Schemes</div>
            <div class="metric-value">1,908</div>
            <div class="metric-delta">Across all AMCs</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Industry AUM Growth Trend (2022–2025)")
        # Group AUM by date
        df_aum_trend = df_aum.groupby("date")["aum_crore"].sum().reset_index()
        df_aum_trend["date"] = pd.to_datetime(df_aum_trend["date"])
        df_aum_trend = df_aum_trend.sort_values("date")
        
        fig_aum = px.line(
            df_aum_trend,
            x="date",
            y="aum_crore",
            title="Total AUM (in Rs. Crore)",
            labels={"aum_crore": "AUM (Crore)", "date": "Date"},
            color_discrete_sequence=["#10B981"]
        )
        fig_aum.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_aum, use_container_width=True)
    with col_right:
        st.subheader("Top 10 Fund Houses by AUM")
        # Get latest AUM for fund houses
        latest_date = df_aum["date"].max()
        df_latest_aum = df_aum[df_aum["date"] == latest_date].sort_values("aum_crore", ascending=False).head(10)
        
        fig_bar = px.bar(
            df_latest_aum,
            x="aum_crore",
            y="fund_house",
            orientation="h",
            title=f"AUM as of {latest_date} (in Rs. Crore)",
            labels={"aum_crore": "AUM (Crore)", "fund_house": "Fund House"},
            color="aum_crore",
            color_continuous_scale="Viridis"
        )
        fig_bar.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis={'categoryorder':'total ascending'},
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
# ----------------- PAGE 2: FUND PERFORMANCE -----------------
elif page == "Fund Performance":
    st.title("🏆 Fund Performance Analytics")
    st.markdown("Evaluate mutual fund risk-adjusted performance using custom computed metrics.")
    # Sidebar Slicers
    st.sidebar.subheader("Filters (Fund Performance)")
    available_houses = sorted(df_scorecard["fund_house"].unique())
    selected_houses = st.sidebar.multiselect("Select Fund House", available_houses, default=available_houses)
    
    # Map raw data categories for plan and category joining
    df_merged = df_scorecard.merge(df_perf_raw[["amfi_code", "std_dev_ann_pct", "aum_crore", "plan"]], on="amfi_code", how="left")
    
    available_categories = sorted(df_merged["sub_category"].dropna().unique())
    selected_categories = st.sidebar.multiselect("Select Category", available_categories, default=available_categories)
    
    available_plans = sorted(df_merged["plan"].dropna().unique())
    selected_plans = st.sidebar.multiselect("Select Plan", available_plans, default=available_plans)
    # Filtered dataframe
    df_filtered = df_merged[
        df_merged["fund_house"].isin(selected_houses) &
        df_merged["sub_category"].isin(selected_categories) &
        df_merged["plan"].isin(selected_plans)
    ]
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.subheader("Risk vs. Return Profile (3Yr CAGR vs. StdDev)")
        if not df_filtered.empty:
            fig_scatter = px.scatter(
                df_filtered,
                x="std_dev_ann_pct",
                y="cagr_3yr_pct",
                size="aum_crore",
                color="sub_category",
                hover_name="scheme_name",
                hover_data=["sharpe_ratio", "alpha", "max_drawdown_pct"],
                title="Risk (Standard Deviation) vs. Return (3Yr CAGR)",
                labels={"std_dev_ann_pct": "Annualised StdDev (Risk %)", "cagr_3yr_pct": "3Yr CAGR (Return %)"}
            )
            fig_scatter.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("No data matches selected filters.")
    with col_right:
        st.subheader("Historical NAV vs. Benchmark")
        # Let user select one of the filtered schemes
        if not df_filtered.empty:
            scheme_options = df_filtered["scheme_name"].tolist()
            selected_scheme = st.selectbox("Select Scheme for NAV Line Chart", scheme_options)
            
            amfi_code = df_filtered[df_filtered["scheme_name"] == selected_scheme]["amfi_code"].iloc[0]
            
            # Fetch scheme benchmark index
            bench_index = df_perf_raw[df_perf_raw["amfi_code"] == amfi_code]["benchmark_3yr_pct"].iloc[0]
            # Since index Close is in 10_benchmark_indices.csv, let's map index dynamically
            scheme_benchmark_name = "NIFTY100" # default
            if amfi_code in [119598, 119599, 101207, 119095, 118634]:
                scheme_benchmark_name = "NIFTY50" if amfi_code in [119598, 119599, 101207] else "NIFTY100"
            
            # Filter Nav
            df_nav_scheme = df_nav[(df_nav["amfi_code"] == amfi_code) & (df_nav["date"] <= "2026-05-29")].sort_values("date")
            df_bench_index = df_bench[(df_bench["index_name"] == scheme_benchmark_name) & (df_bench["date"] <= "2026-05-29")].sort_values("date")
            
            # Normalise to 100 at starting date
            if not df_nav_scheme.empty and not df_bench_index.empty:
                df_nav_scheme = df_nav_scheme.copy()
                df_nav_scheme["norm"] = (df_nav_scheme["nav"] / df_nav_scheme["nav"].iloc[0]) * 100
                
                df_bench_index = df_bench_index.copy()
                start_date = df_nav_scheme["date"].min()
                idx_base = df_bench_index[df_bench_index["date"] >= start_date]["close_value"].iloc[0]
                df_bench_index["norm"] = (df_bench_index["close_value"] / idx_base) * 100
                
                fig_nav = go.Figure()
                fig_nav.add_trace(go.Scatter(x=df_nav_scheme["date"], y=df_nav_scheme["norm"], name="Fund (Normalised)", line=dict(color="#10B981", width=2)))
                fig_nav.add_trace(go.Scatter(x=df_bench_index["date"], y=df_bench_index["norm"], name=f"{scheme_benchmark_name} (Normalised)", line=dict(color="#94A3B8", width=1.5, dash="dash")))
                
                fig_nav.update_layout(
                    title=f"3-Year Normalised Performance vs {scheme_benchmark_name}",
                    template="plotly_dark",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                st.plotly_chart(fig_nav, use_container_width=True)
            else:
                st.info("Performance history not available for this scheme.")
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Sortable Fund Scorecard")
    st.dataframe(
        df_filtered[["scorecard_rank", "scheme_name", "fund_house", "sub_category", "cagr_3yr_pct", "sharpe_ratio", "alpha", "expense_ratio_pct", "max_drawdown_pct", "composite_score"]],
        use_container_width=True,
        hide_index=True
    )
# ----------------- PAGE 3: INVESTOR ANALYTICS -----------------
elif page == "Investor Analytics":
    st.title("👥 Investor Analytics Dashboard")
    st.markdown("Deep dive into demographic and geographic transaction patterns.")
    # Sidebar Slicers
    st.sidebar.subheader("Filters (Investor Analytics)")
    available_states = sorted(df_tx["state"].unique())
    selected_states = st.sidebar.multiselect("Select State", available_states, default=available_states)
    
    available_age_groups = sorted(df_tx["age_group"].unique())
    selected_age_groups = st.sidebar.multiselect("Select Age Group", available_age_groups, default=available_age_groups)
    
    available_tiers = sorted(df_tx["city_tier"].unique())
    selected_tiers = st.sidebar.multiselect("Select City Tier", available_tiers, default=available_tiers)
    # Filtered transactions
    df_tx_filtered = df_tx[
        df_tx["state"].isin(selected_states) &
        df_tx["age_group"].isin(selected_age_groups) &
        df_tx["city_tier"].isin(selected_tiers)
    ]
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Transaction Amount by State")
        df_state = df_tx_filtered.groupby("state")["amount_inr"].sum().reset_index()
        fig_state = px.bar(
            df_state,
            x="amount_inr",
            y="state",
            orientation="h",
            title="Total Transaction Volume (INR) by State",
            labels={"amount_inr": "Total Amount (INR)", "state": "State"},
            color="amount_inr",
            color_continuous_scale="Viridis"
        )
        fig_state.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis={'categoryorder':'total ascending'},
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_state, use_container_width=True)
    with col_r:
        st.subheader("Transaction Type Distribution (SIP vs Lumpsum vs Redemption)")
        df_type = df_tx_filtered.groupby("transaction_type")["amount_inr"].sum().reset_index()
        fig_donut = px.pie(
            df_type,
            values="amount_inr",
            names="transaction_type",
            hole=0.4,
            title="SIP / Lumpsum / Redemption Split",
            color_discrete_sequence=["#10B981", "#3B82F6", "#EF4444"]
        )
        fig_donut.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    col_b_l, col_b_r = st.columns(2)
    with col_b_l:
        st.subheader("Average SIP Amount by Age Group")
        df_sip_age = df_tx_filtered[df_tx_filtered["transaction_type"] == "SIP"].groupby("age_group")["amount_inr"].mean().reset_index()
        fig_sip_age = px.bar(
            df_sip_age,
            x="age_group",
            y="amount_inr",
            title="Average SIP Amount (INR) by Age Group",
            labels={"amount_inr": "Avg SIP Amount", "age_group": "Age Group"},
            color_discrete_sequence=["#38BDF8"]
        )
        fig_sip_age.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_sip_age, use_container_width=True)
    with col_b_r:
        st.subheader("Monthly Transaction Volume")
        df_tx_filtered = df_tx_filtered.copy()
        df_tx_filtered["year_month"] = df_tx_filtered["transaction_date"].dt.to_period("M").astype(str)
        df_monthly = df_tx_filtered.groupby("year_month").size().reset_index(name="tx_count")
        
        fig_monthly = px.line(
            df_monthly,
            x="year_month",
            y="tx_count",
            title="Number of Transactions per Month",
            labels={"tx_count": "Transactions Count", "year_month": "Month"},
            color_discrete_sequence=["#F59E0B"]
        )
        fig_monthly.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
# ----------------- PAGE 4: SIP & MARKET TRENDS -----------------
elif page == "SIP & Market Trends":
    st.title("📊 SIP & Market Trends")
    st.markdown("Analyse market index performance side-by-side with overall industry SIP inflows.")
    # KPI Card
    df_sip = df_sip.sort_values("month")
    latest_sip_row = df_sip.iloc[-1]
    
    col_kpi1, col_kpi2 = st.columns(2)
    with col_kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active SIP Accounts</div>
            <div class="metric-value">{latest_sip_row['active_sip_accounts_crore']} Cr</div>
            <div class="metric-delta">Dec 2025</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">SIP YoY Growth</div>
            <div class="metric-value">{latest_sip_row['yoy_growth_pct']}%</div>
            <div class="metric-delta">Annual Expansion Rate</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Industry SIP Inflow (Bar) vs. Nifty 50 Close (Line)")
    
    # Process Nifty 50 monthly average close
    df_nifty = df_bench[df_bench["index_name"] == "NIFTY50"].copy()
    df_nifty["year_month"] = df_nifty["date"].dt.to_period("M").astype(str)
    df_nifty_monthly = df_nifty.groupby("year_month")["close_value"].mean().reset_index()
    
    df_sip = df_sip.copy()
    df_sip["year_month"] = df_sip["month"]
    df_merged_trends = pd.merge(df_sip, df_nifty_monthly, on="year_month", how="inner")
    
    fig_trends = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Bar for SIP Inflow
    fig_trends.add_trace(
        go.Bar(
            x=df_merged_trends["year_month"],
            y=df_merged_trends["sip_inflow_crore"],
            name="SIP Inflow (Crore)",
            marker_color="#10B981",
            opacity=0.75
        ),
        secondary_y=False
    )
    
    # Line for Nifty 50
    fig_trends.add_trace(
        go.Scatter(
            x=df_merged_trends["year_month"],
            y=df_merged_trends["close_value"],
            name="Nifty 50 Close (Avg)",
            line=dict(color="#3B82F6", width=2.5)
        ),
        secondary_y=True
    )
    
    fig_trends.update_layout(
        title="SIP Inflow vs Nifty 50 (2022-2025)",
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    fig_trends.update_yaxes(title_text="SIP Inflow (INR Crore)", secondary_y=False)
    fig_trends.update_yaxes(title_text="Nifty 50 Index Value", secondary_y=True)
    
    st.plotly_chart(fig_trends, use_container_width=True)
    col_h, col_b = st.columns(2)
    with col_h:
        st.subheader("Category Net Inflows Heatmap")
        # Heatmap of category inflows
        df_pivot_cat = df_cat.pivot(index="category", columns="month", values="net_inflow_crore").fillna(0)
        
        fig_heat = px.imshow(
            df_pivot_cat,
            labels=dict(x="Month", y="Category", color="Net Inflow (Cr)"),
            x=df_pivot_cat.columns,
            y=df_pivot_cat.index,
            title="Monthly Net Inflow by Scheme Category",
            color_continuous_scale="Viridis"
        )
        fig_heat.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    with col_b:
        st.subheader("Top 5 Categories by Net Inflow in FY25")
        # Filter for FY25: months 2024-04 to 2025-03
        fy25_months = ["2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12", "2025-01", "2025-02", "2025-03"]
        df_fy25 = df_cat[df_cat["month"].isin(fy25_months)]
        df_fy25_sum = df_fy25.groupby("category")["net_inflow_crore"].sum().reset_index()
        df_fy25_top5 = df_fy25_sum.sort_values("net_inflow_crore", ascending=False).head(5)
        
        fig_top5 = px.bar(
            df_fy25_top5,
            x="net_inflow_crore",
            y="category",
            orientation="h",
            title="Total Inflow (Crore) FY25",
            labels={"net_inflow_crore": "Total Net Inflow (Cr)", "category": "Category"},
            color="net_inflow_crore",
            color_continuous_scale="Sunsetdark"
        )
        fig_top5.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis={'categoryorder':'total ascending'},
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_top5, use_container_width=True)