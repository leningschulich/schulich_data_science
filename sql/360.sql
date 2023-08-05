WITH conversion_with_next AS (
    SELECT
        cd.customer_id AS customer_id,
        cd.first_name,
        cd.last_name,
        ft_con.conversion_date,
        ROW_NUMBER() OVER (PARTITION BY ft_con.fk_customer ORDER BY ft_con.conversion_date) AS recurrence,
        ft_con.conversion_type,
        ft_con.conversion_channel,
        LEAD(ft_con.conversion_date) OVER (PARTITION BY ft_con.fk_customer ORDER BY ft_con.conversion_date) AS next_conversion_date
    FROM fact_tables.conversions AS ft_con
    INNER JOIN dimensions.customer_dimension as cd on ft_con.fk_customer = cd.sk_customer
),

first_order AS (
    SELECT
        cd2.customer_id,
        ft_orders.order_id  AS first_order_id,
        CASE
            WHEN ft_orders.unit_price - ft_orders.discount < 0 THEN 0
            ELSE ft_orders.unit_price - ft_orders.discount END       AS first_order_total_paid,
        ft_orders.discount  AS first_order_discount,
        ft_orders.fk_order_date AS first_order_date,
        dd.year_week    AS first_order_week,
        ft_orders.fk_product    AS first_order_product,
        ROW_NUMBER() OVER (PARTITION BY ft_orders.fk_customer ORDER BY ft_orders.fk_order_date) AS rn
    FROM fact_tables.orders AS ft_orders
    INNER JOIN dimensions.date_dimension AS dd ON ft_orders.fk_order_date = dd.sk_date
    INNER JOIN dimensions.customer_dimension as cd2 on ft_orders.fk_customer = cd2.sk_customer
),

orders_with_week AS (
    SELECT
        cd2.customer_id AS customer_id,
        ft_orders.order_id,
        ft_orders.order_item_id,
        ft_orders.price_paid AS order_revenue,
        ft_orders.discount AS order_discount,
        dd.year_week AS order_week,
        ft_orders.fk_order_date AS order_date,
        ROW_NUMBER() OVER (PARTITION BY ft_orders.fk_customer ORDER BY ft_orders.fk_order_date) AS order_rank
    FROM fact_tables.orders AS ft_orders
    JOIN dimensions.date_dimension AS dd ON ft_orders.fk_order_date = dd.sk_date
    INNER JOIN dimensions.customer_dimension as cd2 on ft_orders.fk_customer = cd2.sk_customer
),

weekly_orders AS (
    SELECT
        ow.customer_id,
        ow.order_week,
        MIN(ow.order_date) AS week_start_date,
        SUM(ow.order_revenue) AS week_revenue,
        SUM(ow.order_discount) AS week_discounts,
        COUNT(ow.order_id) AS loyalty,
        SUM(COUNT(ow.order_id)) OVER (PARTITION BY ow.customer_id ORDER BY ow.order_week) AS cumulative_loyalty,
        SUM(SUM(ow.order_revenue)) OVER (PARTITION BY ow.customer_id ORDER BY ow.order_week) AS cumulative_revenue
    FROM orders_with_week AS ow
    WHERE ow.order_rank >= 1 -- only considering orders from the first order and onwards
    GROUP BY ow.customer_id, ow.order_week
)

SELECT
    cw.customer_id,
    cw.first_name,
    cw.last_name,
    cw.conversion_date,
    cw.recurrence,
    cw.conversion_type,
    cw.conversion_channel,
    cw.next_conversion_date,
    fo.first_order_date,
    fo.first_order_id,
    pd.product_name AS first_order_product,
    fo.first_order_total_paid,
    fo.first_order_discount,
    dd.year_week AS order_week,
    wo.week_start_date,
    wo.week_revenue,
    wo.week_discounts,
    wo.cumulative_revenue,
    SUM(wo.week_revenue) OVER (ORDER BY cw.customer_id ROWS UNBOUNDED PRECEDING) as cumulative_revenue_lifetime,
    wo.loyalty,
    wo.cumulative_loyalty
FROM conversion_with_next AS cw
LEFT JOIN first_order AS fo ON cw.customer_id = fo.customer_id AND fo.rn = 1
LEFT JOIN dimensions.date_dimension AS dd ON fo.first_order_date = dd.sk_date
LEFT JOIN dimensions.product_dimension AS pd ON fo.first_order_product = pd.sk_product
LEFT JOIN weekly_orders AS wo ON wo.customer_id = cw.customer_id
LEFT JOIN dimensions.customer_dimension AS c2 ON cw.customer_id = c2.sk_customer
ORDER BY customer_id, conversion_date;
