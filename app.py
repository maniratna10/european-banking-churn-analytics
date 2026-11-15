
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="European Bank | Customer Retention", page_icon="🏦", layout="wide")

# A restrained, report-style interface rather than a template-heavy dashboard.
st.markdown("""
<style>
    .stApp {background: #101820; color: #edf2f4;}
    [data-testid="stSidebar"] {background: #17232e;}
    [data-testid="stMetric"] {background: #1a2935; border: 1px solid #2d414f; padding: 14px; border-radius: 8px;}
    [data-testid="stMetricValue"] {color: #f4f7f9;}
    h1, h2, h3 {color: #f4f7f9;}
    .eyebrow {color:#8da5b5; letter-spacing:1.5px; font-size:11px; font-weight:700;}
    .intro {color:#b8c6cf; font-size:15px;}
    .note {background:#172630; border-left:3px solid #5c9ead; padding:12px 15px; border-radius:4px; color:#c7d3da;}
    div[data-testid="stDataFrame"] {border:1px solid #2d414f; border-radius:8px;}
</style>
""", unsafe_allow_html=True)

DATA_PATH = Path(__file__).parent / "data" / "european_bank.csv"
if not DATA_PATH.exists():
    DATA_PATH = Path("data/european_bank.csv")

@st.cache_data
def load_data():
    frame = pd.read_csv(DATA_PATH)
    frame["Exited"] = pd.to_numeric(frame["Exited"], errors="coerce").fillna(0).astype(int)
    frame["AgeGroup"] = pd.cut(frame["Age"], [0, 29, 45, 59, 120],
        labels=["Under 30", "30–45", "46–59", "60+"], include_lowest=True)
    frame["TenureGroup"] = pd.cut(frame["Tenure"], [-1, 3, 7, 10],
        labels=["New (0–3 years)", "Mid-term (4–7 years)", "Long-term (8–10 years)"])
    # Tertiles are calculated from this dataset so the credit bands remain balanced.
    frame["CreditBand"] = pd.qcut(frame["CreditScore"], 3, labels=["Low", "Medium", "High"])
    positive_balances = frame.loc[frame["Balance"] > 0, "Balance"]
    balance_midpoint = positive_balances.median()
    frame["BalanceSegment"] = np.select(
        [frame["Balance"].eq(0), frame["Balance"].lt(balance_midpoint)],
        ["Zero balance", "Low balance"], default="High balance")
    premium_cutoff = positive_balances.quantile(.75)
    frame["ValueSegment"] = np.where(frame["Balance"] >= premium_cutoff, "High-value balance", "Other customers")
    return frame, float(balance_midpoint), float(premium_cutoff)

df, balance_midpoint, premium_cutoff = load_data()
def rate(frame):
    return float(frame["Exited"].mean()) if len(frame) else 0.0
def fmt_pct(x):
    return f"{x:.1%}"
def segment_summary(frame, field):
    out = frame.groupby(field, observed=True).agg(Customers=("Exited","size"), Churned=("Exited","sum"), Churn_Rate=("Exited","mean")).reset_index()
    out["Churn_Rate"] = out["Churn_Rate"].map(fmt_pct)
    return out

