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

st.divider()

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


st.divider()


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

st.bar_chart(data=customer_spending_df,x="customer_id",y="value",color="customer_id",use_container_width=True)


st.header("D. Top Customers")

top_customers_sql="""select c.customer_id, c.customer_city, c.customer_state, count((o.order_id)) as total_orders, sum(price) as total_spending
from customers c 
join orders o on o.customer_id = c.customer_id
join order_items oi on oi.order_id = o.order_id 
group by c.customer_id
order by total_spending desc;
"""

top_customers_df=pd.read_sql_query(top_customers_sql,connection)

st.bar_chart(data=top_customers_df,x="customer_id",y="total_spending",color="customer_id")



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


st.divider()


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

st.bar_chart(data=top_sellers_df,x="seller_id",y="revenue",color="seller_id")


st.header("B. Seller revenue")

seller_revenue_sql="""select s.seller_id, count(distinct(o.order_id)) as total_orders, count(oi.order_item_id) as items_sold , sum(oi.price) as revenue from sellers s 
join order_items oi on oi.seller_id = s.seller_id
join  orders o on o.order_id = oi.order_id
group by s.seller_id 
order by revenue desc;
"""
seller_revenue_df = pd.read_sql_query(seller_revenue_sql,connection)

st.bar_chart(data=seller_revenue_df,x="seller_id",y="revenue",color="seller_id")


st.header("C. Product/category performance")

product_performance_sql="""
select coalesce(p.product_id, p.product_category_name) as category, sum(oi.price) as revenue, count((o.order_id)) as total_itemssold, avg(oi.price) as average_price
from products p 
join order_items oi on oi.product_id = p.product_id 
join orders o on o.order_id = oi.order_id 
group by category 
order by revenue desc;"""

product_performance_df = pd.read_sql_query(product_performance_sql, connection)

st.bar_chart(data=product_performance_df,x="category",y="revenue",color="category")


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


st.divider()


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


st.divider()


st.title("6. Customer Experience ")

st.header("A. Review score distribution ")

review_score_sql = """select oi.review_score,count(review_id) as reviews
from order_reviews oi
group by oi.review_score;
"""

review_score_df = pd.read_sql_query(review_score_sql,connection)

st.bar_chart(data=review_score_df,x="review_score",y="reviews", color="review_score")

st.header("B. Reviews by category")

reviews_category_sql = """select count(orv.review_id) as review_count, p.product_category_name as category
from order_reviews orv
join orders o on orv.order_id = o.order_id
join order_items oi on oi.order_id = o.order_id
join products p on p.product_id = oi.product_id
group by category
order by review_count;
"""
reviews_category_df = pd.read_sql_query(reviews_category_sql,connection)

st.bar_chart(data=reviews_category_df,x="category",y="review_count",color="category")


st.header("C. Rating vs delivery performance")

rating_delivery_performance_sql = """select orv.review_score,
   avg(date(order_delivered_customer_date) - date(order_estimated_delivery_date)) as delivery_days
from orders o
join order_reviews orv on orv.order_id = o.order_id
group by orv.review_score;
"""

rating_delivery_performance_df = pd.read_sql_query(rating_delivery_performance_sql,connection)

st.bar_chart(data=rating_delivery_performance_df,x="review_score",y="delivery_days",color="review_score")


connection.close()