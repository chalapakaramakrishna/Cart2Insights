import streamlit as st
import pandas as pd
import psycopg2

#------------------------------------
# database connection
#------------------------------------
connection = psycopg2.connect(
    host="localhost",
    port="5432",
    user="postgres",
    password="9185",
    database="postgres"
)

connection.autocommit = True



st.title("2. Sales Analysis")

st.header("A. Monthly Revenue Trend")

monthly_revenue_sql = ''' 
select 
      date_trunc('month', o.order_purchase_timestamp) as month,
      sum(oi.price) as revenue
from orders o
join order_items oi
    on o.order_id = oi.order_id 
group by date_trunc('month', o.order_purchase_timestamp)
order by month desc;
'''

monthly_revenue_df = pd.read_sql_query(
    monthly_revenue_sql,
    connection
)

monthly_revenue_df["month"] = pd.to_datetime(
    monthly_revenue_df["month"]
)

monthly_revenue_df["month"] = (
    monthly_revenue_df["month"].dt.strftime("%b %Y")
)

st.line_chart(
    monthly_revenue_df.set_index("month")["revenue"]
)

st.dataframe(
    monthly_revenue_df,
    use_container_width=True,
    hide_index=True
)

st.header("B. Revenue by Category")

category_revenue_sql = """
select 
      p.product_category_name as category,
      sum(price) as revenue
from order_items oi 
join products p
      on oi.product_id  = p.product_id 
group by category
order by revenue desc;
"""

category_revenue_df = pd.read_sql_query(
    category_revenue_sql,
    connection
)

st.bar_chart(
    category_revenue_df.set_index("category")["revenue"]
)

st.dataframe(
    category_revenue_df,
    use_container_width=True,
    hide_index=True
)

st.header("C. Top-Selling Products")


top_products_sql = """
select 
      p.product_id as product , p.product_category_name , count(oi.order_item_id) as orderitems
from  order_items oi
join  products p
     on p.product_id = oi.product_id 
group by product
order by orderitems desc;
"""
top_products_df = pd.read_sql_query(
    top_products_sql,
    connection
)

st.bar_chart(
    top_products_df.set_index("product")["orderitems"]
)

st.dataframe(
    top_products_df,
    use_container_width=True,
    hide_index=True
)

st.header("D. Sales by Location")

location_sales_sql = """
select 
      c.customer_state as state, sum(oi.price) as revenue, count((o.order_id)) as orders 
from  customers c
join orders o on c.customer_id = o.customer_id
join order_items oi on o.order_id = oi.order_id
group by state
order by revenue desc;

"""
location_sales_df = pd.read_sql_query(
    location_sales_sql,
    connection
)

st.bar_chart(
    location_sales_df.set_index("state")["revenue"]
)

st.dataframe(
    location_sales_df,
    use_container_width=True,
    hide_index=True
)

connection.close()