st.markdown('<div class="eyebrow">RETAIL BANKING • CUSTOMER INTELLIGENCE</div>', unsafe_allow_html=True)
st.title("Customer Segmentation & Churn Patterns")
st.markdown('<p class="intro">A practical view of who leaves, where churn is concentrated and which customer groups deserve closer attention.</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Explore the portfolio")
    countries = st.multiselect("Geography", sorted(df["Geography"].dropna().unique()), default=sorted(df["Geography"].dropna().unique()))
    genders = st.multiselect("Gender", sorted(df["Gender"].dropna().unique()), default=sorted(df["Gender"].dropna().unique()))
    age_groups = st.multiselect("Age group", [str(x) for x in df["AgeGroup"].cat.categories], default=[str(x) for x in df["AgeGroup"].cat.categories])
    activity = st.selectbox("Activity status", ["All customers", "Active members", "Inactive members"])
    products = st.multiselect("Number of products", sorted(df["NumOfProducts"].unique()), default=sorted(df["NumOfProducts"].unique()))
    st.caption("Filters update every chart and KPI on this page.")
    st.divider()
    st.caption("Source: supplied European_Bank dataset")

filtered = df[df["Geography"].isin(countries) & df["Gender"].isin(genders) &
              df["AgeGroup"].astype(str).isin(age_groups) & df["NumOfProducts"].isin(products)].copy()
if activity == "Active members":
    filtered = filtered[filtered["IsActiveMember"] == 1]
elif activity == "Inactive members":
    filtered = filtered[filtered["IsActiveMember"] == 0]

n = len(filtered)
churned = int(filtered["Exited"].sum())
overall = rate(filtered)
mean_balance_churned = filtered.loc[filtered["Exited"] == 1, "Balance"].mean() if churned else 0
balance_exposure = filtered.loc[filtered["Exited"] == 1, "Balance"].sum()

m1,m2,m3,m4 = st.columns(4)
m1.metric("Customers in view", f"{n:,}")
m2.metric("Churn rate", fmt_pct(overall), f"{churned:,} exited")
m3.metric("Retained customers", f"{n-churned:,}")
m4.metric("Balance held by churners", f"€{balance_exposure/1e6:,.1f}M")
st.caption("The balance figure is an account-balance exposure indicator, not lost revenue or profit.")

if n == 0:
    st.warning("No customers match the selected filters. Broaden the filters to continue.")
    st.stop()

st.divider()
left, right = st.columns([1.05, 1])
with left:
    st.subheader("Where churn is concentrated")
    geo = filtered.groupby("Geography", as_index=False).agg(Customers=("Exited","size"), Churned=("Exited","sum"), Churn_Rate=("Exited","mean"))
    geo["Churn rate"] = geo["Churn_Rate"].map(fmt_pct)
    fig = px.bar(geo, x="Geography", y="Churn_Rate", text="Churned",
                 labels={"Churn_Rate":"Churn rate", "Geography":"Country"},
                 color="Churn_Rate", color_continuous_scale=["#4b8795","#d5a15f"])
    fig.update_traces(texttemplate="%{text:,} exited", textposition="outside")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      coloraxis_showscale=False, yaxis_tickformat=".0%", margin=dict(l=10,r=10,t=25,b=10))
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Retained vs exited")
    mix = filtered["Exited"].value_counts().reindex([0,1], fill_value=0).rename({0:"Retained",1:"Exited"}).reset_index()
    mix.columns = ["Customer status","Customers"]
    fig = px.pie(mix, names="Customer status", values="Customers", hole=.62,
                 color="Customer status", color_discrete_map={"Retained":"#4b8795","Exited":"#d5a15f"})
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=25,b=10),
                      legend=dict(orientation="h", y=-.08))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Demographic and relationship patterns")
a,b = st.columns(2)
with a:
    age = filtered.groupby("AgeGroup", observed=True).agg(Customers=("Exited","size"), Churn_Rate=("Exited","mean")).reset_index()
    fig = px.bar(age, x="AgeGroup", y="Churn_Rate", text=age["Churn_Rate"].map(fmt_pct),
                 labels={"AgeGroup":"Age band","Churn_Rate":"Churn rate"}, color_discrete_sequence=["#5c9ead"])
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_tickformat=".0%", margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig, use_container_width=True)
with b:
    tenure = filtered.groupby("TenureGroup", observed=True).agg(Customers=("Exited","size"), Churn_Rate=("Exited","mean")).reset_index()
    fig = px.bar(tenure, x="TenureGroup", y="Churn_Rate", text=tenure["Churn_Rate"].map(fmt_pct),
                 labels={"TenureGroup":"Length of relationship","Churn_Rate":"Churn rate"}, color_discrete_sequence=["#d5a15f"])
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_tickformat=".0%", margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig, use_container_width=True)

