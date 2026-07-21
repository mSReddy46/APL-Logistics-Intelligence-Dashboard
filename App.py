"""
APL Logistics — Customer, Product & Profitability Performance Dashboard
Author: Data Analytics Team
Description: Interactive Streamlit dashboard delivering financial clarity and
margin intelligence across customers, products, categories, markets and
discount policy for APL Logistics (KWE Group).
"""

import base64
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="APL Logistics | Profitability Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSET_DIR = Path(__file__).parent

# ----------------------------------------------------------------------------
# BRAND ASSETS (base64-embedded so the app is fully self-contained)
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_b64(filename):
    path = ASSET_DIR / filename
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode()

BANNER_B64 = load_b64("assets_banner_hd.jpg")
LOGO_B64 = load_b64("assets_logo_hd.png")

# ----------------------------------------------------------------------------
# THEME / BRAND CSS
# ----------------------------------------------------------------------------
st.markdown("""
<style>
    :root {
        --apl-blue: #0018D6;
        --apl-blue-dark: #071648;
        --apl-red: #CE0017;
        --apl-green: #1E8449;
        --apl-amber: #C67C00;
    }

    /* ---------- Hero banner ---------- */
    .apl-hero {
        position: relative;
        width: 100%;
        height: 235px;
        border-radius: 18px;
        overflow: hidden;
        margin-bottom: 1.4rem;
        box-shadow: 0 14px 34px rgba(4, 12, 60, 0.28);
        background-image: url("data:image/jpeg;base64,__BANNER__");
        background-size: cover;
        background-position: 50% 62%;
    }
    .apl-hero::before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(100deg,
            rgba(4,10,45,0.96) 0%,
            rgba(4,10,45,0.88) 26%,
            rgba(4,10,45,0.55) 52%,
            rgba(4,10,45,0.12) 78%,
            rgba(4,10,45,0.02) 100%);
    }
    .apl-hero-logo {
        position: absolute;
        top: 22px;
        left: 28px;
        height: 42px;
        border-radius: 7px;
        z-index: 2;
        box-shadow: 0 3px 12px rgba(0,0,0,0.35);
    }
    .apl-hero-text {
        position: absolute;
        left: 28px;
        bottom: 24px;
        z-index: 2;
        color: #ffffff;
        max-width: 680px;
    }
    .apl-hero-text h1 {
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.01em;
        line-height: 1.15;
        text-shadow: 0 2px 10px rgba(0,0,0,0.35);
    }
    .apl-hero-text p {
        margin: 6px 0 0 0;
        font-size: 0.95rem;
        opacity: 0.94;
        text-shadow: 0 1px 6px rgba(0,0,0,0.35);
    }
    .apl-hero-badge {
        position: absolute;
        right: 26px;
        bottom: 24px;
        z-index: 2;
        color: #ffffff;
        text-align: right;
        font-size: 0.78rem;
        opacity: 0.9;
        text-shadow: 0 1px 6px rgba(0,0,0,0.4);
    }

    /* ---------- KPI cards (global + tab-level) ---------- */
    .kpi-card {
        position: relative;
        background: color-mix(in srgb, currentColor 6%, transparent);
        border: 1px solid color-mix(in srgb, currentColor 15%, transparent);
        border-left: 4px solid var(--kpi-accent, var(--apl-blue));
        border-radius: 12px;
        padding: 16px 18px;
        text-align: left;
        cursor: default;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 26px rgba(0, 20, 120, 0.16);
    }
    .kpi-card:active {
        transform: translateY(-1px) scale(0.98);
        box-shadow: 0 5px 12px rgba(0, 20, 120, 0.14);
        transition: transform 0.05s ease;
    }
    .kpi-label {
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.045em;
        opacity: 0.65;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.76rem;
        opacity: 0.6;
        margin-top: 3px;
    }
    .kpi-status {
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        padding: 1px 8px;
        border-radius: 20px;
        margin-top: 8px;
        color: #fff;
    }

    /* ---------- Small metric chips (per-tab context rows) ---------- */
    .chip-row { display: flex; flex-wrap: wrap; gap: 10px; margin: 4px 0 18px 0; }
    .metric-chip {
        flex: 1 1 150px;
        background: color-mix(in srgb, currentColor 5%, transparent);
        border: 1px solid color-mix(in srgb, currentColor 13%, transparent);
        border-radius: 10px;
        padding: 10px 14px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        cursor: default;
    }
    .metric-chip:hover { transform: translateY(-3px); box-shadow: 0 8px 18px rgba(0,20,120,0.14); }
    .metric-chip:active { transform: translateY(0) scale(0.98); }
    .chip-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.6; }
    .chip-value { font-size: 1.15rem; font-weight: 800; margin-top: 2px; }

    /* ---------- Section titles ---------- */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 0.1rem;
        margin-bottom: 0.5rem;
        color: var(--apl-blue);
    }
    .section-sub { font-size: 0.85rem; opacity: 0.65; margin-top: -8px; margin-bottom: 10px; }

    /* ---------- Health snapshot badges (Executive Overview) ---------- */
    .health-card {
        border-radius: 14px;
        padding: 16px 18px;
        color: #fff;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        cursor: default;
        min-height: 118px;
    }
    .health-card:hover { transform: translateY(-4px); box-shadow: 0 12px 26px rgba(0,0,0,0.22); }
    .health-card:active { transform: translateY(-1px) scale(0.98); }
    .health-tag { font-size: 0.68rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.85; }
    .health-title { font-size: 1.02rem; font-weight: 800; margin: 4px 0 4px 0; }
    .health-desc { font-size: 0.82rem; opacity: 0.92; line-height: 1.3; }

    .meta-bar { font-size: 0.85rem; opacity: 0.7; padding: 2px 0 16px 0; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; }

    /* Tab label sizing */
    button[data-baseweb="tab"] { font-size: 0.95rem; }
</style>
""".replace("__BANNER__", BANNER_B64 or ""), unsafe_allow_html=True)


