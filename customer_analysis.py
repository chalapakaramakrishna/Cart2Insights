import pandas as pd
from sqlalchemy import true
import streamlit as st
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

st.title("3.Customer Analysis")


st.header("A. Customer Distribution")

customer_distribution_sql = """select customer_state as state, count(distinct(customer_id)) as customers
from customers 
group by state
order by customers desc;
"""

customer_distribution_df = pd.read_sql_query(customer_distribution_sql,connection)

st.bar_chart(data= customer_distribution_df,x="state", y="customers",color="state",use_container_width=True)


st.header("B. Customer spending ")

customer_spending_sql = """select c.customer_id, count((o.order_id)) as items_purchased, sum(oi.price) as value
from customers c 
join orders o on c.customer_id = o.customer_id 
join order_items oi  on oi.order_id = o.order_id
group by c.customer_id 
order by value desc;
"""
customer_spending_df = pd.read_sql_query(customer_spending_sql,connection)

st.bar_chart(data=customer_spending_df,x="customer_id",y="value",use_container_width=True)


st.header("D. Top Customers")

top_customers_sql="""select c.customer_id, c.customer_city, c.customer_state, count((o.order_id)) as total_orders, sum(price) as total_spending
from customers c 
join orders o on o.customer_id = c.customer_id
join order_items oi on oi.order_id = o.order_id 
group by c.customer_id
order by total_spending desc;
"""

top_customers_df=pd.read_sql_query(top_customers_sql,connection)

st.bar_chart(data=top_customers_df,x="customer_id",y="total_spending")



st.header("C. Repeat vs. new customers")

repeat_customers_sql="""WITH customer_orders AS (
    SELECT 
        customer_id, 
        COUNT(DISTINCT order_id) AS order_count 
    FROM orders 
    GROUP BY customer_id
) 
SELECT 
    CASE 
        WHEN order_count = 1 THEN 'New Customer' 
        ELSE 'Repeat Customer' 
    END AS customer_type, 
    COUNT(*) AS customer_count 
FROM customer_orders 
GROUP BY 1  
ORDER BY customer_count DESC;
"""
repeat_customers_df = pd.read_sql_query(repeat_customers_sql,connection)

st.bar_chart(data=repeat_customers_df,x="customer_type",y="customer_count")


connection.close()

