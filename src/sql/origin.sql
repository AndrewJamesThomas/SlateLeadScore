select
	o.[record], 
	o.[date] as [origin_date],
	(select top 1 [created] from [application] a where a.[person] = o.[record] order by [created]) as [conversion_date],
	case when o.[record] in (select [person] from [application]) then 1 else 0 end as [conversion]
from [origin] o
where o.[first] = 1
