import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="FinTech", layout="centered")
st.title("FinTech 💰")

# -------- AI Categorization Logic --------
def categorize_expense(description: str) -> str:
    description = description.lower()

    if any(word in description for word in ["food", "pizza", "burger", "restaurant", "cafe", "coffee"]):
        return "Food"
    elif any(word in description for word in ["uber", "bus", "metro", "taxi", "train"]):
        return "Transport"
    elif any(word in description for word in ["electricity", "water", "wifi", "gas", "bill", "recharge"]):
        return "Utilities"
    elif any(word in description for word in ["shopping", "clothes", "amazon", "flipkart", "mall"]):
        return "Shopping"
    elif any(word in description for word in ["movie", "netflix", "game", "concert"]):
        return "Entertainment"
    else:
        return "Others"

# -------- SESSION STATE --------
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Description", "Amount", "Category"]
    )

# -------- LIVE INPUT SECTION --------
st.subheader("Live Expense Input 🧾")

desc = st.text_input("Enter expense description")
amt = st.number_input("Enter amount (₹)", min_value=0.0, step=1.0)

if st.button("Add Expense"):
    if desc and amt > 0:
        new_row = {
            "Description": desc,
            "Amount": float(amt),
            "Category": categorize_expense(desc)
        }

        st.session_state.expenses = pd.concat(
            [st.session_state.expenses, pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success(f"Saved! Category: *{new_row['Category']}*")
    else:
        st.warning("Please enter a valid description and amount.")

# -------- DISPLAY SAVED DATA --------
df = st.session_state.expenses

if not df.empty:
    st.subheader("Saved Expenses 📊")
    st.dataframe(df, use_container_width=True)

    # Category-wise sum
    category_sum = df.groupby("Category")["Amount"].sum()

    # Pie chart
    fig, ax = plt.subplots()
    ax.pie(category_sum, labels=category_sum.index, autopct="%1.1f%%")
    ax.set_title("Category-wise Spending")
    st.pyplot(fig)
    plt.close(fig)

    # -------- AI INSIGHTS --------
    st.subheader("AI Insights 🧠")

    highest_category = category_sum.idxmax()
    highest_amount = category_sum.max()
    total_spent = category_sum.sum()

    st.write(f"• You spent the most on **{highest_category}** (₹{highest_amount:.2f})")
    st.write(f"• Your total spending is **₹{total_spent:.2f}**")

    if highest_category in ["Food", "Shopping", "Entertainment"]:
        st.warning("Consider reducing discretionary expenses to save more.")
    else:
        st.success("Your spending is mostly essential and well balanced.")

# -------- DISPLAY & DELETE EXPENSES --------
st.subheader("Saved Expenses (Category-wise) 🗂️")

for category in df["Category"].unique():
    st.markdown(f"### 📌 {category}")
    category_df = df[df["Category"] == category]

    for idx, row in category_df.iterrows():
        col1, col2, col3 = st.columns([4, 2, 1])
        col1.write(row["Description"])
        col2.write(f"₹{row['Amount']:.2f}")

        if col3.button("❌", key=f"delete_{idx}"):
            st.session_state.expenses = df.drop(idx).reset_index(drop=True)
            st.rerun()

# -------- SMART ALERTS --------
st.subheader("Smart Alerts ⚠️")

if len(df) >= 3:
    avg_spend = df["Amount"].mean()
    std_spend = df["Amount"].std()
    last_expense = df.iloc[-1]

    if std_spend > 0 and last_expense["Amount"] > avg_spend + 2 * std_spend:
        st.error(
            f"⚠️ Unusual Expense Detected: ₹{last_expense['Amount']:.2f}"
        )

    category_ratio = df.groupby("Category")["Amount"].sum() / df["Amount"].sum()

for category, ratio in category_ratio.items():
    if ratio > 0.5:
        st.warning(f"⚠️ Over 50% of your spending is in **{category}** ({ratio*100:.1f}%)")

else:
    st.info("Add more expenses to enable smart anomaly detection.")

# -------- NEXT MONTH RECOMMENDATIONS --------
st.subheader("Next Month Smart Recommendations 🔮")

if not df.empty:
    total_spent = df["Amount"].sum()
    category_spend = df.groupby("Category")["Amount"].sum()

    for category, amount in category_spend.items():
        percentage = (amount / total_spent) * 100

        if category == "Shopping" and percentage > 30:
            st.warning(f"🔮 Reduce Shopping expenses ({percentage:.1f}%)")
        elif category == "Food" and percentage > 25:
            st.info(f"🔮 Food spending is high ({percentage:.1f}%)")
        elif category == "Entertainment" and percentage > 20:
            st.info("🔮 Try low-cost entertainment next month")

    if category_spend.max() / total_spent < 0.3:
        st.success("🔮 Your spending is well balanced.")
else:
    st.info("Start adding expenses to get predictions.")

import streamlit as st
import streamlit as st

# -------- Pre-saved Questions & Answers --------
pre_saved_qa = {
    "Where should I save money?": lambda df: "💡 Consider reducing spending on Food, Shopping, and Entertainment to save more." if not df.empty else "No expenses recorded yet.",
    "What are the least spent categories?": lambda df: f"The categories you spend the least on are: {', '.join(df.groupby('Category')['Amount'].sum().sort_values().head(2).index)}" if not df.empty else "No expenses recorded yet.",
    "Any tips for next month?": lambda df: "🔮 Try setting a budget and tracking your spending weekly for better savings." if not df.empty else "No expenses recorded yet.",
    "Any unusual spendings I have done?": lambda df: detect_anomaly(df)
}

# -------- Helper function for anomaly detection --------
def detect_anomaly(df):
    if len(df) < 3:
        return "Add more expenses to enable anomaly detection."
    avg = df["Amount"].mean()
    std = df["Amount"].std()
    last = df.iloc[-1]
    if std > 0 and last["Amount"] > avg + 2 * std:
        return f"⚠️ Last expense of ₹{last['Amount']:.2f} is unusually high!"
    return "No unusual expenses detected."

# -------- UI for Pre-saved Q&A --------
st.subheader("📚 Quick Q&A")
question = st.selectbox("Select a question:", ["-- Select a question --"] + list(pre_saved_qa.keys()))

if question != "-- Select a question --":
    # Use the current expenses DataFrame
    df = st.session_state.get("expenses", pd.DataFrame(columns=["Description", "Amount", "Category"]))
    answer = pre_saved_qa[question](df)
    st.info(answer)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to handle user input
def submit_chat():
    user_message = st.session_state.chat_input  # Get the text from the input
    if user_message.strip() != "":
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_message})
        # Generate bot response (replace this with your AI/chat logic)
        bot_response = f"Bot says: {user_message[::-1]}"  # Example: echo reversed
        st.session_state.messages.append({"role": "bot", "content": bot_response})
    st.session_state.chat_input = ""  # Clear input after submit