def status_color(status):
    return {"good": "var(--apl-green)", "watch": "var(--apl-amber)", "risk": "var(--apl-red)", "info": "var(--apl-blue)"}[status]


def kpi_card(label, value, sub, status=None, accent="var(--apl-blue)"):
    badge = ""
    if status:
        text, kind = status
        badge = f"<div class='kpi-status' style='background:{status_color(kind)}'>{text}</div>"
    st.markdown(f"""
    <div class="kpi-card" style="--kpi-accent:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
        {badge}
    </div>
    """, unsafe_allow_html=True)


def metric_chip_row(items):
    """items: list of (label, value)"""
    html = "<div class='chip-row'>"
    for label, value in items:
        html += f"""<div class="metric-chip">
            <div class="chip-label">{label}</div>
            <div class="chip-value">{value}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def section_title(text, sub=None):
    st.markdown(f"<div class='section-title'>{text}</div>", unsafe_allow_html=True)
    if sub:
        st.markdown(f"<div class='section-sub'>{sub}</div>", unsafe_allow_html=True)


def health_card(tag, title, desc, color):
    st.markdown(f"""
    <div class="health-card" style="background:{color}">
        <div class="health-tag">{tag}</div>
        <div class="health-title">{title}</div>
        <div class="health-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
DATA_PATH = ASSET_DIR / "APL_Logistics_clean.csv"

@st.cache_data(show_spinner="Loading and validating dataset...")
def load_data(path):
    df = pd.read_csv(path, encoding="utf-8")

    # --- Data Cleaning & Financial Validation ---
    df = df.dropna(subset=["Sales", "Order Profit Per Order"])
    df = df[df["Sales"] > 0]
    df["Customer Lname"] = df["Customer Lname"].fillna("Unknown")
    df["Customer Full Name"] = df["Customer Fname"].astype(str) + " " + df["Customer Lname"].astype(str)
    df["Order Item Discount Rate"] = df["Order Item Discount Rate"].clip(lower=0, upper=1)
    df["Margin %"] = np.where(df["Sales"] != 0, df["Order Profit Per Order"] / df["Sales"] * 100, 0)
    df["Is Loss"] = df["Order Profit Per Order"] < 0
    df["Order Region"] = df["Order Region"].str.strip()

    # downcast numerics to save memory
    for c in df.select_dtypes(include=["float64"]).columns:
        df[c] = pd.to_numeric(df[c], downcast="float")
    for c in ["Days for shipping (real)", "Days for shipment (scheduled)", "Late_delivery_risk",
              "Order Item Quantity", "Category Id", "Customer Id", "Department Id"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], downcast="integer")

    return df

df_raw = load_data(DATA_PATH)

