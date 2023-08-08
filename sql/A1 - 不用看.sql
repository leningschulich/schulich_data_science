1.Identify the items with the highest and lowest (non-zero) unit price?
2.Write a SQL query to report the second most sold item from the bakery table.
 If there is no second most sold item, the query should report NULL.
3.Write a SQL query to report the top 3 most sold items for every month in 2022 
 including their monthly sales.
4.Write a SQL query to report all the tickets with 5 or more articles in August 2022 
 including the number of articles in each ticket.
5.Write a SQL query to calculate the average sales per day in August 2022?
6.Write a SQL query to identify the day of the week with more sales?
7.What time of the day is the traditional Baguette more popular?
8.Write a SQL query to find the articles with the lowest sales in each month?
9.Write a query to calculate the percentage of sales for each item between 2022-01-01 and 2022-01-31
10.The order rate is computed by dividing the volume of a specific article divided by 
the total amount of items ordered in a specific date. Calculate the order rate for 
the Banette for every month during 2022.

1.--max_price=60,min_price=0.07
select
max(unit_price) as max_price,
min(unit_price) as min_price
from bakery_sales
where
unit_price <>0;

2.
SELECT article AS second_most_sold_item
FROM bakery_sales
GROUP BY article
ORDER BY sum(quantity) DESC
LIMIT 1 OFFSET 1;

3.--这道题重点在于datetime，article是有可能重复的但是date不会重复
WITH month_top_three as (
SELECT bs.article,
       EXTRACT('month' FROM bs.sale_datetime) AS sale_month,
       SUM(bs.quantity) as quantity_sold,
       RANK() over (PARTITION BY EXTRACT('month' FROM bs.sale_datetime)
                    ORDER BY SUM(bs.quantity) DESC) as rank
FROM assignment01.bakery_sales AS bs
WHERE EXTRACT('year' FROM bs.sale_datetime) = '2022'
GROUP BY bs.article, sale_month
ORDER BY sale_month DESC
)
SELECT *
FROM month_top_three
WHERE rank <= 3;

4.
select ticket_number,
count(article) as Aug_articles
from bakery_sales
where date_part('MONTH', sale_date) = 8
and date_part('YEAR', sale_date) = 2022
group by ticket_number
having count(article) >= 5;
alter table bakery_sales
add column sales integer;
--update bakery_sales
--set sales = quantity * unit_price;

5.
--ROUND(..., 2): This rounds the result to two decimal places.
select
round(sum(quantity * unit_price)/31,2) as August_avg
FROM
assignment01.bakery_sales
WHERE
DATE_PART('MONTH', sale_date) = 8
AND DATE_PART('YEAR', sale_date) = 2022;

6.
SELECT
EXTRACT(DOW FROM sale_date) AS day_of_week,
SUM(quantity * unit_price) AS total_sales
FROM bakery_sales
GROUP BY day_of_week
ORDER BY total_sales DESC;

7.
select
extract(hour from sale_time) as hour_of_day,
--count(*) 算有多少行
--count(*) as sales
sum(quantity) as popular
from bakery_sales
where article = 'TRADITIONAL BAGUETTE'
group by
hour_of_day
ORDER BY popular desc;

8.
with low_article_sale as(
SELECT bs.sale_date,
bs.article,
bs.quantity,
bs.unit_price,
RANK() OVER (PARTITION BY EXTRACT(MONTH FROM bs.sale_date) ORDER BY bs.quantity * bs.unit_price) as rank
FROM assignment01.bakery_sales as bs)

SELECT EXTRACT(MONTH FROM sale_date) as sale_month,
article,
quantity
from low_article_sale
WHERE rank = 1;

9.
select distinct(article) as product,
       (sum(quantity * unit_price)/(select sum(quantity*unit_price) from bakery_sales))*100 as revenue_percentage
from bakery_sales
where sale_date between '2022-01-01' and '2022-01-31'
group by article;


10.
SELECT
EXTRACT(MONTH FROM sale_date) AS month,
SUM(quantity) AS total_count,
SUM(CASE WHEN article = 'BANETTE' THEN quantity ELSE 0 END) AS banette_count,
CAST(CAST(SUM(CASE WHEN article = 'BANETTE' THEN quantity ELSE 0 END)
    AS decimal(18, 4)) * 100 / NULLIF(SUM(quantity), 0)
    AS decimal(18, 2)) AS order_rate
FROM
bakery_sales
WHERE
EXTRACT(YEAR FROM sale_date) = 2022
AND EXTRACT(MONTH FROM sale_date) BETWEEN 1 AND 12
GROUP BY
EXTRACT(MONTH FROM sale_date);