c,d = st.columns(2)
with c:
    st.subheader("Geography × age")
    heat = filtered.pivot_table(index="Geography", columns="AgeGroup", values="Exited", aggfunc="mean", observed=True)
    fig = px.imshow(heat, text_auto=".1%", aspect="auto", color_continuous_scale="YlOrBr",
                    labels=dict(x="Age band", y="Country", color="Churn rate"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig, use_container_width=True)
with d:
    st.subheader("Engagement and product holding")
    engagement = filtered.groupby("IsActiveMember").agg(Customers=("Exited","size"), Churn_Rate=("Exited","mean")).reset_index()
    engagement["Member status"] = engagement["IsActiveMember"].map({0:"Inactive",1:"Active"})
    fig = px.bar(engagement, x="Member status", y="Churn_Rate", text=engagement["Churn_Rate"].map(fmt_pct),
                 labels={"Churn_Rate":"Churn rate"}, color="Member status",
                 color_discrete_map={"Inactive":"#d5a15f","Active":"#4b8795"})
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_tickformat=".0%", showlegend=False, margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("High-value balance customers")
st.markdown(f'<div class="note">For this analysis, “high-value balance” means a balance at or above the 75th percentile of positive account balances (dataset threshold: €{premium_cutoff:,.2f}). This is a transparent proxy, not a bank-defined profitability tier.</div>', unsafe_allow_html=True)
hv = filtered[filtered["ValueSegment"] == "High-value balance"]
x1,x2,x3 = st.columns(3)
x1.metric("High-value customers", f"{len(hv):,}")
x2.metric("High-value churn rate", fmt_pct(rate(hv)) if len(hv) else "—")
x3.metric("High-value customers exited", f"{int(hv['Exited'].sum()):,}")
bal = filtered.groupby("BalanceSegment", as_index=False).agg(Customers=("Exited","size"), Churn_Rate=("Exited","mean"))
fig = px.bar(bal, x="BalanceSegment", y="Churn_Rate", text=bal["Churn_Rate"].map(fmt_pct),
             labels={"BalanceSegment":"Balance segment","Churn_Rate":"Churn rate"},
             color_discrete_sequence=["#5c9ead"])
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                  yaxis_tickformat=".0%", margin=dict(l=10,r=10,t=20,b=10))
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Segment detail")
segment_choice = st.selectbox("Choose a segmentation dimension",
    ["Geography","AgeGroup","CreditBand","TenureGroup","BalanceSegment","Gender","NumOfProducts"])
detail = filtered.groupby(segment_choice, observed=True).agg(
    Customers=("Exited","size"), Churned=("Exited","sum"), Churn_Rate=("Exited","mean"),
    Average_Age=("Age","mean"), Average_Balance=("Balance","mean")).reset_index()
detail["Churn rate"] = detail["Churn_Rate"].map(fmt_pct)
detail["Average balance"] = detail["Average_Balance"].map(lambda x: f"€{x:,.0f}")
st.dataframe(detail[[segment_choice,"Customers","Churned","Churn rate","Average_Age","Average balance"]],
             use_container_width=True, hide_index=True)

st.subheader("Customer-level review")
st.caption("Customer identifiers are included for internal review; surnames are excluded from the dashboard.")
review = filtered.loc[filtered["Exited"] == 1, ["CustomerId","Geography","Gender","Age","Tenure","CreditScore","Balance","NumOfProducts","IsActiveMember"]].copy()
st.dataframe(review.sort_values("Balance", ascending=False).head(100), use_container_width=True, hide_index=True)
st.download_button("Download filtered customer data", filtered.drop(columns=["Surname"], errors="ignore").to_csv(index=False).encode("utf-8"),
                   file_name="filtered_customer_churn.csv", mime="text/csv")

st.divider()
st.caption("Prepared for internship project submission • Descriptive analysis of the supplied 10,000-row dataset. Patterns are associations, not proof of causation.")