# ----------------------------------------------------------------------------
# SIDEBAR — BRAND HEADER + USER CAPABILITIES / FILTERS
# ----------------------------------------------------------------------------
if LOGO_B64:
    st.sidebar.markdown(
        f"""<img src="data:image/png;base64,{LOGO_B64}" style="width:100%; border-radius:10px;
        box-shadow:0 4px 14px rgba(0,20,120,0.25); margin-bottom:6px;">""",
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown("## 🚀 APL Logistics")
st.sidebar.caption("Customer, Product & Profitability Performance Analysis")
st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")

segments = sorted(df_raw["Customer Segment"].unique().tolist())
sel_segments = st.sidebar.multiselect("Customer Segment", segments, default=segments)

markets = sorted(df_raw["Market"].unique().tolist())
sel_markets = st.sidebar.multiselect("Market", markets, default=markets)

regions = sorted(df_raw["Order Region"].unique().tolist())
sel_regions = st.sidebar.multiselect("Order Region", regions, default=regions)

categories = sorted(df_raw["Category Name"].unique().tolist())
sel_categories = st.sidebar.multiselect("Product Category", categories, default=categories)

product_options = sorted(df_raw[df_raw["Category Name"].isin(sel_categories)]["Product Name"].unique().tolist())
sel_products = st.sidebar.multiselect("Product (optional)", product_options, default=[])

min_disc, max_disc = st.sidebar.slider(
    "Discount Rate Range (%)", 0, 50, (0, 50), step=1,
    help="Filter orders by the discount rate applied to the order item."
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Filters", width="stretch"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Data source: APL Logistics order-level dataset (180K+ line items) · KWE Group")

# ----------------------------------------------------------------------------
# APPLY FILTERS
# ----------------------------------------------------------------------------
mask = (
    df_raw["Customer Segment"].isin(sel_segments)
    & df_raw["Market"].isin(sel_markets)
    & df_raw["Order Region"].isin(sel_regions)
    & df_raw["Category Name"].isin(sel_categories)
    & (df_raw["Order Item Discount Rate"] * 100 >= min_disc)
    & (df_raw["Order Item Discount Rate"] * 100 <= max_disc)
)
if sel_products:
    mask &= df_raw["Product Name"].isin(sel_products)

df = df_raw[mask].copy()

if df.empty:
    st.warning("No records match the current filter selection. Please broaden your filters.")
    st.stop()

# ----------------------------------------------------------------------------
# HERO BANNER
# ----------------------------------------------------------------------------
if BANNER_B64:
    hero_html = f"""
    <div class="apl-hero">
        {"<img class='apl-hero-logo' src='data:image/png;base64," + LOGO_B64 + "'>" if LOGO_B64 else ""}
        <div class="apl-hero-text">
            <h1>Customer, Product & Profitability Performance Dashboard</h1>
            <p>Financial clarity and margin intelligence for APL Logistics supply chain operations</p>
        </div>
        <div class="apl-hero-badge">A member of the KWE Group<br>Live Order-Level Analytics</div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
else:
    st.title("🚀 Customer, Product & Profitability Performance Dashboard")
    st.caption("Financial clarity and margin intelligence for APL Logistics supply chain operations")

pct_of_total = len(df) / len(df_raw) * 100
st.markdown(
    f"<div class='meta-bar'>Showing <b>{len(df):,}</b> of <b>{len(df_raw):,}</b> order line items "
    f"({pct_of_total:.1f}%) · <b>{df['Customer Id'].nunique():,}</b> customers · "
    f"<b>{df['Product Name'].nunique():,}</b> products · <b>{df['Category Name'].nunique():,}</b> categories</div>",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# GLOBAL KPI CORE (headline figures shown above every tab)
# ----------------------------------------------------------------------------
total_revenue = df["Sales"].sum()
total_profit = df["Order Profit Per Order"].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0
total_orders = len(df)
avg_discount = df["Order Item Discount Rate"].mean() * 100
loss_pct = df["Is Loss"].mean() * 100
late_rate = df["Late_delivery_risk"].mean() * 100
cust_value_index = df.groupby("Customer Id")["Order Profit Per Order"].sum().mean()
total_discount_given = df["Order Item Discount"].sum()
discount_impact_ratio = (total_discount_given / total_revenue * 100) if total_revenue else 0
avg_order_value = total_revenue / total_orders if total_orders else 0
profit_per_order = total_profit / total_orders if total_orders else 0
n_customers = df["Customer Id"].nunique()
orders_per_customer = total_orders / n_customers if n_customers else 0
loss_making_customers_pct = (df.groupby("Customer Id")["Order Profit Per Order"].sum() < 0).mean() * 100

core_kpis = [
    ("Total Revenue", f"${total_revenue:,.0f}", "Sum of all sales", "var(--apl-blue)", None),
    ("Total Profit", f"${total_profit:,.0f}", "Aggregate profit across orders", "var(--apl-blue)", None),
    ("Profit Margin", f"{profit_margin:.2f}%", "Profit as % of sales",
        "var(--apl-green)" if profit_margin >= 8 else "var(--apl-amber)",
        ("Healthy", "good") if profit_margin >= 8 else ("Watch", "watch")),
    ("Avg Order Value", f"${avg_order_value:,.2f}", "Revenue ÷ order line items", "var(--apl-blue)", None),
    ("Loss-Making Orders", f"{loss_pct:.1f}%", "Share of orders with negative profit",
        "var(--apl-red)" if loss_pct >= 15 else "var(--apl-amber)",
        ("Risk", "risk") if loss_pct >= 15 else ("Watch", "watch")),
    ("Late Delivery Rate", f"{late_rate:.1f}%", "Orders delivered later than scheduled",
        "var(--apl-red)" if late_rate >= 40 else "var(--apl-green)",
        ("Risk", "risk") if late_rate >= 40 else ("Healthy", "good")),
]

cols = st.columns(3)
for i, (label, value, sub, accent, status) in enumerate(core_kpis):
    with cols[i % 3]:
        kpi_card(label, value, sub, status=status, accent=accent)
    if i % 3 == 2 and i != len(core_kpis) - 1:
        cols = st.columns(3)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------------
tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "🧭 Executive Overview",
    "💰 Revenue & Profit Overview",
    "🤝 Customer Value Dashboard",
    "📦 Product & Category Performance",
    "🎯 Discount Impact Analyzer",
])

# ============================================================================
# TAB 0 — EXECUTIVE OVERVIEW
# ============================================================================
with tab0:
    section_title("Business Health Snapshot", "A leadership-level read on where the business stands right now")

    mkt_agg_x = df.groupby("Market", as_index=False).agg(
        Revenue=("Sales", "sum"), Profit=("Order Profit Per Order", "sum")
    )
    mkt_agg_x["Margin %"] = mkt_agg_x["Profit"] / mkt_agg_x["Revenue"] * 100

    cust_agg_x = df.groupby("Customer Id", as_index=False).agg(Profit=("Order Profit Per Order", "sum"))
    cust_sorted_x = cust_agg_x.sort_values("Profit", ascending=False).reset_index(drop=True)
    top20n_x = max(1, int(len(cust_sorted_x) * 0.2))
    top20_share_x = cust_sorted_x.head(top20n_x)["Profit"].sum() / cust_sorted_x["Profit"].sum() * 100

    corr_x = df["Order Item Discount Rate"].corr(df["Order Item Profit Ratio"])

    hc1, hc2, hc3, hc4 = st.columns(4)
    with hc1:
        health_card("Profitability", f"{profit_margin:.1f}% blended margin",
                     f"${total_profit:,.0f} profit on ${total_revenue:,.0f} revenue across {total_orders:,} order lines.",
                     "linear-gradient(135deg,#1E8449,#176238)")
    with hc2:
        health_card("Customer Concentration", f"Top 20% drive {top20_share_x:.0f}% of profit",
                     f"{loss_making_customers_pct:.1f}% of customers are net loss-making — retention of top accounts is critical.",
                     "linear-gradient(135deg,#C67C00,#9C6300)")
    with hc3:
        health_card("Discount Policy", f"r ≈ {corr_x:.2f} with margin",
                     "Discount depth shows negligible correlation with profit ratio — not the primary margin lever.",
                     "linear-gradient(135deg,#0018D6,#071648)")
    with hc4:
        health_card("Delivery Reliability", f"{late_rate:.1f}% delivered late",
                     "A material operational risk that does not itself reduce profitability — treat as a service-quality priority.",
                     "linear-gradient(135deg,#CE0017,#8C0010)")

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
            section_title("Revenue & Profit by Market")
            fig = go.Figure()
            fig.add_bar(x=mkt_agg_x["Market"], y=mkt_agg_x["Revenue"], name="Revenue", marker_color="#0018D6")
            fig.add_bar(x=mkt_agg_x["Market"], y=mkt_agg_x["Profit"], name="Profit", marker_color="#CE0017")
            fig.update_layout(barmode="group", height=420, legend=dict(orientation="h", y=1.12),
                               margin=dict(t=10, b=10))
            st.plotly_chart(fig, width="stretch")
        
            fig = px.pie(mkt_agg_x, names="Market", values="Profit", hole=0.55,
                         color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(height=400, margin=dict(t=10, b=10), showlegend=True)
            st.plotly_chart(fig, width="stretch")

    with st.container(border=True):
        section_title("Category Extremes — Where Margin Is Won and Lost")
        cat_agg_x = df.groupby("Category Name", as_index=False).agg(
            Revenue=("Sales", "sum"), Profit=("Order Profit Per Order", "sum")
        )
        cat_agg_x["Margin %"] = cat_agg_x["Profit"] / cat_agg_x["Revenue"] * 100
        cat_agg_x = cat_agg_x[cat_agg_x["Revenue"] > cat_agg_x["Revenue"].quantile(0.2)]
        top5 = cat_agg_x.nlargest(5, "Margin %").assign(Group="Top 5 Margin")
        bottom5 = cat_agg_x.nsmallest(5, "Margin %").assign(Group="Bottom 5 Margin")
        combo = pd.concat([top5, bottom5])
        fig = px.bar(combo.sort_values("Margin %"), x="Margin %", y="Category Name", orientation="h",
                     color="Group", color_discrete_map={"Top 5 Margin": "#1E8449", "Bottom 5 Margin": "#CE0017"})
        fig.update_layout(height=420, margin=dict(t=10, b=10), legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig, width="stretch")

    with st.container(border=True):
        section_title("Priority Actions", "Condensed from the full profitability analysis")
        pa1, pa2 = st.columns(2)
        with pa1:
            st.markdown("""
            - **Retain top-value customers** — the top 20% generate the large majority of profit; prioritize account management here.
            - **Reprice or renegotiate** the small set of high-revenue, low-margin products flagged in Product & Category Performance.
            - **Don't rely on discount caps** to protect margin — the data shows minimal impact; focus on product and customer mix instead.
            """)
        with pa2:
            best_mkt = mkt_agg_x.sort_values("Margin %", ascending=False).iloc[0]
            worst_mkt = mkt_agg_x.sort_values("Margin %", ascending=True).iloc[0]
            st.markdown(f"""
            - **Strongest market:** {best_mkt['Market']} at {best_mkt['Margin %']:.1f}% margin — study what's working.
            - **Weakest market:** {worst_mkt['Market']} at {worst_mkt['Margin %']:.1f}% margin — investigate cost/pricing structure.
            - **Fix delivery reliability** ({late_rate:.1f}% late) as a standalone service priority, independent of pricing strategy.
            """)

# ============================================================================
# TAB 1 — REVENUE & PROFIT OVERVIEW
# ============================================================================
with tab1:
    best_region = df.groupby("Order Region")["Order Profit Per Order"].sum().idxmax()
    n_markets = df["Market"].nunique()
    n_regions = df["Order Region"].nunique()
    section_title("Headline Figures", "Total sales and profit for the currently filtered selection")
    hcol1, hcol2, hcol3 = st.columns(3)
    with hcol1:
        kpi_card("Total Sales", f"${total_revenue:,.0f}", "Sum of all sales in view", accent="var(--apl-blue)")
    with hcol2:
        kpi_card("Total Profit", f"${total_profit:,.0f}", "Aggregate profit in view", accent="var(--apl-blue)")
    with hcol3:
        kpi_card("Profit Margin", f"{profit_margin:.2f}%", "Profit as % of sales",
                  status=("Healthy", "good") if profit_margin >= 8 else ("Watch", "watch"),
                  accent="var(--apl-green)" if profit_margin >= 8 else "var(--apl-amber)")

    st.markdown("<br>", unsafe_allow_html=True)

    metric_chip_row([
        ("Markets Covered", f"{n_markets}"),
        ("Order Regions", f"{n_regions}"),
        ("Top Profit Region", best_region),
        ("Profit / Order", f"${profit_per_order:,.2f}"),
    ])

    with st.container(border=True):
            section_title("Revenue vs. Profit — Market Comparison")
            mkt_agg = df.groupby("Market", as_index=False).agg(
                Revenue=("Sales", "sum"), Profit=("Order Profit Per Order", "sum")
            ).sort_values("Revenue", ascending=False)
            fig = go.Figure()
            fig.add_bar(x=mkt_agg["Market"], y=mkt_agg["Revenue"], name="Revenue", marker_color="#0018D6")
            fig.add_bar(x=mkt_agg["Market"], y=mkt_agg["Profit"], name="Profit", marker_color="#F58518")
            fig.update_layout(barmode="group", height=420, legend=dict(orientation="h", y=1.1),
                               margin=dict(t=10, b=10))
            st.plotly_chart(fig, width="stretch")

        
            mkt_agg["Margin %"] = mkt_agg["Profit"] / mkt_agg["Revenue"] * 100
            fig2 = px.bar(mkt_agg.sort_values("Margin %"), x="Margin %", y="Market", orientation="h",
                           color="Margin %", color_continuous_scale="RdYlGn", text="Margin %")
            fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig2.update_layout(height=400, margin=dict(t=10, b=10), coloraxis_showscale=False)
            st.plotly_chart(fig2, width="stretch")

    with st.container(border=True):
        section_title("Profit Margin Trend Across Regions",
                       "Regions ordered by revenue (largest → smallest) — this dataset has no order-date field, "
                       "so this reads margin trend across revenue scale rather than over time.")
        reg_agg = df.groupby("Order Region", as_index=False).agg(
            Revenue=("Sales", "sum"), Profit=("Order Profit Per Order", "sum")
        )
        reg_agg["Margin %"] = reg_agg["Profit"] / reg_agg["Revenue"] * 100
        reg_agg = reg_agg.sort_values("Revenue", ascending=False)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=reg_agg["Order Region"], y=reg_agg["Margin %"], mode="lines+markers",
            line=dict(color="#0018D6", width=3), marker=dict(size=7, color="#CE0017"),
            fill="tozeroy", fillcolor="rgba(0,24,214,0.08)",
        ))
        avg_margin_line = reg_agg["Margin %"].mean()
        fig_trend.add_hline(y=avg_margin_line, line_dash="dash", line_color="gray",
                             annotation_text=f"Avg {avg_margin_line:.1f}%", annotation_position="top left")
        fig_trend.update_layout(height=380, margin=dict(t=10, b=10), xaxis_tickangle=-45,
                                 yaxis_title="Margin %", xaxis_title="Order Region (sorted by revenue)")
        st.plotly_chart(fig_trend, width="stretch")

    with st.container(border=True):
        section_title("Regional Profit Concentration")
        fig3 = px.treemap(reg_agg, path=["Order Region"], values="Revenue", color="Margin %",
                           color_continuous_scale="RdYlGn", color_continuous_midpoint=reg_agg["Margin %"].median())
        fig3.update_layout(height=420, margin=dict(t=10, b=10))
        st.plotly_chart(fig3, width="stretch")

    with st.container(border=True):
            section_title("Order Status & Fulfillment Mix")
            status_agg = df["Order Status"].value_counts().reset_index()
            status_agg.columns = ["Order Status", "Count"]
            fig4 = px.pie(status_agg, names="Order Status", values="Count", hole=0.5)
            fig4.update_layout(height=420, margin=dict(t=10, b=10))
            st.plotly_chart(fig4, width="stretch")
        
            seg_agg = df.groupby("Customer Segment", as_index=False).agg(
                Revenue=("Sales", "sum"), Profit=("Order Profit Per Order", "sum")
            )
            seg_agg["Margin %"] = seg_agg["Profit"] / seg_agg["Revenue"] * 100
            fig5 = px.bar(seg_agg, x="Customer Segment", y=["Revenue", "Profit"], barmode="group")
            fig5.update_layout(height=400, margin=dict(t=10, b=10), legend=dict(orientation="h", y=1.15))
            st.plotly_chart(fig5, width="stretch")

# ============================================================================
# TAB 2 — CUSTOMER VALUE DASHBOARD
# ============================================================================
with tab2:
    cust_agg = df.groupby(["Customer Id", "Customer Full Name", "Customer Segment"], as_index=False).agg(
        Revenue=("Sales", "sum"), Profit=("Order Profit Per Order", "sum"), Orders=("Sales", "count")
    )
    cust_agg["Margin %"] = cust_agg["Profit"] / cust_agg["Revenue"] * 100

    metric_chip_row([
        ("Customer Value Index", f"${cust_value_index:,.0f}"),
        ("Orders / Customer", f"{orders_per_customer:.2f}"),
        ("Loss-Making Customers", f"{loss_making_customers_pct:.1f}%"),
        ("Unique Customers", f"{n_customers:,}"),
    ])

    with st.container(border=True):
        section_title("Top and Bottom Customers by Profit")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Top 10 Customers**")
            top10 = cust_agg.sort_values("Profit", ascending=False).head(10)
            fig = px.bar(top10.sort_values("Profit"), x="Profit", y="Customer Full Name", orientation="h",
                         color="Profit", color_continuous_scale="Blues", text="Profit")
            fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
            fig.update_layout(height=340, margin=dict(t=10, b=10), coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch")
            
        with c2:
            st.markdown("**Bottom 10 Customers**")
            bottom10 = cust_agg.sort_values("Profit").head(10)
            fig = px.bar(bottom10.sort_values("Profit", ascending=False), x="Profit", y="Customer Full Name",
                         orientation="h", color="Profit", color_continuous_scale="Reds_r", text="Profit")
            fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
            fig.update_layout(height=340, margin=dict(t=10, b=10), coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch")

    with st.container(border=True):
            section_title("Customer Segment Contribution")
        
            seg_prof = cust_agg.groupby("Customer Segment", as_index=False)["Profit"].sum()
            fig = px.pie(seg_prof, names="Customer Segment", values="Profit", hole=0.5)
            fig.update_layout(height=400, margin=dict(t=10, b=10))
            st.plotly_chart(fig, width="stretch")

            # Value tier segmentation via profit quartiles
            cust_agg["Value Tier"] = pd.qcut(cust_agg["Profit"], 4,
                                              labels=["Low Value", "Moderate Value", "High Value", "Premium Value"])
            tier_summary = cust_agg.groupby("Value Tier", observed=True).agg(
                Customers=("Customer Id", "count"), Total_Profit=("Profit", "sum")
            ).reset_index()
            fig = px.bar(tier_summary, x="Value Tier", y="Customers", color="Value Tier", text="Customers")
            fig.update_layout(height=400, margin=dict(t=10, b=10), showlegend=False)
            st.plotly_chart(fig, width="stretch")

    with st.container(border=True):
        section_title("Pareto Concentration — Profit Share by Customer Decile")
        cust_sorted = cust_agg.sort_values("Profit", ascending=False).reset_index(drop=True)
        cust_sorted["Cumulative Profit %"] = cust_sorted["Profit"].cumsum() / cust_sorted["Profit"].sum() * 100
        cust_sorted["Customer Rank %"] = (cust_sorted.index + 1) / len(cust_sorted) * 100
        fig = px.line(cust_sorted, x="Customer Rank %", y="Cumulative Profit %")
        fig.add_hline(y=80, line_dash="dash", line_color="gray")
        fig.add_vline(x=20, line_dash="dash", line_color="gray")
        fig.update_layout(height=380, margin=dict(t=10, b=10))
        st.plotly_chart(fig, width="stretch")

        top20_share = cust_sorted[cust_sorted["Customer Rank %"] <= 20]["Profit"].sum() / cust_sorted["Profit"].sum() * 100
        st.info(f"📌 The top 20% of customers generate **{top20_share:.1f}%** of total profit — a concentrated value base worth prioritizing for retention.")

        with st.expander("View full customer table"):
            st.dataframe(cust_agg.sort_values("Profit", ascending=False), width="stretch")

# ============================================================================
# TAB 3 — PRODUCT & CATEGORY PERFORMANCE
# ============================================================================
with tab3:
    cat_agg = df.groupby("Category Name", as_index=False).agg(
        Revenue=("Sales", "sum"), Profit=("Order Profit Per Order", "sum"), Qty=("Order Item Quantity", "sum")
    )
    cat_agg["Margin %"] = cat_agg["Profit"] / cat_agg["Revenue"] * 100
    best_cat = cat_agg.loc[cat_agg["Margin %"].idxmax()]
    worst_cat = cat_agg.loc[cat_agg["Margin %"].idxmin()]

    metric_chip_row([
        ("Active SKUs", f"{df['Product Name'].nunique():,}"),
        ("Categories", f"{df['Category Name'].nunique():,}"),
        ("Best Margin Category", f"{best_cat['Category Name']} ({best_cat['Margin %']:.1f}%)"),
        ("Weakest Margin Category", f"{worst_cat['Category Name']} ({worst_cat['Margin %']:.1f}%)"),
    ])

    with st.container(border=True):
        section_title("Category Profitability Heatmap")
        fig = px.treemap(cat_agg, path=["Category Name"], values="Revenue", color="Margin %",
                          color_continuous_scale="RdYlGn", color_continuous_midpoint=cat_agg["Margin %"].median(),
                          hover_data={"Profit": ":.0f"})
        fig.update_layout(height=460, margin=dict(t=10, b=10))
        st.plotly_chart(fig, width="stretch")

    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            section_title("Top 10 Categories by Margin %")
            top_margin = cat_agg[cat_agg["Revenue"] > cat_agg["Revenue"].quantile(0.25)].sort_values("Margin %", ascending=False).head(10)
            fig = px.bar(top_margin.sort_values("Margin %"), x="Margin %", y="Category Name", orientation="h",
                         color="Margin %", color_continuous_scale="Greens")
            fig.update_layout(height=400, margin=dict(t=10, b=10), coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch")

        with c2:
            section_title("Bottom 10 Categories by Margin %")
            low_margin = cat_agg.sort_values("Margin %").head(10)
            fig = px.bar(low_margin.sort_values("Margin %", ascending=False), x="Margin %", y="Category Name",
                         orientation="h", color="Margin %", color_continuous_scale="Reds_r")
            fig.update_layout(height=400, margin=dict(t=10, b=10), coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch")

    prod_agg = df.groupby("Product Name", as_index=False).agg(
        Revenue=("Sales", "sum"), Profit=("Order Profit Per Order", "sum"), Qty=("Order Item Quantity", "sum")
    )
    prod_agg["Margin %"] = prod_agg["Profit"] / prod_agg["Revenue"] * 100

    with st.container(border=True):
        section_title("Product-Level Margin Analysis", "Individual products ranked by margin percentage")
        p1, p2 = st.columns(2)
        with p1:
            st.markdown("**Top 10 Products by Margin %**")
            top_prod_margin = prod_agg[prod_agg["Revenue"] > prod_agg["Revenue"].quantile(0.25)].sort_values("Margin %", ascending=False).head(10)
            fig = px.bar(top_prod_margin.sort_values("Margin %"), x="Margin %", y="Product Name", orientation="h",
                         color="Margin %", color_continuous_scale="Greens")
            fig.update_layout(height=400, margin=dict(t=10, b=10), coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch")
        with p2:
            st.markdown("**Bottom 10 Products by Margin %**")
            bottom_prod_margin = prod_agg.sort_values("Margin %").head(10)
            fig = px.bar(bottom_prod_margin.sort_values("Margin %", ascending=False), x="Margin %", y="Product Name",
                         orientation="h", color="Margin %", color_continuous_scale="Reds_r")
            fig.update_layout(height=400, margin=dict(t=10, b=10), coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch")
        st.caption("Top-margin ranking excludes the bottom quartile by revenue to avoid highlighting low-volume outliers.")

    with st.container(border=True):
        section_title("High-Revenue, Low-Margin Product Detector")
        fig = px.scatter(prod_agg, x="Revenue", y="Margin %", size="Qty", color="Margin %",
                          color_continuous_scale="RdYlGn", hover_name="Product Name",
                          color_continuous_midpoint=prod_agg["Margin %"].median())
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.update_layout(height=440, margin=dict(t=10, b=10))
        st.plotly_chart(fig, width="stretch")
        st.caption("Products in the lower-right quadrant drive strong revenue but weak or negative margins — prime candidates for repricing.")

        with st.expander("View full product table"):
            st.dataframe(prod_agg.sort_values("Profit", ascending=False), width="stretch")

# ============================================================================
# TAB 4 — DISCOUNT IMPACT ANALYZER
# ============================================================================
with tab4:
    zero_disc_pct = (df["Order Item Discount Rate"] == 0).mean() * 100
    corr = df["Order Item Discount Rate"].corr(df["Order Item Profit Ratio"])

    metric_chip_row([
        ("Avg Discount Rate", f"{avg_discount:.1f}%"),
        ("Discount Impact Ratio", f"{discount_impact_ratio:.2f}%"),
        ("Orders w/ No Discount", f"{zero_disc_pct:.1f}%"),
        ("Discount ↔ Margin Corr.", f"{corr:.3f}"),
    ])

    with st.container(border=True):
        section_title("Discount Rate vs. Profit Margin")
        df["Discount Bucket"] = pd.cut(
            df["Order Item Discount Rate"] * 100,
            bins=[-0.1, 0, 10, 20, 30, 40, 50],
            labels=["0%", "0–10%", "10–20%", "20–30%", "30–40%", "40–50%"],
        )
        disc_agg = df.groupby("Discount Bucket", observed=True).agg(
            Orders=("Sales", "count"), Avg_Margin=("Margin %", "mean"), Total_Profit=("Order Profit Per Order", "sum")
        ).reset_index()

        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(disc_agg, x="Discount Bucket", y="Avg_Margin", text="Avg_Margin",
                         color="Avg_Margin", color_continuous_scale="RdYlGn")
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(height=380, margin=dict(t=10, b=10), coloraxis_showscale=False,
                               yaxis_title="Avg. Margin %")
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig = px.bar(disc_agg, x="Discount Bucket", y="Orders", text="Orders", color="Discount Bucket")
            fig.update_layout(height=380, margin=dict(t=10, b=10), showlegend=False)
            st.plotly_chart(fig, width="stretch")

        st.info(f"📌 Correlation between discount rate and profit ratio: **{corr:.3f}** — "
                f"{'discounting shows a meaningful drag on margin.' if abs(corr) > 0.15 else 'discount depth alone is not the primary driver of margin erosion at line-item level; losses concentrate in specific products and order statuses instead.'}")

    with st.container(border=True):
        section_title("Discount Depth by Category")
        cat_disc = df.groupby("Category Name", as_index=False).agg(
            Avg_Discount=("Order Item Discount Rate", "mean"), Avg_Margin=("Margin %", "mean"), Revenue=("Sales", "sum")
        )
        cat_disc["Avg_Discount"] *= 100
        fig = px.scatter(cat_disc, x="Avg_Discount", y="Avg_Margin", size="Revenue", hover_name="Category Name",
                          color="Avg_Margin", color_continuous_scale="RdYlGn")
        fig.update_layout(height=440, margin=dict(t=10, b=10), xaxis_title="Avg. Discount Rate (%)",
                           yaxis_title="Avg. Margin (%)")
        st.plotly_chart(fig, width="stretch")

    with st.container(border=True):
        section_title("What-If Discount Scenario Simulator")
        st.caption("Estimate the profit impact of adjusting the average discount rate across the currently filtered selection.")
        scenario_disc = st.slider("Simulated average discount rate (%)", 0, 50, int(avg_discount), step=1)

        baseline_discount_amt = df["Order Item Discount"].sum()
        baseline_net_of_discount_sales = df["Order Item Product Price"] * df["Order Item Quantity"]
        simulated_discount_amt = (baseline_net_of_discount_sales * (scenario_disc / 100)).sum()
        discount_delta = simulated_discount_amt - baseline_discount_amt
        simulated_profit = total_profit - discount_delta

        s1, s2, s3 = st.columns(3)
        s1.metric("Current Avg Discount", f"{avg_discount:.1f}%")
        s2.metric("Simulated Avg Discount", f"{scenario_disc}%", delta=f"{scenario_disc - avg_discount:.1f} pp")
        s3.metric("Estimated Profit Impact", f"${simulated_profit:,.0f}", delta=f"${-discount_delta:,.0f}")

        st.caption("Simulation assumes discount changes apply uniformly to gross order-item value with all other cost drivers held constant. Use as a directional estimate, not a precise forecast.")

# ============================================================================
# Footer
#============================================================================
st.markdown(f"""
<div style="text-align: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(140, 135, 175, 0.22); font-size: 12px; font-weight: 700; line-height: 1.5;">
         APL Logistics Profitability Intelligence Dashboard <span style="color: #9990CC; font-weight: 600; font-size: 12px;">[•Data reflects order-level transactional history]</span><br>
        Created by <span style="color: #55FF06; font-weight: 600; font-size: 12px; letter-spacing: 0.6px;">M SANDEEP REDDY</span>
</div>
""", unsafe_allow_html=True)