select
  o.product_id,
  sum(o.net_revenue) as revenue,
  sum(o.cogs) as cogs,
  sum(o.net_revenue) - sum(o.cogs) as gross_margin,
  (sum(o.net_revenue) - sum(o.cogs)) / nullif(sum(o.net_revenue),0) as margin_pct
from stg_orders o
group by 1
