import pandas as pd
import streamlit as st


st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="centered")

st.title("💸 Expense Tracker")
st.caption("Add expenses and see where your money goes.")

# Streamlit session state keeps this demo's data available while the current
# browser session is active. It is not permanent storage.
if "expenses" not in st.session_state:
    st.session_state.expenses = []

with st.form("expense_form", clear_on_submit=True):
    st.subheader("Add an expense")
    description = st.text_input("Description", placeholder="e.g. Lunch")
    category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])
    amount = st.number_input("Amount (₹)", min_value=0.01, step=10.0, format="%.2f")
    submitted = st.form_submit_button("Add expense", type="primary")

if submitted:
    if not description.strip():
        st.error("Please enter a description.")
    else:
        st.session_state.expenses.append(
            {
                "Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                "Description": description.strip(),
                "Category": category,
                "Amount (₹)": float(amount),
            }
        )
        st.success("Expense added!")

st.divider()
st.subheader("Your expenses")

if st.session_state.expenses:
    expenses_df = pd.DataFrame(st.session_state.expenses)
    total = expenses_df["Amount (₹)"].sum()
    st.metric("Total spending", f"₹{total:,.2f}")

    category_totals = expenses_df.groupby("Category")["Amount (₹)"].sum().sort_values(ascending=False)
    st.caption("Spending by category")
    st.bar_chart(category_totals)

    st.dataframe(expenses_df.iloc[::-1], use_container_width=True, hide_index=True)
    csv_data = expenses_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download expenses as CSV", csv_data, "expenses.csv", "text/csv")

    if st.button("Clear all expenses"):
        st.session_state.expenses = []
        st.rerun()
else:
    st.info("No expenses yet. Add one above to get started.")

st.caption("Demo note: expenses are kept only for this active browser session and are not permanently stored.")
