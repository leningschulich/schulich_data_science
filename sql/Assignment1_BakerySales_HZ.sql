--Identify the items with the highest and lowest (non-zero) unit price?
select *
       from assignment01.bakery_sales AS bs
where bs.unit_price = (select
                        Max(bs.unit_price)
                    from assignment01.bakery_sales AS bs)
union
select *
       from assignment01.bakery_sales AS bs
where bs.unit_price = (select
                        Min(bs.unit_price)
                    from assignment01.bakery_sales AS bs
                    where bs.unit_price <> 0);

--Write a SQL query to report the second most sold item from the bakery table. If there is no second most sold item, the query should report NULL.
select bs.article,
    sum(bs.quantity) AS Sum_quantity
from assignment01.bakery_sales AS bs
group by bs.article
order by Sum_quantity desc
limit 1 offset 1;

--Write a SQL query to report the top 3 most sold items for every month in 2022 including their monthly sales.
with Sold_2022 AS
(select bs.article,
       date_part('month', bs.sale_datetime) AS sale_month,
       sum(bs.quantity) AS Sum_quantity,
       sum(bs.quantity * bs.unit_price) AS Sum_revenue,
       row_number() OVER (PARTITION BY date_part('month', bs.sale_datetime) ORDER BY sum(bs.quantity) DESC) AS row_num
from assignment01.bakery_sales AS bs
where date_part('year', bs.sale_datetime) = 2022
group by bs.article,
         sale_month)
select
    article,
    sale_month,
    Sum_quantity,
    Sum_revenue
from Sold_2022
where row_num <=3
order by sale_month,
         Sum_quantity desc;

--Write a SQL query to report all the tickets with 5 or more articles in August 2022 including the number of articles in each ticket.
with ticket_articles as(
select bs.ticket_number,
       count( distinct bs.article) AS number_of_article
from assignment01.bakery_sales AS bs
where date_part('year', bs.sale_datetime) = 2022
and date_part('month', bs.sale_datetime) = 08
group by bs.ticket_number)
select ticket_number,
       number_of_article
from ticket_articles
where number_of_article >=5
order by number_of_article desc;

--Write a SQL query to calculate the average sales per day in August 2022?
select sum(bs.quantity * bs.unit_price)/31 AS revenue_per_day
from assignment01.bakery_sales AS bs
where date_part('year', bs.sale_datetime) = 2022
and date_part('month', bs.sale_datetime) = 08;

--Write a SQL query to identify the day of the week with more sales?
--Sunday's sales is the highest
select date_part('dow', bs.sale_datetime) AS sale_day_of_week,
       sum(bs.quantity * bs.unit_price) AS revenue
from assignment01.bakery_sales AS bs
group by sale_day_of_week
order by revenue desc;

--What time of the day is the traditional Baguette more popular?
--10~12am are more popular time
select bs.article,
       date_part('hour', bs.sale_datetime) AS sale_hour,
       sum(bs.quantity) AS Sum_quantity
from assignment01.bakery_sales AS bs
where bs.article = 'TRADITIONAL BAGUETTE'
group by bs.article,
         sale_hour
order by Sum_quantity desc;

--Write a SQL query to find the articles with the lowest sales in each month?
with article_sale_each_month AS(
    select date_part('month', bs.sale_datetime) AS sale_month,
       bs.article,
       sum(bs.quantity * bs.unit_price) AS revenue,
       row_number() OVER (PARTITION BY date_part('month', bs.sale_datetime) ORDER BY sum(bs.quantity * bs.unit_price) asc) AS row_num
from assignment01.bakery_sales AS bs
group by sale_month,
         bs.article)
select sale_month,
       article,
       revenue
from article_sale_each_month
where row_num = 1
order by sale_month,
         revenue asc;

--Write a query to calculate the percentage of sales for each item between 2022-01-01 and 2022-01-31
SELECT c.article,
       CASE WHEN b.total_revenue != 0
            THEN a.revenue / b.total_revenue * 100
            ELSE NULL
       END AS percent_sale
FROM (
    SELECT DISTINCT article
    FROM assignment01.bakery_sales
) c
LEFT JOIN (
    SELECT bs.article,
           SUM(bs.quantity * bs.unit_price) AS revenue
    FROM assignment01.bakery_sales AS bs
    WHERE bs.sale_date BETWEEN '2022-01-01' AND '2022-01-31'
    GROUP BY bs.article
) a
ON c.article = a.article
LEFT JOIN (
    SELECT SUM(bs.quantity * bs.unit_price) AS total_revenue
    FROM assignment01.bakery_sales AS bs
    WHERE bs.sale_date BETWEEN '2022-01-01' AND '2022-01-31'
) b
ON true;


--The order rate is computed by dividing the volume of a specific article divided by the total amount of items ordered in a specific date. Calculate the order rate for the Banette for every month during 2022.
select a.sale_month,
       a.banette_quantity/b.total_items_quantity AS order_rate
           from
(SELECT DATE_PART('month', bs.sale_datetime) AS sale_month,
       SUM(bs.quantity)::FLOAT as banette_quantity
FROM assignment01.bakery_sales AS bs
WHERE DATE_PART('year', bs.sale_datetime) = 2022
      AND bs.article ='BANETTE'
GROUP BY sale_month)a
left join
(SELECT DATE_PART('month', bs.sale_datetime) AS sale_month,
       SUM(bs.quantity)::FLOAT as total_items_quantity
FROM assignment01.bakery_sales AS bs
WHERE DATE_PART('year', bs.sale_datetime) = 2022
GROUP BY sale_month)b
on a.sale_month = b.sale_month;
