import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import random

from utils.data_fetch import (
    get_fred_series,
    get_market_data,
    get_multiple_etfs,
)

# --- CONFIG ---
FRED_API_KEY = "8f3c3a932886909645c3dfc413ee1488"
st.set_page_config(layout="wide")
st.markdown("# MacroStress Analyser")
st.markdown("**Visualize market reactions to macro shocks, stress test portfolios, and explore sector resilience.**")

# --- SCENARIOS ---
scenarios = {
    "Rate Hike Cycle (2015–2018)": ("2015-12-01", "2018-12-31"),
    "COVID Shock (Feb–Mar 2020)": ("2020-02-01", "2020-04-30"),
    "Inflation Spike (2021–2022)": ("2021-01-01", "2022-12-31"),
    "Bank Failures (Mar 2023)": ("2023-03-01", "2023-04-30"),
}

descriptions = {
    "Rate Hike Cycle (2015–2018)": "The Fed gradually increased rates after the 2008 crisis.",
    "COVID Shock (Feb–Mar 2020)": "A sharp selloff triggered by the global pandemic.",
    "Inflation Spike (2021–2022)": "Post-COVID demand surge and stimulus led to high inflation.",
    "Bank Failures (Mar 2023)": "Regional banks collapsed due to duration risk.",
}

tips = {
    "Rate Hike Cycle (2015–2018)": "Financials often benefit from rising rates.",
    "COVID Shock (Feb–Mar 2020)": "Tech and healthcare rebounded quickly.",
    "Inflation Spike (2021–2022)": "Energy performed well; growth stocks struggled.",
    "Bank Failures (Mar 2023)": "Tech & treasuries rallied while banks dropped.",
}

fun_facts = [
    "S&P 500 hit circuit breakers 4 times in 10 days (March 2020).",
    "Zimbabwe had 100 trillion dollar notes in 2008.",
    "In 2021, energy stocks outperformed tech.",
    "Yield curve inversions preceded every U.S. recession since 1960s.",
    "Tesla’s valuation once topped the 10 largest automakers combined."
]

# --- SIDEBAR ---
with st.sidebar:
    st.header("Scenario Settings")
    scenario = st.selectbox("Choose Macro Shock", list(scenarios.keys()))
    start_date, end_date = scenarios[scenario]

    st.markdown("### Scenario Description")
    st.info(descriptions[scenario])

    st.markdown("### Insight")
    st.success(tips[scenario])

    st.markdown("### Fun Macro Fact")
    st.info(random.choice(fun_facts))

    st.markdown("---")
    st.caption("Built by Kritika P.")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["Market Data", "Portfolio Simulation", "Sector Heatmap"])

# --- TAB 1 ---
with tab1:
    st.subheader("ETF Sector Key")
    st.markdown("""
    | ETF  | Sector       |
    |------|--------------|
    | SPY  | S&P 500 (broad market) |
    | XLK  | Technology   |
    | XLF  | Financials   |
    | XLE  | Energy       |
    | XLV  | Healthcare   |
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("S&P 500 (SPY)")
        df_spy = get_market_data("SPY", start=start_date, end=end_date)
        fig1 = px.line(df_spy, x="Date", y="Price", template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Fed Funds Rate")
        fed = get_fred_series("FEDFUNDS", api_key=FRED_API_KEY).loc[start_date:end_date].dropna().reset_index()
        fed.columns = ["Date", "Rate"]
        fig2 = px.line(fed, x="Date", y="Rate", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("CPI Inflation YoY")
        cpi = get_fred_series("CPIAUCSL", api_key=FRED_API_KEY)
        cpi = (cpi.pct_change(12)*100).loc[start_date:end_date].dropna().reset_index()
        cpi.columns = ["Date", "CPI YoY (%)"]
        fig3 = px.line(cpi, x="Date", y="CPI YoY (%)", template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Yield Curve (10Y − 3M)")
        y10 = get_fred_series("GS10", api_key=FRED_API_KEY)
        y3 = get_fred_series("DTB3", api_key=FRED_API_KEY)
        yc = pd.merge(y10, y3, left_index=True, right_index=True, how="outer")
        yc.columns = ["10Y", "3M"]
        yc["Spread"] = yc["10Y"] - yc["3M"]
        yc = yc.loc[start_date:end_date].dropna().reset_index()
        yc.columns = ["Date", "10Y", "3M", "Spread"]
        fig4 = px.line(yc, x="Date", y="Spread", template="plotly_dark")
        fig4.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig4, use_container_width=True)
        if yc["Spread"].min() < 0:
            st.warning("Yield curve inversion detected — when the curve dips below 0, it often precedes a recession.")
        else:
            st.info("The yield curve is currently positive — inversions (when spread < 0) often signal recessions.")


# --- TAB 2 ---
with tab2:
    st.subheader("Build Your Portfolio")

    etfs = ["SPY", "XLK", "XLF", "XLE", "XLV"]
    cols = st.columns(len(etfs))
    weights = {etf: cols[i].slider(etf, 0, 100, 0, 1) for i, etf in enumerate(etfs)}
    total = sum(weights.values())

    if total != 100:
        st.warning(" Weights must sum to 100%")
    else:
        selected = [etf for etf in etfs if weights[etf] > 0]
        df = get_multiple_etfs(selected, start=start_date, end=end_date)
        df = df.pivot(index="Date", columns="ETF", values="Price").fillna(method="ffill")
        df_norm = df / df.iloc[0] * 100
        alloc = np.array([weights[etf] / 100 for etf in selected])
        df_norm["Portfolio"] = df_norm[selected].dot(alloc)
        st.line_chart(df_norm["Portfolio"])

        ret = df_norm["Portfolio"].pct_change().dropna()
        total_ret = df_norm["Portfolio"].iloc[-1] - 100
        vol = ret.std() * np.sqrt(252)
        drawdown = (df_norm["Portfolio"] / df_norm["Portfolio"].cummax() - 1).min() * 100

        st.metric("Total Return (%)", f"{total_ret:.1f}")
        st.metric("Volatility (Ann.)", f"{vol:.1f}")
        st.metric("Max Drawdown (%)", f"{drawdown:.1f}")

# --- TAB 3 ---
with tab3:
    st.subheader(" Sector Heatmap")

    etf_map = {"XLK": "Technology", "XLF": "Financials", "XLE": "Energy", "XLV": "Healthcare"}
    data = {}

    for name, (s, e) in scenarios.items():
        df = get_multiple_etfs(list(etf_map.keys()), start=s, end=e).dropna()
        returns = df.groupby("ETF").apply(lambda x: (x["Price"].iloc[-1] / x["Price"].iloc[0] - 1) * 100)
        data[name] = returns.rename(index=etf_map)

    dfm = pd.DataFrame(data).T.round(1)
    dfm = dfm[dfm.mean().sort_values(ascending=False).index]
    dfm.loc["Average"] = dfm.mean()

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    sns.heatmap(dfm.T, annot=True, cmap="coolwarm", center=0, fmt=".1f",
                linewidths=0.5, cbar_kws={"label": "% Return"}, ax=ax)

    ax.set_title("Sector Performance Across Macro Shocks (%)", fontsize=14, color="white", pad=10)
    ax.set_xlabel("Scenario", color="white")
    ax.set_ylabel("Sector", color="white")
    ax.tick_params(colors="white")
    plt.xticks(rotation=45, color="white")
    plt.yticks(rotation=0, color="white")
    st.pyplot(fig)
