with perf as (
  select * from product_performance order by revenue desc
), ranked as (
  select *,
    sum(revenue) over () as total_rev,
    sum(revenue) over (order by revenue desc rows between unbounded preceding and current row) / nullif(sum(revenue) over (),0) as cum_rev_pct
  from perf
)
select *,
  case when cum_rev_pct <= 0.80 then 'A'
       when cum_rev_pct <= 0.95 then 'B'
       else 'C' end as abc
from ranked
