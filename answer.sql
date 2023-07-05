--Write a SQL query to identify the month(s)
-- of each year (2021 and 2022) with the lowest amount of orders for each type of Baguette in the dataset

WITH lowest_sale AS (
  SELECT
    bs.article,
    DATE_PART('year', bs.sale_datetime) AS year,
    DATE_PART('month', bs.sale_datetime) AS worst_month,
    SUM(bs.quantity) AS sales_volume,
    RANK() OVER (PARTITION BY bs.article, DATE_PART('year', bs.sale_datetime) ORDER BY SUM(bs.quantity)) AS rank
  FROM assignment01.bakery_sales AS bs
  WHERE DATE_PART('year', bs.sale_datetime) IN (2021, 2022)
   AND bs.article LIKE '%BAGUETTE%'
  GROUP BY bs.article, year, worst_month
)
SELECT article, year, worst_month, sales_volume
FROM lowest_sale
WHERE rank = 1
ORDER BY article, year, worst_month, sales_volume;

--2.Write a SQL query to calculate the bottom three (worst) performing products
-- (dense_rank = 1, 2, 3) with a non-zero unit prize in the entire dataset (use sales volume as your metric)
WITH bottom_three AS (
  SELECT
    article,
    SUM(quantity) AS sales_volume,
    DENSE_RANK() OVER (ORDER BY SUM(quantity)) AS DenseRank_bs
  FROM assignment01.bakery_sales
  WHERE unit_price <> 0
  GROUP BY article
)
SELECT article, sales_volume, DenseRank_bs
FROM bottom_three
WHERE DenseRank_bs <= 3
ORDER BY DenseRank_bs asc;

--3.Write a SQL query to calculate net revenue and number of items sold broken down by year and by quarter
--Hint: you can use EXTRACT(quarter FROM ...) or DATE_PART('quarter', ...)
SELECT
  DATE_PART('year', sale_datetime) AS year,
  DATE_PART('quarter', sale_datetime) AS quarter,
  SUM(unit_price * quantity) AS net_revenue,
  SUM(quantity) AS sales_volumes
FROM assignment01.bakery_sales
GROUP BY year, quarter
ORDER BY year, quarter;

--4.Write a query to identify the top 3 performing products for each year and month using revenue

WITH top_three AS (
  SELECT
    bs.article,
    EXTRACT('year' FROM bs.sale_datetime) AS sale_year,
    EXTRACT('month' FROM bs.sale_datetime) AS sale_month,
    SUM(bs.quantity * bs.unit_price) AS revenue,
    RANK() OVER (PARTITION BY EXTRACT('year' FROM bs.sale_datetime), EXTRACT('month' FROM bs.sale_datetime) ORDER BY SUM(bs.quantity * bs.unit_price) DESC) AS revenue_rank
  FROM assignment01.bakery_sales AS bs
  GROUP BY bs.article, sale_year, sale_month
)
SELECT *
FROM top_three
WHERE revenue_rank <= 3
ORDER BY sale_year, sale_month, revenue_rank;








