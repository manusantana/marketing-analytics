with o as (
  select customer_id, date, net_revenue from stg_orders
), last_date as (
  select max(date) as max_date from o
), agg as (
  select customer_id,
         julianday((select max_date from last_date)) - julianday(max(date)) as recency_days,
         count(*) as frequency,
         sum(net_revenue) as monetary
  from o group by 1
)
select *,
  ntile(5) over (order by -recency_days) as R,
  ntile(5) over (order by frequency) as F,
  ntile(5) over (order by monetary) as M,
  (ntile(5) over (order by -recency_days)) + (ntile(5) over (order by frequency)) + (ntile(5) over (order by monetary)) as rfm_score
from agg
