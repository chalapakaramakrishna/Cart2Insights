"""
create database cart2insights;


create table customers(
customer_id varchar(50) primary key,
customer_unique_id varchar(50),
customer_zip_code_prefix varchar(50),
customer_city varchar(50),
customer_state varchar(50));

create table orders(
order_id varchar(50) primary key,
customer_id varchar(50),
order_status varchar(50),
order_purchase_timestamp timestamp,
order_delivered_customer_date timestamp,
order_estimated_delivery_date timestamp,
constraint fk_customer_id foreign key (customer_id) references customers (customer_id));

create table order_payments(
order_id varchar(50),
payment_sequential int,
payment_type varchar(50),
payment_installments int,
payment_value float,
constraint fk_order_id foreign key (order_id) references orders (order_id));


create table order_reviews(
review_id varchar(50),
order_id varchar(50),
review_score int,
review_comment_message varchar(200),
review_creation_date timestamp,
constraint fk_order_id foreign key (order_id) references orders (order_id));


create table product_category_translation(
product_category_name varchar(50) primary key,
product_category_name_english varchar(50));



create table products(
product_id varchar(50) primary key,
product_category_name varchar(50),
product_weight_g int,
product_length_cm int,
product_photos_qty int,
constraint fk_product_category_name foreign key (product_category_name) references product_category_translation (product_category_name));

create table sellers(
seller_id varchar(50) primary key,
seller_zip_code_prefix varchar(50),
seller_city varchar(50),
seller_state varchar(50));


create table order_items(
order_id varchar(50),
order_item_id int primary key,
product_id varchar(50),
seller_id varchar(50),
shipping_limit_date timestamp,
price float,
freight_value float,
constraint fk_order_id foreign key (order_id) references orders (order_id),
constraint fk_product_id foreign key (product_id) references products (product_id),
constraint fk_seller_id foreign key (seller_id) references sellers (seller_id));

create table geolocation(
geolocation_zip_code_prefix varchar(50) primary key,
geolocation_lat float,
geolocation_lng float,
geolocation_city varchar(50),
geolocation_state varchar(50));

select * from customers;

alter table orders 
add order_approved_at timestamp,
add order_delivered_carrier_date timestamp;

alter table products 
add product_name_lenght float,
add product_description_lenght float,
add product_height_cm float,
add product_width_cm float;


alter table order_reviews 
add review_comment_title varchar(50),
add review_answer_timestamp timestamp ;

alter table customers 
add 
constraint fk_customer_zip_code_prefix foreign key (customer_zip_code_prefix) references geolocation (geolocation_zip_code_prefix);


alter table sellers 
add 
constraint fk_seller_zip_code_prefix foreign key (seller_zip_code_prefix) references geolocation (geolocation_zip_code_prefix);


select * from customers;

select * from geolocation;

select * from order_items;

ALTER TABLE public.order_reviews
ALTER COLUMN review_comment_message TYPE TEXT;

select * from order_payments;
select * from orders;
select * from product_category_translation;
select * from products;
select * from sellers;
select * from order_reviews;


select * from order_payments;
select count(*) from order_payments;

--- Total order value

select sum(payment_value) from order_payments;

---Customer order count 

select customer_id, count(order_id)
from orders
group by customer_id
order by count(order_id) desc;

select payment_value from order_payments;
select price from order_items;

---Customer total spending

select c.customer_id, c.customer_unique_id, sum(oi.price) as total_spending
from customers c
left join orders o on c.customer_id = o.customer_id 
left join order_items oi  on o.order_id = oi.order_id 
group by c.customer_id
order by total_spending asc;

---Average order value 

select oi.order_id, avg(oi.price) 
from order_items oi
group by oi.order_id
order by avg(oi.price) asc;

---Seller revenue 

select oi.seller_id, sum(oi.price) as seller_revenue
from order_items oi
group by  oi.seller_id 
order by seller_revenue desc;

--- Seller order count 

select oi.seller_id, count(oi.order_id) as order_count
from order_items oi
group by oi.seller_id
order by order_count desc;

---Delivery days

---select order_purchase_timestamp, order_delivered_customer_date,
---datediff(order_delivered_customer_date,order_purchase_timestamp ) as delivery_days from orders;

SELECT 
    order_purchase_timestamp,
    order_delivered_customer_date,
    DATE(order_delivered_customer_date) - DATE(order_purchase_timestamp) AS delivery_days
FROM orders;

---Delivery delay

---select order_estimated_delivery_date, order_delivered_customer_date,
---datediff ( order_delivered_customer_date,order_estimated_delivery_date) as delivery_delay from orders;


select order_estimated_delivery_date, 
        order_delivered_customer_date,
        date(order_estimated_delivery_date)- date (order_delivered_customer_date) as delivery_delay 
from orders;

---Repeat customer indicator 

select * from products;

select * from order_items oi ;

--- 1. business overview

select sum (price) from order_items oi;

select count(distinct(order_id)) from orders o ; 

select count(distinct(customer_id)) from customers c;

select count(distinct(seller_id)) from sellers s ;

select avg(price) from order_items oi ;

select avg(review_score) from order_reviews ore ;





SELECT
    p.product_category_name,
    SUM(oi.price) AS revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY revenue DESC;


--- 2. Sales Analysis ---

--Monthly revenue trend

select 
      date_trunc('month', o.order_purchase_timestamp) as month,
      sum(oi.price) as monthlyrevenue
from orders o
join order_items oi
    on o.order_id = oi.order_id 
group by date_trunc('month', o.order_purchase_timestamp)
order by month desc;

--Revenue by category 

select 
      p.product_category_name as category,
      sum(price) as revenue
from order_items oi 
join products p
      on oi.product_id  = p.product_id 
group by category
order by revenue desc; 

--top selling Products

select 
      p.product_id as product , p.product_category_name, count(oi.order_item_id) as orderitems
from  order_items oi
join  products p
     on p.product_id = oi.product_id 
group by product
order by orderitems desc;
      

---sales by location

select 
      c.customer_state as state, sum(oi.price) as revenue, count((o.order_id)) as orders 
from  customers c
join orders o on c.customer_id = o.customer_id
join order_items oi on o.order_id = oi.order_id
group by state
order by revenue desc;


---- 3. Customer Analysis ---- 

--- customer distribution ---

select customer_state as state, count(distinct(customer_id)) as customers
from customers 
group by state
order by customers desc;

--- customer spending ---

select c.customer_id, count((o.order_id)) as items_purchased, sum(oi.price) as value
from customers c 
join orders o on c.customer_id = o.customer_id 
join order_items oi  on oi.order_id = o.order_id
group by c.customer_id 
order by value desc;


--- Top customers ----

select c.customer_id, c.customer_city, c.customer_state, count((o.order_id)) as total_orders, sum(price) as total_spending
from customers c 
join orders o on o.customer_id = c.customer_id
join order_items oi on oi.order_id = o.order_id 
group by c.customer_id
order by total_spending desc;

---- repeat Vs. New Customer

WITH customer_orders AS (
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
GROUP BY 1  -- Groups by the first column (customer_type) for cleaner code
ORDER BY customer_count DESC;


--- 4. Seller & Product Analysis ---

--- Top sellers ---

select s.seller_id, s.seller_city, s.seller_state, sum(oi.price) as revenue, count((oi.order_id)) as total_orders
from sellers s
join order_items oi on oi.seller_id = s.seller_id 
join orders o on oi.order_id = o.order_id
group by s.seller_id
order by revenue desc;


---Seller revenue---

select s.seller_id, count(distinct(o.order_id)) as total_orders, count(oi.order_item_id) as items_sold , sum(oi.price) as revenue from sellers s 
join order_items oi on oi.seller_id = s.seller_id
join  orders o on o.order_id = oi.order_id
group by s.seller_id 
order by revenue desc;

---Product/category performance---

select coalesce(p.product_id, p.product_category_name) as category, sum(oi.price) as revenue, count((o.order_id)) as total_itemssold, avg(oi.price) as average_price
from products p 
join order_items oi on oi.product_id = p.product_id 
join orders o on o.order_id = oi.order_id 
group by category 
order by revenue desc;

---Seller ratings ---

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


--- 5. Delivery Analysis ---

--- Average delivery time ---

select order_estimated_delivery_date, 
        order_delivered_customer_date,
        avg(date(order_delivered_customer_date)- date (order_estimated_delivery_date)) as delivery_days 
from orders
group by order_estimated_delivery_date,order_delivered_customer_date;

--- On-time vs delayed orders ---

select order_estimated_delivery_date, order_delivered_customer_date,
      date(order_delivered_customer_date)- date (order_estimated_delivery_date)as delivery_days,
case when date(order_delivered_customer_date)<= date(order_estimated_delivery_date) then 'On Time'
     else 'Delayed'
end as delivery_status
from orders;	

---Delivery performance by location ---

select c.customer_state as state,
count(order_id) as total_orders,
avg(date(order_delivered_customer_date)- date (order_estimated_delivery_date)) as avg_delivery_days,
case when date(order_delivered_customer_date)<= date(order_estimated_delivery_date) then 'On Time'
     else 'Delayed'
end as delivery_status
from customers c
join orders o on o.customer_id = c.customer_id
group by state,order_estimated_delivery_date,order_delivered_customer_date
order by avg_delivery_days;

---- Delivery delay vs review score -----

select o.order_id, orv.review_score,
   date(order_delivered_customer_date) - date(order_estimated_delivery_date) as delivery_days,
     case when date (order_delivered_customer_date) <= date (order_estimated_delivery_date) then 'On Time'
     else 'Delayed'
     end as delivery_status
from orders o
join order_reviews orv on orv.order_id = o.order_id;

--- 6. Customer Experience ---

--- Review score distribution ---

select oi.review_score,count(review_id) as reviews
from order_reviews oi
group by oi.review_score;


--- Reviews by category ---

select count(orv.review_id) as review_count, p.product_category_name as category
from order_reviews orv
join orders o on orv.order_id = o.order_id
join order_items oi on oi.order_id = o.order_id
join products p on p.product_id = oi.product_id
group by category
order by review_count;




--- Rating vs delivery performance ---

select orv.review_score,
   avg(date(order_delivered_customer_date) - date(order_estimated_delivery_date)) as delivery_days
from orders o
join order_reviews orv on orv.order_id = o.order_id
group by orv.review_score;




"""
