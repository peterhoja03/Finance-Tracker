import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
from pathlib import Path

st.set_page_config(
    page_title="Finance Tracker",
    page_icon="₤",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif;
}

.main-header {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: #1a1a2e;
    margin-bottom: 0;
    line-height: 1.1;
}

.sub-header {
    font-size: 0.9rem;
    color: #888;
    font-weight: 300;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #f0f0f0;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}

.metric-label {
    font-size: 0.75rem;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
    margin-bottom: 0.3rem;
}

.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #1a1a2e;
    line-height: 1;
}

.metric-value.positive { color: #2d7a4f; }
.metric-value.negative { color: #c0392b; }
.metric-value.neutral  { color: #1a1a2e; }

.metric-sub {
    font-size: 0.8rem;
    color: #bbb;
    margin-top: 0.3rem;
}

.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: #1a1a2e;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #f0f0f0;
}

.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}

.tag-income  { background: #e8f5ee; color: #2d7a4f; }
.tag-expense { background: #fdecea; color: #c0392b; }

[data-testid="stSidebar"] {
    background: #1a1a2e;
}

[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}

[data-testid="stSidebar"] .stRadio label {
    color: #e0e0e0 !important;
}

.stButton > button {
    background: #1a1a2e;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    transition: background 0.2s;
}

.stButton > button:hover {
    background: #2d2d4e;
    color: white;
}

.stTextInput input, .stNumberInput input, .stSelectbox select {
    border-radius: 8px;
    border: 1px solid #e8e8e8;
    font-family: 'DM Sans', sans-serif;
}

div[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #f0f0f0;
}
</style>
""", unsafe_allow_html=True)


DATA_FILE = Path("data.json")

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"transactions": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_transactions_df(data):
    if not data["transactions"]:
        return pd.DataFrame(columns=["date", "type", "category", "description", "amount"])
    df = pd.DataFrame(data["transactions"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False).reset_index(drop=True)
    return df

INCOME_CATEGORIES  = ["Salary / RAF Pay", "Amazon DSP", "Freelance", "Gift", "Investment", "Other Income"]
EXPENSE_CATEGORIES = ["Rent / Bills", "Food & Drink", "Transport", "Fuel", "Car", "Clothing", "Golf", "Hockey", "Subscriptions", "Savings", "Other Expense"]


data = load_data()
df   = get_transactions_df(data)

with st.sidebar:
    st.markdown("## ₤ Finance")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["Dashboard", "Add Transaction", "Income", "Expenses", "All Transactions"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if not df.empty:
        months = df["date"].dt.to_period("M").unique()
        month_options = ["All time"] + [str(m) for m in sorted(months, reverse=True)]
        selected_month = st.selectbox("Filter by month", month_options)
    else:
        selected_month = "All time"


if not df.empty and selected_month != "All time":
    period = pd.Period(selected_month)
    filtered_df = df[df["date"].dt.to_period("M") == period]
else:
    filtered_df = df

total_income  = filtered_df[filtered_df["type"] == "Income"]["amount"].sum()  if not filtered_df.empty else 0
total_expense = filtered_df[filtered_df["type"] == "Expense"]["amount"].sum() if not filtered_df.empty else 0
net           = total_income - total_expense


if page == "Dashboard":
    st.markdown('<p class="main-header">Your Finances</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{selected_month if selected_month != "All time" else "All time overview"}</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Income</div>
            <div class="metric-value positive">£{total_income:,.2f}</div>
            <div class="metric-sub">money in</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Expenses</div>
            <div class="metric-value negative">£{total_expense:,.2f}</div>
            <div class="metric-sub">money out</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        net_class = "positive" if net >= 0 else "negative"
        net_label = "surplus" if net >= 0 else "deficit"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Net Balance</div>
            <div class="metric-value {net_class}">£{net:,.2f}</div>
            <div class="metric-sub">{net_label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-title">Income by category</p>', unsafe_allow_html=True)
        if not filtered_df.empty:
            inc = filtered_df[filtered_df["type"] == "Income"].groupby("category")["amount"].sum().sort_values(ascending=False)
            if not inc.empty:
                for cat, amt in inc.items():
                    pct = (amt / total_income * 100) if total_income > 0 else 0
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid #f8f8f8;">
                        <span style="font-size:0.9rem;color:#555;">{cat}</span>
                        <span style="font-family:'DM Serif Display',serif;color:#2d7a4f;">£{amt:,.2f} <span style="font-size:0.75rem;color:#bbb;">({pct:.0f}%)</span></span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.caption("No income recorded.")
        else:
            st.caption("No data yet.")

    with col_b:
        st.markdown('<p class="section-title">Expenses by category</p>', unsafe_allow_html=True)
        if not filtered_df.empty:
            exp = filtered_df[filtered_df["type"] == "Expense"].groupby("category")["amount"].sum().sort_values(ascending=False)
            if not exp.empty:
                for cat, amt in exp.items():
                    pct = (amt / total_expense * 100) if total_expense > 0 else 0
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid #f8f8f8;">
                        <span style="font-size:0.9rem;color:#555;">{cat}</span>
                        <span style="font-family:'DM Serif Display',serif;color:#c0392b;">£{amt:,.2f} <span style="font-size:0.75rem;color:#bbb;">({pct:.0f}%)</span></span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.caption("No expenses recorded.")
        else:
            st.caption("No data yet.")

    st.markdown("---")
    st.markdown('<p class="section-title">Recent transactions</p>', unsafe_allow_html=True)
    if not filtered_df.empty:
        recent = filtered_df.head(8)
        for _, row in recent.iterrows():
            tag_class = "tag-income" if row["type"] == "Income" else "tag-expense"
            sign      = "+" if row["type"] == "Income" else "-"
            color     = "#2d7a4f" if row["type"] == "Income" else "#c0392b"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.6rem 0;border-bottom:1px solid #f8f8f8;">
                <div>
                    <span style="font-size:0.9rem;font-weight:500;color:#1a1a2e;">{row['description']}</span>
                    <span style="margin-left:8px;" class="tag {tag_class}">{row['category']}</span>
                    <div style="font-size:0.75rem;color:#bbb;margin-top:2px;">{row['date'].strftime('%d %b %Y')}</div>
                </div>
                <span style="font-family:'DM Serif Display',serif;font-size:1.1rem;color:{color};">{sign}£{row['amount']:,.2f}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No transactions yet — add one to get started.")


elif page == "Add Transaction":
    st.markdown('<p class="main-header">Add Transaction</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Record income or an expense</p>', unsafe_allow_html=True)

    with st.form("add_transaction", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t_type = st.selectbox("Type", ["Income", "Expense"])
        with col2:
            t_date = st.date_input("Date", value=date.today())

        categories = INCOME_CATEGORIES if t_type == "Income" else EXPENSE_CATEGORIES
        col3, col4 = st.columns(2)
        with col3:
            t_category = st.selectbox("Category", categories)
        with col4:
            t_amount = st.number_input("Amount (£)", min_value=0.01, step=0.01, format="%.2f")

        t_description = st.text_input("Description", placeholder="e.g. Amazon DSP shift, Tesco shop...")

        submitted = st.form_submit_button("Add Transaction")
        if submitted:
            if t_description.strip() == "":
                st.error("Please add a description.")
            else:
                new_entry = {
                    "date": str(t_date),
                    "type": t_type,
                    "category": t_category,
                    "description": t_description.strip(),
                    "amount": round(t_amount, 2)
                }
                data["transactions"].append(new_entry)
                save_data(data)
                st.success(f"{'Income' if t_type == 'Income' else 'Expense'} of £{t_amount:,.2f} added.")
                st.rerun()


elif page == "Income":
    st.markdown('<p class="main-header">Income</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{selected_month if selected_month != "All time" else "All time"}</p>', unsafe_allow_html=True)

    inc_df = filtered_df[filtered_df["type"] == "Income"] if not filtered_df.empty else pd.DataFrame()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Income</div>
            <div class="metric-value positive">£{total_income:,.2f}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        count = len(inc_df)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Transactions</div>
            <div class="metric-value neutral">{count}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if not inc_df.empty:
        display = inc_df[["date", "category", "description", "amount"]].copy()
        display["date"]   = display["date"].dt.strftime("%d %b %Y")
        display["amount"] = display["amount"].apply(lambda x: f"£{x:,.2f}")
        display.columns   = ["Date", "Category", "Description", "Amount"]
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No income recorded for this period.")


elif page == "Expenses":
    st.markdown('<p class="main-header">Expenses</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{selected_month if selected_month != "All time" else "All time"}</p>', unsafe_allow_html=True)

    exp_df = filtered_df[filtered_df["type"] == "Expense"] if not filtered_df.empty else pd.DataFrame()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Expenses</div>
            <div class="metric-value negative">£{total_expense:,.2f}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        count = len(exp_df)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Transactions</div>
            <div class="metric-value neutral">{count}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if not exp_df.empty:
        display = exp_df[["date", "category", "description", "amount"]].copy()
        display["date"]   = display["date"].dt.strftime("%d %b %Y")
        display["amount"] = display["amount"].apply(lambda x: f"£{x:,.2f}")
        display.columns   = ["Date", "Category", "Description", "Amount"]
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No expenses recorded for this period.")


elif page == "All Transactions":
    st.markdown('<p class="main-header">All Transactions</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{selected_month if selected_month != "All time" else "All time"}</p>', unsafe_allow_html=True)

    if not filtered_df.empty:
        display = filtered_df[["date", "type", "category", "description", "amount"]].copy()
        display["date"]   = display["date"].dt.strftime("%d %b %Y")
        display["amount"] = display["amount"].apply(lambda x: f"£{x:,.2f}")
        display.columns   = ["Date", "Type", "Category", "Description", "Amount"]
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**Delete a transaction**")
        if len(data["transactions"]) > 0:
            tx_labels = [
                f"{t['date']} — {t['description']} (£{t['amount']})"
                for t in data["transactions"]
            ]
            to_delete = st.selectbox("Select transaction to delete", tx_labels)
            if st.button("Delete selected"):
                idx = tx_labels.index(to_delete)
                data["transactions"].pop(idx)
                save_data(data)
                st.success("Transaction deleted.")
                st.rerun()
    else:
        st.info("No transactions recorded for this period.")
