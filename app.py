import plotly.express as px
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from io import BytesIO

# Page settings
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Dark theme styling
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
h1, h2, h3, p, label {
    color: white !important;
}
[data-testid="stMetric"] {
    background-color: #1e2530;
    padding: 20px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# Database connection
def get_data():
    conn = sqlite3.connect("expense.db")
    df = pd.read_sql_query(
        "SELECT * FROM transactions ORDER BY date DESC",
        conn
    )
    conn.close()
    return df

# Dashboard title
st.title("💰 My Expense Tracker")
st.caption("Manage your income and expenses easily.")

# Read database
df = get_data()

# Calculate totals
income = df.loc[
    df["transaction_type"] == "Income", "amount"
].sum()

expense = df.loc[
    df["transaction_type"] == "Expense", "amount"
].sum()

savings = income - expense

# Metric cards
col1, col2, col3 = st.columns(3)

col1.metric("Total Income", f"₹{income:,.2f}")
col2.metric("Total Expense", f"₹{expense:,.2f}")
col3.metric("Total Savings", f"₹{savings:,.2f}")

st.divider()

# Reset form fields after successful transaction
if st.session_state.get("reset_transaction_form", False):
    st.session_state["transaction_type"] = "Expense"
    st.session_state["amount"] = 0.0
    st.session_state["category"] = "Food"
    st.session_state["description"] = ""
    st.session_state["transaction_date"] = date.today()
    st.session_state["reset_transaction_form"] = False

# Add transaction
st.subheader("➕ Add New Transaction")

with st.form("transaction_form"):

    transaction_type = st.selectbox(
        "Transaction Type",
        ["Income", "Expense"],
        key="transaction_type"
    )

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=100.0,
        key="amount"
    )

    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Shopping", "Salary",
         "Education", "Bills", "Freelancing", "Other"],
        key="category"
    )

    description = st.text_input(
        "Description",
        key="description"
    )

    transaction_date = st.date_input(
        "Select date",
        value=date.today(),
        key="transaction_date"
    )

    submit = st.form_submit_button("Save Transaction")

    if submit:
        if amount <= 0:
            st.error("Please enter an amount greater than zero.")
        else:
            conn = sqlite3.connect("expense.db")
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO transactions
                (transaction_type, amount, category, description, date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                transaction_type,
                amount,
                category,
                description,
                str(transaction_date)
            ))

            conn.commit()
            conn.close()

            st.success("Transaction added successfully!")

            st.session_state["reset_transaction_form"] = True

            st.rerun()

st.divider()





# Category-wise Expense Pie Chart


st.subheader("🍩 Category-wise Expense Breakdown")

expense_df = df[
    df["transaction_type"] == "Expense"
]

