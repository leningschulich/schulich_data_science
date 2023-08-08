--Queation 1 Identify the items with the highest and lowest (non-zero) unit price?
select article as item
from bakery_sales
where unit_price =(select max(unit_price) from bakery_sales) or unit_price =(select min(unit_price) from bakery_sales where unit_price != 0);

--Question 2 Write a SQL query to report the second most sold item from the bakery table. If there is no second most sold item, the query should report NULL.
select article as most_sold_item
from bakery_sales
group by article
order by sum(quantity) desc
limit 1 offset 1;

--Question 3 Write a SQL query to report the top 3 most sold items for every month in 2022 including their monthly sales.
Select *
    from (Select *,
                 rank()over(partition by bakery.Month order by revenue DESC)as item_rank
          from (select article as Item,
                               sum(quantity) as item_sold,
                               sum(quantity*unit_price) as revenue,
                               extract(month from sale_date) as Month
               from bakery_sales
               where extract(year from sale_date) = '2022'and bakery_sales.unit_price>=0 and quantity >=0
               group by article, extract(month from sale_date)
               order by Month, sum(quantity) desc) as bakery) as new_bakery
where item_rank <4;

--Question 4 Write a SQL query to report all the tickets with 5 or more articles in August 2022 including the number of articles in each ticket.
select ticket_number as ticket_more_than_5_articles,
        count(article) as number_of_article
from bakery_sales
where extract(year from sale_date) = 2022 and extract(month from sale_date) = 8
group by ticket_number
having count(article) >=5;

--Question 5 Write a SQL query to calculate the average sales per day in August 2022?
SELECT count(ticket_number) as total_ticket,
       sum(unit_price*quantity)/count(ticket_number) as avg_revenue_per_day,
        sale_date as date_in_2022
FROM bakery_sales
WHERE extract(month from sale_date) = 8 AND extract(year from sale_date) = 2022
Group by sale_date;

--Question 6 Write a SQL query to identify the day of the week with more sales?
SELECT extract(dow from sale_date),
       sum(unit_price*quantity)
from bakery_sales
group by extract(dow from sale_date)
order by sum(unit_price*quantity) desc
limit 1;

--Question 7 What time of the day is the traditional Baguette more popular?
select extract(hour from sale_time) as Time_of_Day,
       sum(quantity) as total_sales
from bakery_sales
where article = 'TRADITIONAL BAGUETTE'
group by Time_of_Day
order by sum(quantity) desc
limit 1;

--Question 8 Write a SQL query to find the articles with the lowest sales in each month?
select*
from(select *, rank()over(
        partition by new_bakery.year, new_bakery.Month
        order by total_sales asc) as lowest_sale
    from (select article,
            sum(unit_price * quantity) as total_sales,
            extract(year from sale_date) as year,
            extract(month from sale_date) as month
        from bakery_sales
    group by article, year, month
    order by year, month,total_sales asc) as new_bakery) as new_bakery_table
where lowest_sale < 2;

--Question 9 Write a query to calculate the percentage of sales for each item between 2022-01-01 and 2022-01-31
select distinct(article) as product,
       (sum(quantity * unit_price)/(select sum(quantity*unit_price) from bakery_sales))*100 as revenue_percentage
from bakery_sales
where sale_date between '2022-01-01' and '2022-01-31'
group by article

--Question 10 The order rate is computed by dividing the volume of a specific article divided by the total amount of
-- items ordered in a specific date. Calculate the order rate for the Banette for every month during 2022.
with new_bakery as (
    Select article,
       extract(month from sale_datetime) as month,
       sum(quantity)as total
    from bakery_sales
    where extract(year from sale_datetime)='2022'
    group by article, month
    order by month)
Select * , total/(select sum(total) from new_bakery)*100 as order_rate
from new_bakery
where Upper(article) like '%BANETTE%'









