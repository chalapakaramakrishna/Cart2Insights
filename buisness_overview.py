import streamlit as st
import psycopg2
import pandas as pd


# ---------------------------------------
# DATABASE CONNECTION
# ---------------------------------------

connection = psycopg2.connect(
    host="localhost",
    port="5432",
    user="postgres",
    password="9185",
    database="postgres"
)

connection.autocommit = True

cursor = connection.cursor()


# ---------------------------------------
# STREAMLIT TITLE
# ---------------------------------------

st.title("📊 1. Business Overview")


# ---------------------------------------
# BUSINESS OVERVIEW SQL
# ---------------------------------------

sql = """
SELECT
    (SELECT COALESCE(SUM(price), 0)
     FROM order_items) AS total_revenue,

    (SELECT COUNT(DISTINCT order_id)
     FROM orders) AS total_orders,

    (SELECT COUNT(DISTINCT customer_id)
     FROM customers) AS total_customers,

    (SELECT COUNT(DISTINCT seller_id)
     FROM sellers) AS total_sellers,

    (SELECT COALESCE(AVG(review_score), 0)
     FROM order_reviews) AS average_review_score
"""


# ---------------------------------------
# EXECUTE QUERY
# ---------------------------------------

cursor.execute(sql)

result = cursor.fetchone()


# ---------------------------------------
# STORE RESULTS
# ---------------------------------------

total_revenue = result[0]
total_orders = result[1]
total_customers = result[2]
total_sellers = result[3]
average_review_score = result[4]


# ---------------------------------------
# CALCULATE AVERAGE ORDER VALUE
# ---------------------------------------

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)


# ---------------------------------------
# KPI CARDS
# ---------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "💰 Total Revenue",
        f"₹{total_revenue:,.2f}"
    )

with col2:
    st.metric(
        "📦 Total Orders",
        f"{total_orders:,}"
    )

with col3:
    st.metric(
        "👥 Total Customers",
        f"{total_customers:,}"
    )


col4, col5, col6 = st.columns(3)

with col4:
    st.metric(
        "🏪 Total Sellers",
        f"{total_sellers:,}"
    )

with col5:
    st.metric(
        "🛒 Average Order Value",
        f"₹{average_order_value:,.2f}"
    )

with col6:
    st.metric(
        "⭐ Average Review Score",
        f"{average_review_score:.2f} / 5"
    )


# ---------------------------------------
# BUSINESS OVERVIEW TABLE
# ---------------------------------------

st.divider()

st.subheader("Business Overview Details")


overview_df = pd.DataFrame({
    "Metric": [
        "Total Revenue",
        "Total Orders",
        "Total Customers",
        "Total Sellers",
        "Average Order Value",
        "Average Review Score"
    ],

    "Value": [
        f"₹{total_revenue:,.2f}",
        f"{total_orders:,}",
        f"{total_customers:,}",
        f"{total_sellers:,}",
        f"₹{average_order_value:,.2f}",
        f"{average_review_score:.2f} / 5"
    ]
})


st.dataframe(
    overview_df,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------
# CLOSE DATABASE CONNECTION
# ---------------------------------------

cursor.close()
connection.close()