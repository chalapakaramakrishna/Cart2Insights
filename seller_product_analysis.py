import pandas as pd
import streamlit as st
import psycopg2

connection = psycopg2.connect(
    host="localhost",
    port="5432",
    user="postgres",
    password="9185",
    database="postgres"
)
connection.autocommit = True

st.title("4. Seller & Product Analysis ")


st.header("A. Top sellers")

top_sellers_sql="""select s.seller_id, s.seller_city, s.seller_state, sum(oi.price) as revenue, count((oi.order_id)) as total_orders
from sellers s
join order_items oi on oi.seller_id = s.seller_id 
join orders o on oi.order_id = o.order_id
group by s.seller_id
order by revenue desc;
"""
top_sellers_df = pd.read_sql_query(top_sellers_sql,connection)

st.bar_chart(data=top_sellers_df,x="seller_id",y="revenue")


st.header("B. Seller revenue")

seller_revenue_sql="""select s.seller_id, count(distinct(o.order_id)) as total_orders, count(oi.order_item_id) as items_sold , sum(oi.price) as revenue from sellers s 
join order_items oi on oi.seller_id = s.seller_id
join  orders o on o.order_id = oi.order_id
group by s.seller_id 
order by revenue desc;
"""
seller_revenue_df = pd.read_sql_query(seller_revenue_sql,connection)

st.bar_chart(data=seller_revenue_df,x="seller_id",y="revenue")


st.header("C. Product/category performance")

product_performance_sql="""
select coalesce(p.product_id, p.product_category_name) as category, sum(oi.price) as revenue, count((o.order_id)) as total_itemssold, avg(oi.price) as average_price
from products p 
join order_items oi on oi.product_id = p.product_id 
join orders o on o.order_id = oi.order_id 
group by category 
order by revenue desc;"""

product_performance_df = pd.read_sql_query(product_performance_sql, connection)

st.bar_chart(data=product_performance_df,x="category",y="revenue")


st.header("D. Seller ratings ")

seller_ratings_sql="""
SELECT
    s.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    ROUND(AVG(orv.review_score)::numeric, 2) AS average_rating
FROM sellers s
JOIN order_items oi
    ON s.seller_id = oi.seller_id
JOIN orders o
    ON o.order_id = oi.order_id
JOIN order_reviews orv
    ON orv.order_id = o.order_id
GROUP BY s.seller_id
ORDER BY average_rating DESC;
"""
seller_ratings_df = pd.read_sql_query(seller_ratings_sql,connection)

st.bar_chart(data=seller_ratings_df,x="seller_id",y="average_rating")

connection.close()