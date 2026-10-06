import pandas as pd
import psycopg2
import streamlit as st

connection = psycopg2.connect(
    host="localhost",
    port="5432",
    user="postgres",
    password="9185",
    database="postgres"
)
connection.autocommit = True

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

st.bar_chart(data=seller_ratings_df,x="seller_id",y="average_rating",color="seller_id")


st.title("5. Delivery Analysis ")

st.header("A. Average delivery time")

average_delivery_time_sql="""select order_estimated_delivery_date, 
        order_delivered_customer_date,
        avg(date(order_delivered_customer_date)- date (order_estimated_delivery_date)) as delivery_days 
from orders
group by order_estimated_delivery_date,order_delivered_customer_date;
"""
average_delivery_time_df = pd.read_sql_query(average_delivery_time_sql,connection)

st.line_chart(data=average_delivery_time_df,x="order_estimated_delivery_date",y="order_delivered_customer_date")

st.header("B. On-time vs delayed orders")

ontime_delayed_sql = """select order_estimated_delivery_date, order_delivered_customer_date,
      date(order_delivered_customer_date)- date (order_estimated_delivery_date) as delivery_days,
case when date(order_delivered_customer_date)<= date(order_estimated_delivery_date) then 'On Time'
     else 'Delayed'
end as delivery_status
from orders;
"""
ontime_delayed_df = pd.read_sql_query(ontime_delayed_sql,connection)

st.scatter_chart (data=ontime_delayed_df,x="delivery_status",y="delivery_days")

st.header("C. Delivery performance by location ")

delivery_performance_sql= """select c.customer_state as state,
count(order_id) as total_orders,
avg(date(order_delivered_customer_date)- date (order_estimated_delivery_date)) as avg_delivery_days,
case when date(order_delivered_customer_date)<= date(order_estimated_delivery_date) then 'On Time'
     else 'Delayed'
end as delivery_status
from customers c
join orders o on o.customer_id = c.customer_id
group by state,order_estimated_delivery_date,order_delivered_customer_date
order by avg_delivery_days;
"""
delivery_performance_df = pd.read_sql_query(delivery_performance_sql,connection)

st.bar_chart(data=delivery_performance_df,x="state",y="avg_delivery_days",color="state")

st.header("D. Delivery delay vs review score")

delivery_delay_review_sql ="""select o.order_id, orv.review_score,
   date(order_delivered_customer_date) - date(order_estimated_delivery_date) as delivery_days,
     case when date (order_delivered_customer_date) <= date (order_estimated_delivery_date) then 'On Time'
     else 'Delayed'
     end as delivery_status
from orders o
join order_reviews orv on orv.order_id = o.order_id;
"""
delivery_delay_review_df = pd.read_sql_query(delivery_delay_review_sql,connection)

st.scatter_chart(data=delivery_delay_review_df,x="delivery_days",y="review_score",color="delivery_days")

connection.close()