if not expense_df.empty:

    category_data = expense_df.groupby(
        "category"
    )["amount"].sum()

    st.subheader("Expense by Category")

    import plotly.express as px

    fig = px.pie(
    names=category_data.index,
    values=category_data.values,
    title="Where is your money going?",
    hole=0.4
    )

    fig.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )

    fig.update_layout(
    template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No expense data available for the pie chart.")


st.divider()
# Transaction history
st.subheader("📋 Recent Transactions")

df = get_data()

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No transactions available yet.")


# Sidebar Filters
st.sidebar.header("Filters")

start_date = st.sidebar.date_input(
    "Start Date",
    value=None
)

end_date = st.sidebar.date_input(
    "End Date",
    value=None
)

categories = ["All Categories"] + sorted(
    df["category"].dropna().unique().tolist()
)

selected_category = st.sidebar.selectbox(
    "Select Category",
    categories
)

# Apply Filters
filtered_df = df.copy()
filtered_df["date"] = pd.to_datetime(
    filtered_df["date"]
).dt.date

# Check whether any filter is applied
filter_applied = (
    start_date is not None
    or end_date is not None
    or selected_category != "All Categories"
)
if not filter_applied:
    st.info("Please apply a Date or Category filter to view your transactions.")

if filter_applied:

    if start_date is not None:
        filtered_df = filtered_df[
            filtered_df["date"] >= start_date
        ]

    if end_date is not None:
        filtered_df = filtered_df[
            filtered_df["date"] <= end_date
        ]

    if selected_category != "All Categories":
        filtered_df = filtered_df[
            filtered_df["category"] == selected_category
        ]

else:
    filtered_df = df.iloc[0:0].copy()
    filtered_df["date"] = pd.to_datetime(
        filtered_df["date"]
    ).dt.date




# Display Filtered Data
st.dataframe(filtered_df)

total_income = filtered_df[
    filtered_df["transaction_type"] == "Income"
]["amount"].sum()

total_expense = filtered_df[
    filtered_df["transaction_type"] == "Expense"
]["amount"].sum()

total_savings = total_income - total_expense

# Three KPI Cards
col1, col2, col3 = st.columns(3)

col1.metric("Total Income", f"₹{total_income:,.2f}")
col2.metric("Total Expense", f"₹{total_expense:,.2f}")
col3.metric("Net_Savings", f"₹{total_savings:,.2f}")



# Prepare data for monthly chart
chart_df = filtered_df.copy()

chart_df["date"] = pd.to_datetime(chart_df["date"])
chart_df["amount"] = pd.to_numeric(
    chart_df["amount"], errors="coerce"
)

chart_df["transaction_type"] = (
    chart_df["transaction_type"]
    .str.strip()
    .str.lower()
)

chart_df["month"] = chart_df["date"].dt.strftime("%Y-%m")

# Monthly Summary
monthly_summary = chart_df.pivot_table(
    index="month",
    columns="transaction_type",
    values="amount",
    aggfunc="sum",
    fill_value=0
)

monthly_summary = monthly_summary.reindex(
    columns=["income", "expense"],
    fill_value=0
)

st.subheader("Monthly Income vs Expense")
st.bar_chart(monthly_summary)


# Top Expense Category Analysis


expense_df = filtered_df[
    filtered_df["transaction_type"] == "Expense"
]

category_summary = expense_df.groupby(
    "category"
)["amount"].sum().sort_values(ascending=False)

st.subheader("Top Expense Categories")

if not category_summary.empty:
    st.bar_chart(category_summary)
else:
    st.info("No expense data available for selected filters.")



# Expense Distribution Pie Chart

st.subheader("Expense Distribution")

if not category_summary.empty:
    st.plotly_chart(
        px.pie(
            names=category_summary.index,
            values=category_summary.values,
            title="Category-wise Expense Distribution",
            hole=0.4
        ),
        use_container_width=True
    )
else:
    st.info("No expense data available.")



# Highest Spending Insights

st.subheader("Highest Spending Insights")

if not category_summary.empty:

    highest_category = category_summary.idxmax()
    highest_amount = category_summary.max()

    total_expense = category_summary.sum()

    percentage = (highest_amount / total_expense) * 100

    col1, col2, col3 = st.columns(3)

    col1.metric("Highest Expense Category", highest_category)

    col2.metric("Highest Spending", f"₹{highest_amount:,.2f}")

    col3.metric("Expense Percentage", f"{percentage:.2f}%")

else:
    st.info("No expense data available.")


st.divider()
# Income vs Expense Percentage

st.subheader("Income vs Expense Percentage")

if total_income > 0:
    expense_percentage = (total_expense / total_income) * 100
    savings_percentage = (total_savings / total_income) * 100

    col1, col2 = st.columns(2)

    col1.metric(
        "Expense Percentage",
        f"{expense_percentage:.2f}%"
    )
    col2.metric(
            "Savings Percentage",
            f"{savings_percentage:.2f}%"
    )

    st.write(f"💸 Expense — {expense_percentage:.2f}%")
    st.progress(max(0, min(expense_percentage, 100)) / 100)

    st.write(f"💰 Savings — {savings_percentage:.2f}%")
    st.progress(max(0, min(savings_percentage, 100)) / 100)

else:
    st.info("No income data available to calculate percentage.")




# Transaction Search
st.divider()
st.subheader("Transaction Search")

if "search_submitted" not in st.session_state:
    st.session_state.search_submitted = ""

def submit_search():
    st.session_state.search_submitted = st.session_state.search_input
    st.session_state.search_input = ""

search_query = st.text_input(
    "Search by Category or Description",
    placeholder="Enter category or description...",
    key="search_input",
    on_change=submit_search
)

search_query = st.session_state.search_submitted
export_df = filtered_df

if search_query:
    search_df = filtered_df[
        filtered_df["category"].astype(str).str.contains(
            search_query, case=False, na=False
        )
        |
        filtered_df["description"].astype(str).str.contains(
            search_query, case=False, na=False
        )
    ]
    export_df = search_df

    st.dataframe(search_df, use_container_width=True)

    st.write(f"Total matching transactions: {len(search_df)}")

else:
    st.info("Enter a category or description to search transactions.")

download_disabled = not filter_applied or export_df.empty

# CSV / Excel Export

st.subheader("Export Transactions")

# CSV Download
csv_data = export_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="expense_report.csv",
    mime="text/csv",
    disabled=download_disabled
)

# Excel Download
excel_buffer = BytesIO()

with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    export_df.to_excel(
        writer,
        index=False,
        sheet_name="Transactions"
    )

st.download_button(
    label="Download Excel",
    data=excel_buffer.getvalue(),
    file_name="expense_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    disabled=download_disabled
)
