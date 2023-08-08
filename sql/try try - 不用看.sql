with conversion_with_next as (
    SELECT
        cd.customer_id,
        cd.first_name,
        cd.last_name,
        co.conversion_date,
        row_number() over (partition by cd.sk_customer order by co.conversion_date) as recurrence,
        co.conversion_type,
        co.conversion_channel,
        LEAD(co.conversion_date) OVER (partition by cd.sk_customer order by co.conversion_date) as next_conversion_date
    FROM dimensions.customer_dimension as cd
    INNER JOIN fact_tables.conversions as co
    ON cd.sk_customer = co.fk_customer
),
first_order as(
    SELECT
        cd2.customer_id as customer_id,
        min(oo.fk_order_date) as first_order_date,
        dd.week as first_order_week,
        oo.order_id as first_order_id,
        pd.product_name as first_order_product,
        oo.price_paid as first_order_total_paid,
        oo.discount as first_order_discount
    FROM fact_tables.orders as oo
    INNER JOIN dimensions.date_dimension as dd
    ON dd.sk_date = oo.fk_order_date
    INNER JOIN dimensions.product_dimension as pd
    ON pd.sk_product = oo.fk_product
    INNER JOIN dimensions.customer_dimension as cd2 on oo.fk_customer = cd2.sk_customer
    GROUP BY dd.week, oo.order_id, pd.product_name, oo.price_paid, oo.discount,cd2.customer_id
),
orders_with_week AS (
    SELECT
        cd2.customer_id as customer_id,
        oo.order_id as order_id,
        oo.price_paid as order_revenue,
        oo.discount as order_discounts,
        dd.week as order_week,
        oo.fk_order_date as order_date,
        row_number() over (partition by oo.fk_customer order by oo.order_date) as order_rank
    FROM fact_tables.orders as oo
    INNER JOIN dimensions.date_dimension as dd
    ON dd.sk_date = oo.fk_order_date
    INNER JOIN dimensions.customer_dimension as cd2 on oo.fk_customer = cd2.sk_customer
),
weekly_orders AS (
    SELECT
        oww.customer_id as customer_id,
        sum(oww.order_revenue) as week_revenue,
        sum(oww.order_discounts) as week_discounts,
        sum(count(oww.order_id)) over(partition by oww.customer_id order by oww.order_week) as loyalty,
        sum(sum(oww.order_id)) over(partition by oww.customer_id order by oww.order_week) as cumulative_revenue
    FROM orders_with_week as oww
    WHERE oww.order_rank >=1
    GROUP BY oww.customer_id,oww.order_week
)
SELECT
    cwn.customer_id,
    cwn.first_name,
    cwn.last_name,
    cwn.conversion_date,
    cwn.recurrence,
    cwn.conversion_type,
    cwn.conversion_channel,
    cwn.next_conversion_date,
    fo.first_order_date,
    fo.first_order_id,
    fo.first_order_product,
    fo.first_order_week,
    fo.first_order_discount,
    fo.first_order_total_paid,
    oww2.order_week,
    oww2.order_date,
    wo.week_revenue,
    wo.week_discounts,
    wo.loyalty,
    wo.cumulative_revenue
FROM conversion_with_next as cwn
LEFT JOIN first_order AS fo ON cwn.customer_id = fo.customer_id
LEFT JOIN orders_with_week as oww2 ON oww2.customer_id = fo.customer_id
LEFT JOIN weekly_orders as wo ON wo.customer_id = oww2.customer_id