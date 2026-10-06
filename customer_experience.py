from turtle import home

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

from streamlit_option_menu import option_menu

with st.sidebar:
    selected = option_menu("Main Menu", ["Home", "6. Customer Experience "], 
        icons=['house', 'gear'], menu_icon="cast", default_index=1)
if selected == "Home":
       st.write("Welcome")
if selected == "6. Customer Experience ":
       
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